'use strict';

const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const CODE_SOURCE = fs.readFileSync(
  path.join(process.cwd(), 'workspace', 'apps_script', 'Code.gs'),
  'utf8',
);
const WORKER_SOURCE = fs.readFileSync(
  path.join(process.cwd(), 'workspace', 'apps_script', 'CommandWorker.gs'),
  'utf8',
);

const COMMAND_HEADERS = [
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

function baseRows() {
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
          authority_id: 'google-sheets-m0',
          resource_ref: 'runtime:google-structured-state',
          namespace: 'mira-2-sandbox',
          failure_domain: 'google-sheets-sandbox',
          owner_id: 'm0-synthetic-user',
          schema_version: 'mira-structured-state-v1',
          verified: true,
          enabled: true,
        }),
        '2026-09-04T16:00:00Z',
        'bootstrap-authority-google-sheets-m0',
        'hash-authority',
      ],
      [
        'authority_binding',
        'binding-entity',
        1,
        JSON.stringify({data_class: 'entity', authority_id: 'google-sheets-m0'}),
        '2026-09-04T16:00:00Z',
        'bootstrap-binding-entity',
        'hash-binding',
      ],
    ],
    Events: [[
      'event_type',
      'event_id',
      'stream_type',
      'stream_id',
      'stream_revision',
      'payload_json',
      'occurred_at',
      'idempotency_key',
    ]],
    Idempotency: [[
      'idempotency_key',
      'operation',
      'request_hash',
      'result_json',
      'created_at',
      'resource_ref',
    ]],
  };
}

function cloneRows(rows) {
  return Object.fromEntries(
    Object.entries(rows).map(([name, table]) => [name, table.map((row) => row.slice())]),
  );
}

