/*
 * MIRA queued-writer worker for the Android/shared-client Personal lane.
 *
 * API-originated Google Sheets writes do not fire Apps Script edit triggers, so
 * clients append durable API-001 commands to a Commands tab and a time-driven
 * worker polls them. Every worker execution holds one ScriptLock while it
 * performs revision/idempotency preflight, canonical mutation, recovery and
 * exact readback.
 *
 * The Changes tab introduced by M2-M1-006 is an append-only read projection of
 * canonical Resources. It is transport evidence for reconnect, never canonical
 * state. Missing projection rows are reconstructed from exact current Resource
 * readback under the same ScriptLock.
 *
 * This is same-user Personal infrastructure. The command inbox and Changes
 * projection are transport, never canonical state. Cross-person permission
 * semantics remain blocked.
 */

const MIRA_COMMAND_MODE_KEY_ = 'mutation_mode';
const MIRA_DIRECT_MODE_ = 'direct_single_writer';
const MIRA_QUEUED_MODE_ = 'queued_writer';
const MIRA_COMMAND_HANDLER_ = 'miraProcessCommandQueue';
const MIRA_COMMAND_LIMIT_ = 20;
const MIRA_COMMAND_HEADERS_ = [
  'command_id',
  'subject_id',
  'data_class',
  'action',
  'api_major',
  'schema_version',
  'resource_id',
  'payload_json',
  'idempotency_key',
  'expected_revision',
  'submitted_at',
  'status',
  'result_json',
  'processed_at',
  'error_code',
  'error_message',
];
const MIRA_CHANGE_HEADERS_ = [
  'change_seq',
  'change_id',
  'data_class',
  'resource_id',
  'revision',
  'payload_json',
  'recorded_at',
  'source_command_id',
  'readback_verified',
];
const MIRA_IDEMPOTENCY_HEADERS_ = [
  'idempotency_key',
  'operation',
  'request_hash',
  'result_json',
  'created_at',
  'resource_ref',
];
const MIRA_RESOURCE_HEADERS_ = [
  'resource_type',
  'resource_id',
  'revision',
  'payload_json',
  'updated_at',
  'last_idempotency_key',
  'request_hash',
];
const MIRA_INTERNAL_CHANGE_TYPES_ = ['authority', 'authority_binding'];

function miraEnableQueuedWriter() {
  miraWorkspaceSchema_();
  const spreadsheet = miraSpreadsheet_();
  miraEnsureCommandsSheet_(spreadsheet);
  miraEnsureChangesSheet_(spreadsheet);
  // Trigger validation/creation happens before changing the mutation mode. If
  // trigger setup fails, direct single-writer behavior remains authoritative.
  miraEnsureCommandTrigger_();
  miraSetMetadataValue_(spreadsheet, MIRA_COMMAND_MODE_KEY_, MIRA_QUEUED_MODE_);
  SpreadsheetApp.flush();
  return {
    mutation_mode: MIRA_QUEUED_MODE_,
    worker: MIRA_COMMAND_HANDLER_,
    interval_minutes: 1,
  };
}

