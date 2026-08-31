/*
 * MIRA Google Workspace first-run runtime.
 *
 * First bounded slice: initialize a copied Sheet, expose health/schema, and
 * perform canonical read queries through persisted Authority state. Writes and
 * external client authentication are intentionally not implemented in this
 * slice; they remain fail-closed until the next packet checkpoint.
 */

const MIRA_SPREADSHEET_PROPERTY_ = 'MIRA_SPREADSHEET_ID';
const MIRA_API_MAJOR_ = 1;
const MIRA_API_SCHEMA_ = 'mira-api-1';
const MIRA_STORE_CONTRACT_ = 'STORE-001';
const MIRA_WRITER_MODEL_ = 'single_writer';
const MIRA_ID_RE_ = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/;
const MIRA_CLASS_RE_ = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,95}$/;

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('MIRA')
    .addItem('Initialize this copy', 'miraInitializeCopy')
    .addItem('Enable Calendar', 'miraEnableGoogleCalendar')
    .addToUi();
}

function miraInitializeCopy() {
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  if (!spreadsheet) {
    throw new Error('MIRA initialization requires the copied Sheet to be open.');
  }
  PropertiesService.getScriptProperties().setProperty(
    MIRA_SPREADSHEET_PROPERTY_,
    spreadsheet.getId(),
  );
  SpreadsheetApp.getUi().alert(
    'MIRA initialized',
    'This copy is now bound to its own MIRA spreadsheet state.',
    SpreadsheetApp.getUi().ButtonSet.OK,
  );
}

function miraEnableGoogleCalendar() {
  const result = miraEnsureGoogleCalendar_();
  const message = result.created
    ? 'MIRA created a dedicated Google Calendar for MIRA-managed events.'
    : result.recovered
      ? 'MIRA recovered its existing dedicated Google Calendar and is ready to use it.'
      : 'MIRA Calendar is already enabled and ready.';
  SpreadsheetApp.getUi().alert(
    'MIRA Calendar enabled',
    message,
    SpreadsheetApp.getUi().ButtonSet.OK,
  );
}

function doGet(e) {
  return miraHandle_(function () {
    const path = miraPath_(e);
    if (path === '/v1/health') {
      miraWorkspaceSchema_();
      return {service: 'mira', status: 'ok'};
    }
    if (path === '/v1/schema') {
      return miraWorkspaceSchema_();
    }
    throw miraError_('route_not_found', 'route not found');
  });
}

function doPost(e) {
  return miraHandle_(function () {
    const path = miraPath_(e);
    if (path === '/v1/query') {
      return miraReadQuery_(miraJsonBody_(e));
    }
    if (path === '/v1/commands') {
      throw miraError_(
        'not_implemented',
        'Workspace command handling is not enabled in this read-only slice',
      );
    }
    throw miraError_('route_not_found', 'route not found');
  });
}

function miraReadQuery_(body) {
  miraRequireObject_(body, 'query envelope');
  miraRejectExtraKeys_(body, [
    'request_id',
    'subject_id',
    'data_class',
    'action',
    'api_major',
    'schema_version',
    'resource_id',
    'filters',
    'limit',
  ]);

  const requestId = miraId_(body.request_id, 'request_id');
  miraId_(body.subject_id, 'subject_id');
  const dataClass = miraDataClass_(body.data_class);
  if (body.action !== 'read') {
    throw miraError_(
      'validation_error',
      'read-only Workspace slice supports query action=read only',
    );
  }
  if (body.api_major !== MIRA_API_MAJOR_ || body.schema_version !== MIRA_API_SCHEMA_) {
    throw miraError_(
      'compatibility_error',
      'request API/schema version is incompatible with this service',
    );
  }
  const resourceId = miraId_(body.resource_id, 'resource_id');
  if (body.filters && Object.keys(body.filters).length) {
    throw miraError_('validation_error', 'read does not accept filters');
  }

  const schema = miraWorkspaceSchema_();
  if (schema.resource_types.indexOf(dataClass) === -1) {
    throw miraError_('validation_error', 'unknown resource type: ' + dataClass);
  }

  const resources = miraResourceRows_();
  const authority = miraResolveAuthority_(resources, dataClass, schema.schema_version);
  const record = miraFindResource_(resources, dataClass, resourceId);
  return {
    request_id: requestId,
    authority_id: authority.authority_id,
    items: [record],
  };
}

