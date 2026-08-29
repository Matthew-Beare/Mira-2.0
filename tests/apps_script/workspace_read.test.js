'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const SOURCE = fs.readFileSync(
  path.join(process.cwd(), 'workspace', 'apps_script', 'Code.gs'),
  'utf8',
);

function starterRows() {
  return {
    Metadata: [
      ['Key', 'Value'],
      ['adapter_contract', 'STORE-001'],
      ['writer_model', 'single_writer'],
      ['schema_version', 'mira-structured-state-v1'],
      ['resource_types_json', '["authority","authority_binding","entity"]'],
      ['event_types_json', '["created","updated"]'],
    ],
    Resources: [
      [
        'resource_type',
        'resource_id',
        'revision',
        'payload_json',
        'updated_at',
        'last_idempotency_key',
        'request_hash',
      ],
      [
        'authority',
        'google-sheets-m0',
        1,
        JSON.stringify({
          adapter_key: 'google-sheets',
          resource_ref: 'runtime:google-structured-state',
          namespace: 'mira-2-sandbox',
          failure_domain: 'google-sheets-sandbox',
          owner_id: 'm0-synthetic-user',
          schema_version: 'mira-structured-state-v1',
          verified: true,
          enabled: true,
        }),
        '2026-08-29T00:00:00Z',
        'bootstrap-authority-google-sheets-m0',
        'hash-authority',
      ],
      [
        'authority_binding',
        'binding-entity',
        1,
        JSON.stringify({data_class: 'entity', authority_id: 'google-sheets-m0'}),
        '2026-08-29T00:00:00Z',
        'bootstrap-binding-entity',
        'hash-binding',
      ],
      [
        'entity',
        'synthetic-1',
        3,
        JSON.stringify({name: 'Synthetic One', state: 'ready'}),
        '2026-08-29T00:00:00Z',
        'entity-3',
        'hash-entity',
      ],
    ],
  };
}

function runtime(options = {}) {
  const rows = options.rows || starterRows();
  const properties = new Map();
  if (options.initialized !== false) {
    properties.set('MIRA_SPREADSHEET_ID', 'sheet-test-copy');
  }
  const alerts = [];
  const menu = [];

  const ui = {
    ButtonSet: {OK: 'OK'},
    alert(...args) {
      alerts.push(args);
    },
    createMenu(name) {
      return {
        addItem(label, fn) {
          menu.push([name, label, fn]);
          return this;
        },
        addToUi() {
          return this;
        },
      };
    },
  };

  function workbook() {
    return {
      getId() {
        return 'sheet-test-copy';
      },
      getSheetByName(name) {
        if (!Object.prototype.hasOwnProperty.call(rows, name)) return null;
        return {
          getDataRange() {
            return {
              getValues() {
                return rows[name].map((row) => row.slice());
              },
            };
          },
        };
      },
    };
  }

  const context = {
    console,
    JSON,
    Object,
    Array,
    Number,
    String,
    Error,
    RegExp,
    PropertiesService: {
      getScriptProperties() {
        return {
          getProperty(name) {
            return properties.has(name) ? properties.get(name) : null;
          },
          setProperty(name, value) {
            properties.set(name, value);
          },
        };
      },
    },
    SpreadsheetApp: {
      getUi() {
        return ui;
      },
      getActiveSpreadsheet() {
        return workbook();
      },
      openById(id) {
        assert.equal(id, 'sheet-test-copy');
        return workbook();
      },
    },
    ContentService: {
      MimeType: {JSON: 'application/json'},
      createTextOutput(text) {
        return {
          text,
          mimeType: null,
          setMimeType(value) {
            this.mimeType = value;
            return this;
          },
        };
      },
    },
  };
  vm.createContext(context);
  vm.runInContext(SOURCE, context, {filename: 'Code.gs'});
  return {context, properties, alerts, menu, rows};
}

function payload(output) {
  assert.equal(output.mimeType, 'application/json');
  return JSON.parse(output.text);
}

function post(context, pathInfo, body) {
  return payload(
    context.doPost({
      pathInfo,
      postData: {contents: JSON.stringify(body)},
    }),
  );
}

test('browser initializer binds the copied sheet in Script Properties', () => {
  const app = runtime({initialized: false});
  app.context.onOpen();
  assert.deepEqual(app.menu, [['MIRA', 'Initialize this copy', 'miraInitializeCopy']]);
  app.context.miraInitializeCopy();
  assert.equal(app.properties.get('MIRA_SPREADSHEET_ID'), 'sheet-test-copy');
  assert.equal(app.alerts.length, 1);
});

test('health validates Workspace schema before reporting ready', () => {
  const app = runtime();
  assert.deepEqual(payload(app.context.doGet({pathInfo: 'v1/health'})), {
    service: 'mira',
    status: 'ok',
  });
});

test('schema readback matches the persisted STORE-001 metadata', () => {
  const app = runtime();
  assert.deepEqual(payload(app.context.doGet({pathInfo: 'v1/schema'})), {
    schema_version: 'mira-structured-state-v1',
    resource_types: ['authority', 'authority_binding', 'entity'],
    event_types: ['created', 'updated'],
  });
});

test('read query resolves persisted authority then returns exact canonical entity', () => {
  const app = runtime();
  const result = post(app.context, 'v1/query', {
    request_id: 'read-1',
    subject_id: 'm0-synthetic-user',
    data_class: 'entity',
    action: 'read',
    api_major: 1,
    schema_version: 'mira-api-1',
    resource_id: 'synthetic-1',
  });
  assert.deepEqual(result, {
    request_id: 'read-1',
    authority_id: 'google-sheets-m0',
    items: [
      {
        resource_type: 'entity',
        resource_id: 'synthetic-1',
        payload: {name: 'Synthetic One', state: 'ready'},
        revision: 3,
      },
    ],
  });
});

test('uninitialized web execution fails closed without a provider id', () => {
  const app = runtime({initialized: false});
  assert.deepEqual(payload(app.context.doGet({pathInfo: 'v1/health'})), {
    error: {
      code: 'not_initialized',
      message: 'Open the copied Sheet and choose MIRA > Initialize this copy before deploying the web app',
    },
  });
});

test('API compatibility mismatch returns the stable MIRA error category', () => {
  const app = runtime();
  const result = post(app.context, 'v1/query', {
    request_id: 'read-2',
    subject_id: 'm0-synthetic-user',
    data_class: 'entity',
    action: 'read',
    api_major: 99,
    schema_version: 'mira-api-1',
    resource_id: 'synthetic-1',
  });
  assert.equal(result.error.code, 'compatibility_error');
});

test('missing canonical entity returns not_found', () => {
  const app = runtime();
  const result = post(app.context, 'v1/query', {
    request_id: 'read-3',
    subject_id: 'm0-synthetic-user',
    data_class: 'entity',
    action: 'read',
    api_major: 1,
    schema_version: 'mira-api-1',
    resource_id: 'missing',
  });
  assert.equal(result.error.code, 'not_found');
});

test('commands fail closed in the first read-only slice', () => {
  const app = runtime();
  const result = post(app.context, 'v1/commands', {});
  assert.deepEqual(result, {
    error: {
      code: 'not_implemented',
      message: 'Workspace command handling is not enabled in this read-only slice',
    },
  });
});