function miraProcessCommandQueue() {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const spreadsheet = miraSpreadsheet_();
    miraRequireQueuedMode_(spreadsheet);
    const sheet = miraRequireTable_(spreadsheet, 'Commands', MIRA_COMMAND_HEADERS_);
    miraEnsureChangesSheet_(spreadsheet);

    // Reconcile current canonical state before processing new commands. This
    // seeds pre-Android Resources and repairs a crash after canonical write but
    // before projection acknowledgement. Internal Authority rows are excluded
    // because they are infrastructure, not client-domain state.
    miraReconcileCurrentChanges_(spreadsheet);

    const rows = sheet.getDataRange().getValues();
    const handled = {};
    let processed = 0;

    for (let index = 1; index < rows.length && processed < MIRA_COMMAND_LIMIT_; index += 1) {
      const status = String(rows[index][11] || '').trim();
      if (status !== 'pending') continue;

      const rawCommandId = String(rows[index][0] || '').trim();
      const rawGroup = miraRawCommandGroup_(rows, rawCommandId);
      const pendingRows = rawGroup.filter(function (entry) {
        return String(entry.row[11] || '').trim() === 'pending';
      }).map(function (entry) {
        return entry.row_number;
      });

      if (rawCommandId && handled[rawCommandId]) continue;
      if (rawCommandId) handled[rawCommandId] = true;
      processed += 1;

      let command = null;
      try {
        command = miraParseQueuedCommand_(rows[index], index + 1);
        const group = miraValidateExactCommandGroup_(rawGroup, command);
        const priorTerminal = miraExactCommandTerminal_(group);
        if (priorTerminal && priorTerminal.status === 'failed') {
          pendingRows.forEach(function (rowNumber) {
            miraWriteCommandResult_(
              sheet,
              rowNumber,
              'failed',
              null,
              priorTerminal.error_code,
              priorTerminal.error_message,
            );
          });
          continue;
        }

        const result = miraExecuteQueuedCommand_(spreadsheet, command);
        pendingRows.forEach(function (rowNumber) {
          miraWriteCommandResult_(sheet, rowNumber, 'succeeded', result, '', '');
        });
      } catch (error) {
        const code = error && error.miraCode ? error.miraCode : 'internal_error';
        if (miraRetryableWorkerCode_(code)) {
          // Leave every duplicate physical delivery pending. A later run retries
          // one logical command using the same API-001 idempotency material.
          continue;
        }
        const targets = pendingRows.length ? pendingRows : [index + 1];
        targets.forEach(function (rowNumber) {
          miraWriteCommandResult_(
            sheet,
            rowNumber,
            'failed',
            null,
            code,
            String(error && error.message ? error.message : error),
          );
        });
      }
    }
    SpreadsheetApp.flush();
    return {processed: processed};
  } finally {
    SpreadsheetApp.flush();
    lock.releaseLock();
  }
}

