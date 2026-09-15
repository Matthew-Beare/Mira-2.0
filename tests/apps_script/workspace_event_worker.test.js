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
  'command_id', 'subject_id', 'data_class', 'action', 'api_major', 'schema_version',
  'resource_id', 'payload_json', 'idempotency_key', 'expected_revision', 'submitted_at',
  'status', 'result_json', 'processed_at', 'error_code', 'error_message',
];
const EVENT_HEADERS = [
  'event_type', 'event_id', 'stream_type', 'stream_id', 'stream_revision',
  'payload_json', 'occurred_at', 'idempotency_key',
];
const CHANGE_HEADERS = [
  'change_seq', 'change_id', 'data_class', 'resource_id', 'revision', 'payload_json',
  'recorded_at', 'source_command_id', 'readback_verified',
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
      ['resource_type', 'resource_id', 'revision', 'payload_json', 'updated_at',
        'last_idempotency_key', 'request_hash'],
      ['authority', 'google-sheets-m0', 1, JSON.stringify({
        adapter_key: 'google-sheets',
        authority_id: 'google-sheets-m0',
        resource_ref: 'runtime:google-structured-state',
        namespace: 'mira-2-sandbox',
        failure_domain: 'google-sheets-sandbox',
        owner_id: 'm0-synthetic-user',
        schema_version: 'mira-structured-state-v1',
        verified: true,
        enabled: true,
      }), '2026-08-29T00:00:00Z', 'bootstrap-authority', 'hash-authority'],
      ['authority_binding', 'binding-entity', 1,
        JSON.stringify({data_class: 'entity', authority_id: 'google-sheets-m0'}),
        '2026-08-29T00:00:00Z', 'bootstrap-binding', 'hash-binding'],
    ],
    Events: [EVENT_HEADERS.slice()],
    Idempotency: [[
      'idempotency_key', 'operation', 'request_hash', 'result_json', 'created_at',
      'resource_ref',
    ]],
  };
}