function miraWorkspaceSchema_() {
  const spreadsheet = miraSpreadsheet_();
  const sheet = spreadsheet.getSheetByName('Metadata');
  if (!sheet) {
    throw miraError_('authority_unavailable', 'missing required sheet tab: Metadata');
  }
  const rows = sheet.getDataRange().getValues();
  if (!rows.length || rows[0][0] !== 'Key' || rows[0][1] !== 'Value') {
    throw miraError_('validation_error', 'Metadata headers are invalid');
  }

  const metadata = {};
  for (let index = 1; index < rows.length; index += 1) {
    const key = String(rows[index][0] || '').trim();
    if (!key) continue;
    if (Object.prototype.hasOwnProperty.call(metadata, key)) {
      throw miraError_('conflict', 'duplicate Metadata key: ' + key);
    }
    metadata[key] = rows[index][1];
  }

  if (metadata.adapter_contract !== MIRA_STORE_CONTRACT_) {
    throw miraError_('validation_error', 'Google Workspace metadata does not declare STORE-001');
  }
  if (metadata.writer_model !== MIRA_WRITER_MODEL_) {
    throw miraError_('validation_error', 'Google Workspace requires writer_model=single_writer');
  }

  const schemaVersion = miraToken_(metadata.schema_version, 'schema_version');
  const resourceTypes = miraTypeArray_(metadata.resource_types_json, 'resource_types_json');
  const eventTypes = miraTypeArray_(metadata.event_types_json, 'event_types_json');
  return {
    schema_version: schemaVersion,
    resource_types: resourceTypes.sort(),
    event_types: eventTypes.sort(),
  };
}

function miraResolveAuthority_(resources, dataClass, schemaVersion) {
  const bindings = resources.filter(function (record) {
    return record.resource_type === 'authority_binding' &&
      record.payload && record.payload.data_class === dataClass;
  });
  if (bindings.length !== 1) {
    throw miraError_(
      'authority_unavailable',
      'expected exactly one authority binding for data class: ' + dataClass,
    );
  }

  const authorityId = miraId_(bindings[0].payload.authority_id, 'authority_id');
  const authorities = resources.filter(function (record) {
    return record.resource_type === 'authority' && record.resource_id === authorityId;
  });
  if (authorities.length !== 1) {
    throw miraError_('authority_unavailable', 'canonical authority record is missing or duplicated');
  }

  const payload = authorities[0].payload || {};
  if (payload.enabled !== true || payload.verified !== true) {
    throw miraError_('authority_unavailable', 'canonical authority is not verified and enabled');
  }
  if (payload.adapter_key !== 'google-sheets') {
    throw miraError_('authority_unavailable', 'canonical authority adapter is not Google Sheets');
  }
  if (payload.schema_version !== schemaVersion) {
    throw miraError_('authority_unavailable', 'canonical authority schema does not match Workspace state');
  }
  return {authority_id: authorityId};
}

function miraFindResource_(resources, resourceType, resourceId) {
  const matches = resources.filter(function (record) {
    return record.resource_type === resourceType && record.resource_id === resourceId;
  });
  if (!matches.length) {
    throw miraError_('not_found', resourceType + ':' + resourceId + ' does not exist');
  }
  if (matches.length !== 1) {
    throw miraError_('conflict', 'duplicate persisted resource identity');
  }
  return matches[0];
}