function miraExecuteQueuedCommand_(spreadsheet, command) {
  if (command.action !== 'upsert') {
    throw miraError_('validation_error', 'queued Workspace worker supports upsert only');
  }
  if (command.api_major !== MIRA_API_MAJOR_ || command.schema_version !== MIRA_API_SCHEMA_) {
    throw miraError_(
      'compatibility_error',
      'command API/schema version is incompatible with this service',
    );
  }

  const schema = miraWorkspaceSchema_();
  if (schema.resource_types.indexOf(command.data_class) === -1) {
    throw miraError_('validation_error', 'unknown resource type: ' + command.data_class);
  }

  const parsedResources = miraResourceRows_();
  const authority = miraResolveWorkerAuthority_(parsedResources, command.data_class, schema.schema_version);
  if (command.subject_id !== authority.owner_id) {
    throw miraError_('authorization_error', 'same-user command subject does not match authority owner');
  }

  const fingerprint = miraQueuedUpsertFingerprint_(command);
  const idempotencyRows = miraRawIdempotencyRows_(spreadsheet);
  const matchingIdempotency = idempotencyRows.filter(function (row) {
    return row.idempotency_key === command.idempotency_key;
  });
  if (matchingIdempotency.length > 1) {
    throw miraError_('conflict', 'duplicate persisted idempotency key');
  }
  if (matchingIdempotency.length === 1) {
    const stored = matchingIdempotency[0];
    if (stored.operation !== 'upsert' || stored.request_hash !== fingerprint) {
      throw miraError_('conflict', 'idempotency key was already used for different material input');
    }
    const replay = miraParseResultJson_(stored.result_json);
    miraVerifyQueuedReadback_(spreadsheet, command, fingerprint, replay);
    miraEnsureVerifiedChange_(spreadsheet, replay.record, command.command_id);
    return miraCommandResult_(command, authority.authority_id, replay.record, true);
  }

  const rawResources = miraRawResourceRows_(spreadsheet);
  const matches = rawResources.filter(function (row) {
    return row.resource_type === command.data_class && row.resource_id === command.resource_id;
  });
  if (matches.length > 1) {
    throw miraError_('conflict', 'duplicate persisted resource identity');
  }
  const current = matches.length ? matches[0] : null;

  // Recovery path: a previous execution can die after the resource write but
  // before appending its idempotency acknowledgement. The resource row itself
  // carries the key/hash, so the retry can prove the exact mutation landed,
  // reconstruct the missing idempotency row, and converge without revision 3.
  if (current && current.last_idempotency_key === command.idempotency_key) {
    if (current.request_hash !== fingerprint) {
      throw miraError_('conflict', 'resource records the idempotency key with a different request hash');
    }
    if (
      current.revision !== command.expected_revision + 1 ||
      miraCanonicalJson_(current.payload) !== miraCanonicalJson_(command.payload)
    ) {
      throw miraError_('readback_error', 'partial-write recovery material does not match command');
    }
    const recovered = miraUpsertResult_(current.resource_type, current.resource_id, current.payload, current.revision);
    miraAppendIdempotency_(spreadsheet, command, fingerprint, recovered);
    SpreadsheetApp.flush();
    miraVerifyQueuedReadback_(spreadsheet, command, fingerprint, recovered);
    miraEnsureVerifiedChange_(spreadsheet, recovered.record, command.command_id);
    return miraCommandResult_(command, authority.authority_id, recovered.record, true);
  }

  const currentRevision = current ? current.revision : 0;
  if (command.expected_revision !== currentRevision) {
    throw miraError_(
      'conflict',
      'expected revision ' + command.expected_revision + ', current revision is ' + currentRevision,
    );
  }

  const revision = currentRevision + 1;
  const now = miraNow_();
  const result = miraUpsertResult_(
    command.data_class,
    command.resource_id,
    command.payload,
    revision,
  );
  miraWriteCanonicalResource_(
    spreadsheet,
    current ? current.row_number : null,
    [
      command.data_class,
      command.resource_id,
      revision,
      miraCanonicalJson_(command.payload),
      now,
      command.idempotency_key,
      fingerprint,
    ],
  );
  SpreadsheetApp.flush();

  // Deliberately separate from the resource write. Recovery above makes a
  // crash at this exact seam safe without requiring a second infrastructure
  // service or pretending SpreadsheetApp offers a cross-tab transaction.
  miraAppendIdempotency_(spreadsheet, command, fingerprint, result, now);
  SpreadsheetApp.flush();
  miraVerifyQueuedReadback_(spreadsheet, command, fingerprint, result);
  miraEnsureVerifiedChange_(spreadsheet, result.record, command.command_id);
  return miraCommandResult_(command, authority.authority_id, result.record, false);
}

function miraParseQueuedCommand_(row, rowNumber) {
  const commandId = miraId_(String(row[0] || ''), 'command_id');
  const subjectId = miraId_(String(row[1] || ''), 'subject_id');
  const dataClass = miraDataClass_(String(row[2] || ''));
  const action = miraToken_(String(row[3] || ''), 'action');
  const apiMajor = Number(row[4]);
  const schemaVersion = miraToken_(String(row[5] || ''), 'schema_version');
  const resourceId = miraId_(String(row[6] || ''), 'resource_id');
  let payload;
  try {
    payload = JSON.parse(String(row[7] || ''));
  } catch (error) {
    throw miraError_('validation_error', 'queued payload_json is invalid');
  }
  miraRequireObject_(payload, 'queued payload');
  const idempotencyKey = miraId_(String(row[8] || ''), 'idempotency_key');
  const expectedRevision = Number(row[9]);
  if (!Number.isInteger(expectedRevision) || expectedRevision < 0) {
    throw miraError_('validation_error', 'expected_revision must be a non-negative integer');
  }
  if (!Number.isInteger(apiMajor) || apiMajor < 1) {
    throw miraError_('validation_error', 'api_major must be a positive integer');
  }
  return {
    row_number: rowNumber,
    command_id: commandId,
    subject_id: subjectId,
    data_class: dataClass,
    action: action,
    api_major: apiMajor,
    schema_version: schemaVersion,
    resource_id: resourceId,
    payload: payload,
    idempotency_key: idempotencyKey,
    expected_revision: expectedRevision,
  };
}

