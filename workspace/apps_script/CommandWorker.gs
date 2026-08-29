/*
 * MIRA queued-writer worker for the Android/shared-client Personal lane.
 *
 * API-originated Google Sheets writes do not fire Apps Script edit triggers, so
 * clients append durable API-001 commands to a Commands tab and a time-driven
 * worker polls them.  Every worker execution holds one ScriptLock while it
 * performs revision/idempotency preflight, canonical mutation, recovery and
 * exact readback.
 *
 * This is same-user Personal infrastructure.  The command inbox is transport,
 * never canonical state.  Cross-person permission semantics remain blocked.
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

function miraEnableQueuedWriter() {
  miraWorkspaceSchema_();
  const spreadsheet = miraSpreadsheet_();
  miraEnsureCommandsSheet_(spreadsheet);
  miraSetMetadataValue_(spreadsheet, MIRA_COMMAND_MODE_KEY_, MIRA_QUEUED_MODE_);
  miraEnsureCommandTrigger_();
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
    const rows = sheet.getDataRange().getValues();
    let processed = 0;

    for (let index = 1; index < rows.length && processed < MIRA_COMMAND_LIMIT_; index += 1) {
      const status = String(rows[index][11] || '').trim();
      if (status !== 'pending') continue;
      const rowNumber = index + 1;
      const command = miraParseQueuedCommand_(rows[index], rowNumber);
      processed += 1;

      try {
        const result = miraExecuteQueuedCommand_(spreadsheet, command);
        miraWriteCommandResult_(sheet, rowNumber, 'succeeded', result, '', '');
      } catch (error) {
        const code = error && error.miraCode ? error.miraCode : 'internal_error';
        if (miraRetryableWorkerCode_(code)) {
          // Leave the durable command pending. A later run retries the same
          // API-001 material and canonical idempotency key.
          continue;
        }
        miraWriteCommandResult_(
          sheet,
          rowNumber,
          'failed',
          null,
          code,
          String(error && error.message ? error.message : error),
        );
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