function miraResourceRows_() {
  const spreadsheet = miraSpreadsheet_();
  const sheet = spreadsheet.getSheetByName('Resources');
  if (!sheet) {
    throw miraError_('authority_unavailable', 'missing required sheet tab: Resources');
  }
  const rows = sheet.getDataRange().getValues();
  const requiredHeaders = [
    'resource_type',
    'resource_id',
    'revision',
    'payload_json',
    'updated_at',
    'last_idempotency_key',
    'request_hash',
  ];
  if (!rows.length) {
    throw miraError_('validation_error', 'Resources tab is empty');
  }
  const header = rows[0].map(function (value) { return String(value || ''); });
  requiredHeaders.forEach(function (name, index) {
    if (header[index] !== name) {
      throw miraError_('validation_error', 'Resources headers are invalid');
    }
  });

  const records = [];
  for (let index = 1; index < rows.length; index += 1) {
    const row = rows[index];
    const resourceType = String(row[0] || '').trim();
    const resourceId = String(row[1] || '').trim();
    if (!resourceType && !resourceId) continue;
    const revision = Number(row[2]);
    if (!Number.isInteger(revision) || revision < 1) {
      throw miraError_('validation_error', 'persisted resource revision is invalid');
    }
    let payload;
    try {
      payload = JSON.parse(String(row[3] || ''));
    } catch (error) {
      throw miraError_('validation_error', 'persisted resource payload_json is invalid');
    }
    miraRequireObject_(payload, 'persisted resource payload');
    records.push({
      resource_type: miraDataClass_(resourceType),
      resource_id: miraId_(resourceId, 'resource_id'),
      payload: payload,
      revision: revision,
    });
  }
  return records;
}

function miraSpreadsheet_() {
  const id = PropertiesService.getScriptProperties().getProperty(MIRA_SPREADSHEET_PROPERTY_);
  if (!id || String(id).trim() !== String(id)) {
    throw miraError_(
      'not_initialized',
      'Open the copied Sheet and choose MIRA > Initialize this copy before deploying the web app',
    );
  }
  return SpreadsheetApp.openById(id);
}

function miraJsonBody_(e) {
  if (!e || !e.postData || typeof e.postData.contents !== 'string') {
    throw miraError_('invalid_request', 'request body is unavailable');
  }
  if (e.postData.contents.length > 65536) {
    throw miraError_('payload_too_large', 'request body exceeds configured limit');
  }
  let body;
  try {
    body = JSON.parse(e.postData.contents);
  } catch (error) {
    throw miraError_('invalid_json', 'request body must be valid JSON');
  }
  miraRequireObject_(body, 'request JSON');
  return body;
}

function miraPath_(e) {
  const raw = e && typeof e.pathInfo === 'string' ? e.pathInfo : '';
  return '/' + raw.replace(/^\/+|\/+$/g, '');
}

function miraHandle_(work) {
  try {
    return miraJsonOutput_(work());
  } catch (error) {
    const code = error && error.miraCode ? error.miraCode : 'internal_error';
    const message = code === 'internal_error'
      ? 'unexpected Workspace runtime failure'
      : String(error.message || error);
    return miraJsonOutput_({error: {code: code, message: message}});
  }
}

function miraJsonOutput_(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}

function miraError_(code, message) {
  const error = new Error(message);
  error.miraCode = code;
  return error;
}

function miraRequireObject_(value, field) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw miraError_('validation_error', field + ' must be an object');
  }
}

function miraRejectExtraKeys_(value, allowed) {
  Object.keys(value).forEach(function (key) {
    if (allowed.indexOf(key) === -1) {
      throw miraError_('invalid_request', 'unexpected query field: ' + key);
    }
  });
}

function miraId_(value, field) {
  if (typeof value !== 'string' || !MIRA_ID_RE_.test(value)) {
    throw miraError_('validation_error', field + ' is invalid');
  }
  return value;
}

function miraDataClass_(value) {
  if (typeof value !== 'string' || !MIRA_CLASS_RE_.test(value)) {
    throw miraError_('validation_error', 'data_class/resource_type is invalid');
  }
  return value;
}

function miraToken_(value, field) {
  if (typeof value !== 'string' || !value || value.trim() !== value || value.length > 256) {
    throw miraError_('validation_error', field + ' is invalid');
  }
  return value;
}

function miraTypeArray_(value, field) {
  let parsed;
  try {
    parsed = JSON.parse(String(value || ''));
  } catch (error) {
    throw miraError_('validation_error', field + ' is invalid JSON');
  }
  if (!Array.isArray(parsed) || !parsed.length) {
    throw miraError_('validation_error', field + ' must be a non-empty JSON array');
  }
  const seen = {};
  return parsed.map(function (item) {
    const normalized = miraDataClass_(item);
    if (seen[normalized]) {
      throw miraError_('validation_error', field + ' contains duplicates');
    }
    seen[normalized] = true;
    return normalized;
  });
}