function miraRawCommandGroup_(rows, commandId) {
  if (!commandId) return [];
  const group = [];
  for (let index = 1; index < rows.length; index += 1) {
    if (String(rows[index][0] || '').trim() === commandId) {
      group.push({row_number: index + 1, row: rows[index]});
    }
  }
  return group;
}

function miraValidateExactCommandGroup_(rawGroup, command) {
  const expected = miraCommandMaterial_(command);
  const parsed = [];
  rawGroup.forEach(function (entry) {
    const candidate = miraParseQueuedCommand_(entry.row, entry.row_number);
    if (miraCommandMaterial_(candidate) !== expected) {
      throw miraError_('conflict', 'duplicate command_id has different command material');
    }
    parsed.push({
      row_number: entry.row_number,
      row: entry.row,
      command: candidate,
    });
  });
  return parsed;
}

function miraCommandMaterial_(command) {
  return miraCanonicalJson_({
    action: command.action,
    api_major: command.api_major,
    command_id: command.command_id,
    data_class: command.data_class,
    expected_revision: command.expected_revision,
    idempotency_key: command.idempotency_key,
    payload: command.payload,
    resource_id: command.resource_id,
    schema_version: command.schema_version,
    subject_id: command.subject_id,
  });
}

function miraExactCommandTerminal_(group) {
  let terminal = null;
  group.forEach(function (entry) {
    const status = String(entry.row[11] || '').trim();
    if (status !== 'succeeded' && status !== 'failed') return;
    const candidate = {
      status: status,
      result_json: String(entry.row[12] || ''),
      error_code: String(entry.row[14] || '').trim(),
      error_message: String(entry.row[15] || '').trim(),
    };
    if (!terminal) {
      terminal = candidate;
      return;
    }
    if (miraCanonicalJson_(terminal) !== miraCanonicalJson_(candidate)) {
      throw miraError_('conflict', 'duplicate command rows have contradictory terminal state');
    }
  });
  return terminal;
}

function miraResolveWorkerAuthority_(resources, dataClass, schemaVersion) {
  const bindings = resources.filter(function (record) {
    return record.resource_type === 'authority_binding' &&
      record.payload && record.payload.data_class === dataClass;
  });
  if (bindings.length !== 1) {
    throw miraError_('authority_unavailable', 'expected exactly one authority binding');
  }
  const authorityId = miraId_(bindings[0].payload.authority_id, 'authority_id');
  const authorities = resources.filter(function (record) {
    return record.resource_type === 'authority' && record.resource_id === authorityId;
  });
  if (authorities.length !== 1) {
    throw miraError_('authority_unavailable', 'canonical authority record is missing or duplicated');
  }
  const payload = authorities[0].payload || {};
  if (
    payload.enabled !== true ||
    payload.verified !== true ||
    payload.adapter_key !== 'google-sheets' ||
    payload.schema_version !== schemaVersion
  ) {
    throw miraError_('authority_unavailable', 'canonical Google Sheets authority is not ready');
  }
  return {
    authority_id: authorityId,
    owner_id: miraId_(payload.owner_id, 'owner_id'),
  };
}

function miraQueuedUpsertFingerprint_(command) {
  const material = {
    expected_revision: command.expected_revision,
    operation: 'upsert',
    payload: command.payload,
    resource_id: command.resource_id,
    resource_type: command.data_class,
  };
  return miraSha256_(miraCanonicalJson_(material));
}