function runtime() {
  const rows = Object.fromEntries(
    Object.entries(baseRows()).map(([name, table]) => [name, table.map((row) => row.slice())]),
  );
  const properties = new Map([['MIRA_SPREADSHEET_ID', 'sheet-test-copy']]);
  const triggers = [];

  function ensureRow(table, rowIndex, width) {
    while (table.length <= rowIndex) table.push([]);
    while (table[rowIndex].length < width) table[rowIndex].push('');
  }

  function sheet(name) {
    return {
      getDataRange() {
        return {getValues() { return rows[name].map((row) => row.slice()); }};
      },
      getLastRow() { return rows[name].length; },
      getRange(row, column, numRows, numColumns) {
        return {
          setValues(values) {
            values.forEach((source, rowOffset) => {
              assert.equal(source.length, numColumns);
              const target = row - 1 + rowOffset;
              ensureRow(rows[name], target, column - 1 + numColumns);
              source.forEach((value, columnOffset) => {
                rows[name][target][column - 1 + columnOffset] = value;
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
      getId() { return 'sheet-test-copy'; },
      getSheetByName(name) {
        return Object.prototype.hasOwnProperty.call(rows, name) ? sheet(name) : null;
      },
      insertSheet(name) {
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
          getProperty(name) { return properties.has(name) ? properties.get(name) : null; },
          setProperty(name, value) { properties.set(name, value); },
        };
      },
    },
    SpreadsheetApp: {
      getUi() {
        return {
          ButtonSet: {OK: 'OK'},
          alert() {},
          createMenu() { return {addItem() { return this; }, addToUi() { return this; }}; },
        };
      },
      getActiveSpreadsheet() { return workbook(); },
      openById(id) { assert.equal(id, 'sheet-test-copy'); return workbook(); },
      flush() {},
    },
    ScriptApp: {
      getProjectTriggers() { return triggers.slice(); },
      newTrigger(handler) {
        return {
          timeBased() { return this; },
          everyMinutes() { return this; },
          create() {
            const trigger = {getHandlerFunction() { return handler; }};
            triggers.push(trigger);
            return trigger;
          },
        };
      },
    },
    LockService: {
      getScriptLock() { return {waitLock() {}, releaseLock() {}}; },
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
        return {text, setMimeType() { return this; }};
      },
    },
  };

  vm.createContext(context);
  vm.runInContext(CODE_SOURCE, context, {filename: 'Code.gs'});
  vm.runInContext(WORKER_SOURCE, context, {filename: 'CommandWorker.gs'});
  context.miraEnableQueuedWriter();
  return {context, rows};
}

function eventCommand({
  commandId = 'cmd-event-1',
  eventId = 'event-1',
  idempotencyKey = 'idem-event-1',
  expectedRevision = '',
  payload = {state: 'observed'},
  eventType = 'updated',
} = {}) {
  return [
    commandId,
    'm0-synthetic-user',
    'entity',
    'append_event',
    1,
    'mira-api-1',
    'shared-entity-001',
    JSON.stringify({event_id: eventId, event_type: eventType, payload}),
    idempotencyKey,
    expectedRevision,
    '2026-09-15T20:00:00Z',
    'pending',
    '', '', '', '',
  ];
}

function events(app) {
  return app.rows.Events.slice(1);
}

function idempotency(app, key) {
  return app.rows.Idempotency.slice(1).filter((row) => row[0] === key);
}

test('append_event commits one canonical event and exact idempotency readback', () => {
  const app = runtime();
  app.rows.Commands.push(eventCommand());

  const result = app.context.miraProcessCommandQueue();

  assert.equal(result.processed, 1);
  assert.equal(events(app).length, 1);
  assert.deepEqual(events(app)[0].slice(0, 5), [
    'updated', 'event-1', 'entity', 'shared-entity-001', 1,
  ]);
  assert.deepEqual(JSON.parse(events(app)[0][5]), {state: 'observed'});
  assert.equal(events(app)[0][7], 'idem-event-1');
  assert.equal(idempotency(app, 'idem-event-1').length, 1);
  assert.equal(idempotency(app, 'idem-event-1')[0][1], 'append_event');
  assert.equal(idempotency(app, 'idem-event-1')[0][5], 'entity/shared-entity-001#event-1');
  assert.equal(app.rows.Commands[1][11], 'succeeded');
  const commandResult = JSON.parse(app.rows.Commands[1][12]);
  assert.equal(commandResult.record, null);
  assert.equal(commandResult.event.event_id, 'event-1');
  assert.equal(commandResult.event.stream_revision, 1);
  assert.equal(commandResult.idempotent_replay, false);
  assert.equal(commandResult.readback_verified, true);
  assert.equal(app.rows.Changes.length, 1);
});

test('duplicate physical append_event rows converge to one event', () => {
  const app = runtime();
  const first = eventCommand({commandId: 'cmd-dupe', eventId: 'event-dupe', idempotencyKey: 'idem-dupe'});
  const second = first.slice();
  second[10] = '2026-09-15T20:00:05Z';
  app.rows.Commands.push(first, second);

  const result = app.context.miraProcessCommandQueue();

  assert.equal(result.processed, 1);
  assert.equal(events(app).length, 1);
  assert.equal(idempotency(app, 'idem-dupe').length, 1);
  assert.equal(app.rows.Commands[1][11], 'succeeded');
  assert.equal(app.rows.Commands[2][11], 'succeeded');
  assert.equal(app.rows.Commands[1][12], app.rows.Commands[2][12]);
});

test('event-first crash recovers missing idempotency without duplicate event', () => {
  const app = runtime();
  app.rows.Commands.push(eventCommand({
    commandId: 'cmd-crash',
    eventId: 'event-crash',
    idempotencyKey: 'idem-crash',
  }));
  const originalAppend = app.context.miraAppendIdempotency_;
  let crashed = false;
  app.context.miraAppendIdempotency_ = function (...args) {
    if (!crashed) {
      crashed = true;
      throw new Error('synthetic post-event crash');
    }
    return originalAppend(...args);
  };

  app.context.miraProcessCommandQueue();
  assert.equal(app.rows.Commands[1][11], 'pending');
  assert.equal(events(app).length, 1);
  assert.equal(idempotency(app, 'idem-crash').length, 0);

  app.context.miraAppendIdempotency_ = originalAppend;
  app.context.miraProcessCommandQueue();
  assert.equal(app.rows.Commands[1][11], 'succeeded');
  assert.equal(events(app).length, 1);
  assert.equal(idempotency(app, 'idem-crash').length, 1);
  const commandResult = JSON.parse(app.rows.Commands[1][12]);
  assert.equal(commandResult.idempotent_replay, true);
});

test('stale expected stream revision fails without second event', () => {
  const app = runtime();
  app.rows.Commands.push(eventCommand({
    commandId: 'cmd-first', eventId: 'event-first', idempotencyKey: 'idem-first', expectedRevision: 0,
  }));
  app.context.miraProcessCommandQueue();
  app.rows.Commands.push(eventCommand({
    commandId: 'cmd-stale', eventId: 'event-stale', idempotencyKey: 'idem-stale', expectedRevision: 0,
  }));

  app.context.miraProcessCommandQueue();

  assert.equal(events(app).length, 1);
  assert.equal(app.rows.Commands[2][11], 'failed');
  assert.equal(app.rows.Commands[2][14], 'conflict');
  assert.equal(idempotency(app, 'idem-stale').length, 0);
});

test('malformed append_event transport envelope fails closed before event write', () => {
  const app = runtime();
  const row = eventCommand({commandId: 'cmd-bad', eventId: 'event-bad', idempotencyKey: 'idem-bad'});
  row[7] = JSON.stringify({
    event_id: 'event-bad',
    event_type: 'updated',
    payload: {state: 'observed'},
    surprise: true,
  });
  app.rows.Commands.push(row);

  app.context.miraProcessCommandQueue();

  assert.equal(events(app).length, 0);
  assert.equal(app.rows.Commands[1][11], 'failed');
  assert.equal(app.rows.Commands[1][14], 'invalid_request');
  assert.equal(idempotency(app, 'idem-bad').length, 0);
});