function runtime(seed = baseRows()) {
  const rows = cloneRows(seed);
  const properties = new Map([['MIRA_SPREADSHEET_ID', 'sheet-cross-readback']]);
  const triggers = [];

  function ensureRow(table, rowIndex, width) {
    while (table.length <= rowIndex) table.push([]);
    while (table[rowIndex].length < width) table[rowIndex].push('');
  }

  function sheet(name) {
    return {
      getDataRange() {
        return {
          getValues() {
            return rows[name].map((row) => row.slice());
          },
        };
      },
      getLastRow() {
        return rows[name].length;
      },
      getRange(row, column, numRows, numColumns) {
        return {
          setValues(values) {
            assert.equal(values.length, numRows);
            values.forEach((source, rowOffset) => {
              assert.equal(source.length, numColumns);
              const targetIndex = row - 1 + rowOffset;
              ensureRow(rows[name], targetIndex, column - 1 + numColumns);
              source.forEach((value, columnOffset) => {
                rows[name][targetIndex][column - 1 + columnOffset] = value;
              });
            });
            return this;
          },
        };
      },
    };
  }

  function workbook() {
    return {
      getId() {
        return 'sheet-cross-readback';
      },
      getSheetByName(name) {
        return Object.prototype.hasOwnProperty.call(rows, name) ? sheet(name) : null;
      },
      insertSheet(name) {
        assert.equal(Object.prototype.hasOwnProperty.call(rows, name), false);
        rows[name] = [];
        return sheet(name);
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
    Date,
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
        return {
          ButtonSet: {OK: 'OK'},
          alert() {},
          createMenu() {
            return {addItem() { return this; }, addToUi() { return this; }};
          },
        };
      },
      getActiveSpreadsheet() {
        return workbook();
      },
      openById(id) {
        assert.equal(id, 'sheet-cross-readback');
        return workbook();
      },
      flush() {},
    },
    ScriptApp: {
      getProjectTriggers() {
        return triggers.slice();
      },
      newTrigger(handler) {
        return {
          timeBased() {
            return this;
          },
          everyMinutes(minutes) {
            this.minutes = minutes;
            return this;
          },
          create() {
            const trigger = {getHandlerFunction() { return handler; }};
            triggers.push(trigger);
            return trigger;
          },
        };
      },
    },
    LockService: {
      getScriptLock() {
        return {waitLock() {}, releaseLock() {}};
      },
    },
    Utilities: {
      DigestAlgorithm: {SHA_256: 'SHA_256'},
      Charset: {UTF_8: 'UTF_8'},
      computeDigest(algorithm, text, charset) {
        assert.equal(algorithm, 'SHA_256');
        assert.equal(charset, 'UTF_8');
        return Array.from(crypto.createHash('sha256').update(text, 'utf8').digest());
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
  vm.runInContext(CODE_SOURCE, context, {filename: 'Code.gs'});
  vm.runInContext(WORKER_SOURCE, context, {filename: 'CommandWorker.gs'});
  return {context, rows};
}

function androidCommandRow({
  commandId = 'android-cmd-001',
  resourceId = 'cross-client-entity-001',
  payload = {origin: 'android', state: 'mutated'},
  idempotencyKey = 'android-idem-001',
  expectedRevision = 0,
} = {}) {
  const row = [
    commandId,
    'm0-synthetic-user',
    'entity',
    'upsert',
    1,
    'mira-api-1',
    resourceId,
    JSON.stringify(payload),
    idempotencyKey,
    expectedRevision,
    '2026-09-04T16:05:00Z',
    'pending',
    '',
    '',
    '',
    '',
  ];
  assert.equal(row.length, COMMAND_HEADERS.length);
  return row;
}

function postQuery(context, resourceId, requestId = 'chatgpt-read-001') {
  const output = context.doPost({
    pathInfo: 'v1/query',
    postData: {
      contents: JSON.stringify({
        request_id: requestId,
        subject_id: 'm0-synthetic-user',
        data_class: 'entity',
        action: 'read',
        api_major: 1,
        schema_version: 'mira-api-1',
        resource_id: resourceId,
      }),
    },
  });
  assert.equal(output.mimeType, 'application/json');
  return JSON.parse(output.text);
}

function entityRows(app, resourceId) {
  return app.rows.Resources.slice(1).filter(
    (row) => row[0] === 'entity' && row[1] === resourceId,
  );
}

test('stock ChatGPT query reads exact Android queued mutation from the same canonical authority', () => {
  const app = runtime();
  const targetId = 'cross-client-entity-001';
  assert.equal(entityRows(app, targetId).length, 0);

  const activation = app.context.miraEnableQueuedWriter();
  assert.equal(activation.mutation_mode, 'queued_writer');
  assert.deepEqual(app.rows.Commands[0], COMMAND_HEADERS);
  app.rows.Commands.push(androidCommandRow({resourceId: targetId}));

  const worker = app.context.miraProcessCommandQueue();
  assert.equal(worker.processed, 1);
  assert.equal(app.rows.Commands[1][11], 'succeeded');
  const terminal = JSON.parse(app.rows.Commands[1][12]);
  assert.equal(terminal.readback_verified, true);
  assert.equal(terminal.authority_id, 'google-sheets-m0');
  assert.equal(terminal.record.resource_type, 'entity');
  assert.equal(terminal.record.resource_id, targetId);
  assert.equal(terminal.record.revision, 1);
  assert.deepEqual(terminal.record.payload, {origin: 'android', state: 'mutated'});

  const canonical = entityRows(app, targetId);
  assert.equal(canonical.length, 1);
  assert.equal(canonical[0][2], 1);
  assert.deepEqual(JSON.parse(canonical[0][3]), {origin: 'android', state: 'mutated'});

  // The stock-ChatGPT query contract reads canonical Resources through Authority.
  // Remove the nonauthoritative reconnect projection to prove cross-readback does
  // not accidentally depend on Android-only synchronization evidence.
  delete app.rows.Changes;

  const readback = postQuery(app.context, targetId);
  assert.deepEqual(readback, {
    request_id: 'chatgpt-read-001',
    authority_id: 'google-sheets-m0',
    items: [{
      resource_type: 'entity',
      resource_id: targetId,
      payload: {origin: 'android', state: 'mutated'},
      revision: 1,
    }],
  });
  assert.deepEqual(readback.items[0], terminal.record);
});

test('queued mutation mode remains readable through the existing stock ChatGPT query contract', () => {
  const app = runtime();
  app.context.miraEnableQueuedWriter();
  const mutationMode = app.rows.Metadata.slice(1).find((row) => row[0] === 'mutation_mode');
  assert.deepEqual(mutationMode, ['mutation_mode', 'queued_writer']);

  app.rows.Commands.push(androidCommandRow({
    commandId: 'android-cmd-readable',
    resourceId: 'queued-readable-entity',
    idempotencyKey: 'android-idem-readable',
  }));
  app.context.miraProcessCommandQueue();

  const readback = postQuery(app.context, 'queued-readable-entity', 'chatgpt-read-queued');
  assert.equal(readback.authority_id, 'google-sheets-m0');
  assert.equal(readback.items[0].revision, 1);
  assert.deepEqual(readback.items[0].payload, {origin: 'android', state: 'mutated'});
});

test('failed stale Android command cannot masquerade as successful stock ChatGPT cross-readback', () => {
  const rows = baseRows();
  rows.Resources.push([
    'entity',
    'existing-cross-client',
    1,
    JSON.stringify({origin: 'canonical', state: 'before'}),
    '2026-09-04T16:02:00Z',
    'prior-idem',
    'prior-hash',
  ]);
  const app = runtime(rows);
  app.context.miraEnableQueuedWriter();
  app.rows.Commands.push(androidCommandRow({
    commandId: 'android-cmd-stale',
    resourceId: 'existing-cross-client',
    payload: {origin: 'android', state: 'should-not-commit'},
    idempotencyKey: 'android-idem-stale',
    expectedRevision: 0,
  }));

  const worker = app.context.miraProcessCommandQueue();
  assert.equal(worker.processed, 1);
  assert.equal(app.rows.Commands[1][11], 'failed');
  assert.equal(app.rows.Commands[1][14], 'conflict');

  const canonical = entityRows(app, 'existing-cross-client');
  assert.equal(canonical.length, 1);
  assert.equal(canonical[0][2], 1);
  assert.deepEqual(JSON.parse(canonical[0][3]), {origin: 'canonical', state: 'before'});

  const readback = postQuery(app.context, 'existing-cross-client', 'chatgpt-read-after-stale');
  assert.deepEqual(readback.items, [{
    resource_type: 'entity',
    resource_id: 'existing-cross-client',
    payload: {origin: 'canonical', state: 'before'},
    revision: 1,
  }]);
  assert.notDeepEqual(readback.items[0].payload, {origin: 'android', state: 'should-not-commit'});
});