function miraRawResourceRows_(spreadsheet) {
  const sheet = miraRequireTable_(spreadsheet, 'Resources', MIRA_RESOURCE_HEADERS_);
  const rows = sheet.getDataRange().getValues();
  const parsed = [];
  for (let index = 1; index < rows.length; index += 1) {
    const row = rows[index];
    if (!String(row[0] || '').trim() && !String(row[1] || '').trim()) continue;
    let payload;
    try {
      payload = JSON.parse(String(row[3] || ''));
    } catch (error) {
      throw miraError_('validation_error', 'persisted resource payload_json is invalid');
    }
    miraRequireObject_(payload, 'persisted resource payload');
    const revision = Number(row[2]);
    if (!Number.isInteger(revision) || revision < 1) {
      throw miraError_('validation_error', 'persisted resource revision is invalid');
    }
    parsed.push({
      row_number: index + 1,
      resource_type: miraDataClass_(String(row[0] || '').trim()),
      resource_id: miraId_(String(row[1] || '').trim(), 'resource_id'),
      revision: revision,
      payload: payload,
      last_idempotency_key: String(row[5] || '').trim(),
      request_hash: String(row[6] || '').trim(),
    });
  }
  return parsed;
}

function miraRawIdempotencyRows_(spreadsheet) {
  const sheet = miraRequireTable_(spreadsheet, 'Idempotency', MIRA_IDEMPOTENCY_HEADERS_);
  const rows = sheet.getDataRange().getValues();
  const parsed = [];
  for (let index = 1; index < rows.length; index += 1) {
    const row = rows[index];
    if (!String(row[0] || '').trim()) continue;
    parsed.push({
      row_number: index + 1,
      idempotency_key: miraId_(String(row[0] || '').trim(), 'idempotency_key'),
      operation: miraToken_(String(row[1] || '').trim(), 'operation'),
      request_hash: miraToken_(String(row[2] || '').trim(), 'request_hash'),
      result_json: String(row[3] || ''),
      resource_ref: String(row[5] || '').trim(),
    });
  }
  return parsed;
}

function miraWriteCanonicalResource_(spreadsheet, rowNumber, values) {
  const sheet = miraRequireTable_(spreadsheet, 'Resources', MIRA_RESOURCE_HEADERS_);
  const targetRow = rowNumber || sheet.getLastRow() + 1;
  sheet.getRange(targetRow, 1, 1, MIRA_RESOURCE_HEADERS_.length).setValues([values]);
}

function miraAppendIdempotency_(spreadsheet, command, fingerprint, result, nowValue) {
  const sheet = miraRequireTable_(spreadsheet, 'Idempotency', MIRA_IDEMPOTENCY_HEADERS_);
  const now = nowValue || miraNow_();
  sheet.getRange(sheet.getLastRow() + 1, 1, 1, MIRA_IDEMPOTENCY_HEADERS_.length).setValues([[
    command.idempotency_key,
    'upsert',
    fingerprint,
    miraCanonicalJson_(result),
    now,
    command.data_class + '/' + command.resource_id,
  ]]);
}

function miraVerifyQueuedReadback_(spreadsheet, command, fingerprint, result) {
  const resources = miraRawResourceRows_(spreadsheet).filter(function (row) {
    return row.resource_type === command.data_class && row.resource_id === command.resource_id;
  });
  if (resources.length !== 1) {
    throw miraError_('readback_error', 'canonical resource readback is missing or duplicated');
  }
  const expected = result.record;
  const actual = resources[0];
  if (
    actual.revision !== expected.revision ||
    actual.last_idempotency_key !== command.idempotency_key ||
    actual.request_hash !== fingerprint ||
    miraCanonicalJson_(actual.payload) !== miraCanonicalJson_(expected.payload)
  ) {
    throw miraError_('readback_error', 'canonical resource readback does not match command result');
  }

  const idempotency = miraRawIdempotencyRows_(spreadsheet).filter(function (row) {
    return row.idempotency_key === command.idempotency_key;
  });
  if (idempotency.length !== 1) {
    throw miraError_('readback_error', 'idempotency readback is missing or duplicated');
  }
  if (
    idempotency[0].operation !== 'upsert' ||
    idempotency[0].request_hash !== fingerprint ||
    idempotency[0].resource_ref !== command.data_class + '/' + command.resource_id ||
    miraCanonicalJson_(miraParseResultJson_(idempotency[0].result_json)) !== miraCanonicalJson_(result)
  ) {
    throw miraError_('readback_error', 'idempotency readback material does not match command');
  }
}

function miraReconcileCurrentChanges_(spreadsheet) {
  const resources = miraRawResourceRows_(spreadsheet)
    .filter(function (row) {
      return MIRA_INTERNAL_CHANGE_TYPES_.indexOf(row.resource_type) === -1;
    })
    .sort(function (left, right) {
      const leftKey = left.resource_type + '\u0000' + left.resource_id;
      const rightKey = right.resource_type + '\u0000' + right.resource_id;
      return leftKey < rightKey ? -1 : leftKey > rightKey ? 1 : 0;
    });
  resources.forEach(function (resource) {
    miraEnsureVerifiedChange_(spreadsheet, {
      resource_type: resource.resource_type,
      resource_id: resource.resource_id,
      revision: resource.revision,
      payload: resource.payload,
    }, '');
  });
}

function miraEnsureVerifiedChange_(spreadsheet, record, sourceCommandId) {
  const resourceType = miraDataClass_(String(record.resource_type || ''));
  const resourceId = miraId_(String(record.resource_id || ''), 'resource_id');
  const revision = Number(record.revision);
  if (!Number.isInteger(revision) || revision < 1) {
    throw miraError_('readback_error', 'change projection revision is invalid');
  }
  miraRequireObject_(record.payload, 'change projection payload');

  // Freshly re-read the canonical source before asserting verified projection.
  const canonical = miraRawResourceRows_(spreadsheet).filter(function (row) {
    return row.resource_type === resourceType && row.resource_id === resourceId;
  });
  if (canonical.length !== 1) {
    throw miraError_('readback_error', 'change projection source is missing or duplicated');
  }
  if (
    canonical[0].revision !== revision ||
    miraCanonicalJson_(canonical[0].payload) !== miraCanonicalJson_(record.payload)
  ) {
    throw miraError_('readback_error', 'change projection source does not match canonical readback');
  }

  const material = {
    data_class: resourceType,
    payload: record.payload,
    resource_id: resourceId,
    revision: revision,
  };
  const changeId = miraSha256_(miraCanonicalJson_(material));
  const sheet = miraEnsureChangesSheet_(spreadsheet);
  const rows = sheet.getDataRange().getValues();
  let lastSequence = 0;
  let existing = null;

  for (let index = 1; index < rows.length; index += 1) {
    const row = rows[index];
    if (!String(row[0] || '').trim()) continue;
    const sequence = Number(row[0]);
    if (!Number.isInteger(sequence) || sequence !== lastSequence + 1) {
      throw miraError_('readback_error', 'Changes sequence is not contiguous');
    }
    lastSequence = sequence;
    const rowClass = miraDataClass_(String(row[2] || '').trim());
    const rowId = miraId_(String(row[3] || '').trim(), 'resource_id');
    const rowRevision = Number(row[4]);
    if (!Number.isInteger(rowRevision) || rowRevision < 1) {
      throw miraError_('readback_error', 'persisted change revision is invalid');
    }
    if (rowClass === resourceType && rowId === resourceId && rowRevision === revision) {
      if (existing) {
        throw miraError_('readback_error', 'duplicate change projection identity');
      }
      existing = row;
    }
  }

  if (existing) {
    let existingPayload;
    try {
      existingPayload = JSON.parse(String(existing[5] || ''));
    } catch (error) {
      throw miraError_('readback_error', 'persisted change payload_json is invalid');
    }
    if (
      String(existing[1] || '').trim() !== changeId ||
      miraCanonicalJson_(existingPayload) !== miraCanonicalJson_(record.payload) ||
      existing[8] !== true
    ) {
      throw miraError_('readback_error', 'same canonical revision has contradictory change material');
    }
    return {change_seq: Number(existing[0]), change_id: changeId, replay: true};
  }

  const nextSequence = lastSequence + 1;
  const now = miraNow_();
  sheet.getRange(sheet.getLastRow() + 1, 1, 1, MIRA_CHANGE_HEADERS_.length).setValues([[
    nextSequence,
    changeId,
    resourceType,
    resourceId,
    revision,
    miraCanonicalJson_(record.payload),
    now,
    sourceCommandId || '',
    true,
  ]]);
  SpreadsheetApp.flush();

  // Exact projection readback. A crash before this point leaves either no row
  // or a complete row; the next retry revalidates exact material and converges.
  const verifyRows = sheet.getDataRange().getValues().filter(function (row, index) {
    return index > 0 && Number(row[0]) === nextSequence;
  });
  if (verifyRows.length !== 1) {
    throw miraError_('readback_error', 'new change projection readback is missing or duplicated');
  }
  const verify = verifyRows[0];
  let verifyPayload;
  try {
    verifyPayload = JSON.parse(String(verify[5] || ''));
  } catch (error) {
    throw miraError_('readback_error', 'new change projection payload is invalid');
  }
  if (
    String(verify[1] || '').trim() !== changeId ||
    String(verify[2] || '').trim() !== resourceType ||
    String(verify[3] || '').trim() !== resourceId ||
    Number(verify[4]) !== revision ||
    miraCanonicalJson_(verifyPayload) !== miraCanonicalJson_(record.payload) ||
    verify[8] !== true
  ) {
    throw miraError_('readback_error', 'new change projection readback does not match canonical state');
  }
  return {change_seq: nextSequence, change_id: changeId, replay: false};
}

function miraWriteCommandResult_(sheet, rowNumber, status, result, errorCode, errorMessage) {
  sheet.getRange(rowNumber, 12, 1, 5).setValues([[
    status,
    result ? miraCanonicalJson_(result) : '',
    miraNow_(),
    errorCode || '',
    errorMessage || '',
  ]]);
}

function miraUpsertResult_(resourceType, resourceId, payload, revision) {
  return {
    kind: 'upsert',
    record: {
      payload: JSON.parse(miraCanonicalJson_(payload)),
      resource_id: resourceId,
      resource_type: resourceType,
      revision: revision,
    },
  };
}

function miraCommandResult_(command, authorityId, record, replay) {
  return {
    command_id: command.command_id,
    authority_id: authorityId,
    record: record,
    event: null,
    idempotent_replay: replay === true,
    readback_verified: true,
  };
}

function miraParseResultJson_(value) {
  let result;
  try {
    result = JSON.parse(String(value || ''));
  } catch (error) {
    throw miraError_('conflict', 'persisted idempotency result is invalid JSON');
  }
  miraRequireObject_(result, 'persisted idempotency result');
  if (result.kind !== 'upsert' || !result.record) {
    throw miraError_('conflict', 'persisted idempotency result has wrong operation');
  }
  return result;
}

function miraEnsureCommandsSheet_(spreadsheet) {
  let sheet = spreadsheet.getSheetByName('Commands');
  if (!sheet) {
    sheet = spreadsheet.insertSheet('Commands');
    sheet.getRange(1, 1, 1, MIRA_COMMAND_HEADERS_.length).setValues([MIRA_COMMAND_HEADERS_]);
    return sheet;
  }
  miraRequireTable_(spreadsheet, 'Commands', MIRA_COMMAND_HEADERS_);
  return sheet;
}

function miraEnsureChangesSheet_(spreadsheet) {
  let sheet = spreadsheet.getSheetByName('Changes');
  if (!sheet) {
    sheet = spreadsheet.insertSheet('Changes');
    sheet.getRange(1, 1, 1, MIRA_CHANGE_HEADERS_.length).setValues([MIRA_CHANGE_HEADERS_]);
    return sheet;
  }
  miraRequireTable_(spreadsheet, 'Changes', MIRA_CHANGE_HEADERS_);
  return sheet;
}

function miraRequireTable_(spreadsheet, name, headers) {
  const sheet = spreadsheet.getSheetByName(name);
  if (!sheet) {
    throw miraError_('authority_unavailable', 'missing required sheet tab: ' + name);
  }
  const rows = sheet.getDataRange().getValues();
  if (!rows.length) {
    throw miraError_('validation_error', name + ' tab is empty');
  }
  headers.forEach(function (header, index) {
    if (String(rows[0][index] || '') !== header) {
      throw miraError_('validation_error', name + ' headers are invalid');
    }
  });
  return sheet;
}

function miraSetMetadataValue_(spreadsheet, key, value) {
  const sheet = spreadsheet.getSheetByName('Metadata');
  if (!sheet) {
    throw miraError_('authority_unavailable', 'missing required sheet tab: Metadata');
  }
  const rows = sheet.getDataRange().getValues();
  let found = null;
  for (let index = 1; index < rows.length; index += 1) {
    if (String(rows[index][0] || '').trim() === key) {
      if (found !== null) {
        throw miraError_('conflict', 'duplicate Metadata key: ' + key);
      }
      found = index + 1;
    }
  }
  const rowNumber = found || sheet.getLastRow() + 1;
  sheet.getRange(rowNumber, 1, 1, 2).setValues([[key, value]]);
}

function miraRequireQueuedMode_(spreadsheet) {
  const sheet = spreadsheet.getSheetByName('Metadata');
  if (!sheet) {
    throw miraError_('authority_unavailable', 'missing required sheet tab: Metadata');
  }
  const rows = sheet.getDataRange().getValues();
  const matches = rows.slice(1).filter(function (row) {
    return String(row[0] || '').trim() === MIRA_COMMAND_MODE_KEY_;
  });
  if (matches.length !== 1 || String(matches[0][1] || '').trim() !== MIRA_QUEUED_MODE_) {
    throw miraError_('queued_writer_not_enabled', 'Workspace queued-writer mode is not enabled');
  }
}

function miraEnsureCommandTrigger_() {
  const matches = ScriptApp.getProjectTriggers().filter(function (trigger) {
    return trigger.getHandlerFunction() === MIRA_COMMAND_HANDLER_;
  });
  if (matches.length > 1) {
    throw miraError_('conflict', 'duplicate MIRA command-worker triggers exist');
  }
  if (matches.length === 0) {
    ScriptApp
      .newTrigger(MIRA_COMMAND_HANDLER_)
      .timeBased()
      .everyMinutes(1)
      .create();
  }
}

function miraRetryableWorkerCode_(code) {
  return code === 'authority_unavailable' ||
    code === 'readback_error' ||
    code === 'internal_error';
}

function miraCanonicalJson_(value) {
  return JSON.stringify(miraCanonicalize_(value));
}

function miraCanonicalize_(value) {
  if (Array.isArray(value)) {
    return value.map(miraCanonicalize_);
  }
  if (value && typeof value === 'object') {
    const result = {};
    Object.keys(value).sort().forEach(function (key) {
      result[key] = miraCanonicalize_(value[key]);
    });
    return result;
  }
  return value;
}

function miraSha256_(text) {
  const digest = Utilities.computeDigest(
    Utilities.DigestAlgorithm.SHA_256,
    text,
    Utilities.Charset.UTF_8,
  );
  return digest.map(function (value) {
    const byte = value < 0 ? value + 256 : value;
    return ('0' + byte.toString(16)).slice(-2);
  }).join('');
}

function miraNow_() {
  return new Date().toISOString();
}
