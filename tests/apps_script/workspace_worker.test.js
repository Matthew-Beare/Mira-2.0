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
const CHANGE_HEADERS = [
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

function runtime(options = {}) {
  const rows = cloneRows(options.rows || baseRows());
  const properties = new Map([['MIRA_SPREADSHEET_ID', 'sheet-test-copy']]);
  const triggers = (options.triggers || []).map((handler) => triggerObject(handler));
  const triggerCreations = [];
  const lockEvents = [];
  let flushes = 0;

  function triggerObject(handler) {
    return {
      getHandlerFunction() {
        return handler;
      },
    };
  }

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
        return 'sheet-test-copy';
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

  const lock = {
    waitLock(milliseconds) {
      lockEvents.push(['wait', milliseconds]);
    },
    releaseLock() {
      lockEvents.push(['release']);
    },
  };

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
        assert.equal(id, 'sheet-test-copy');
        return workbook();
      },
      flush() {
        flushes += 1;
      },
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
            triggerCreations.push([handler, this.minutes]);
            triggers.push(triggerObject(handler));
            return triggerObject(handler);
          },
        };
      },
    },
    LockService: {
      getScriptLock() {
        return lock;
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
  return {
    context,
    rows,
    properties,
    triggers,
    triggerCreations,
    lockEvents,
    get flushes() { return flushes; },
  };
}

function metadataValue(app, key) {
  const matches = app.rows.Metadata.slice(1).filter((row) => row[0] === key);
  return matches.length === 1 ? matches[0][1] : null;
}

function commandRow({
  commandId = 'cmd-001',
  subjectId = 'm0-synthetic-user',
  resourceId = 'shared-entity-001',
  state = 'created',
  idempotencyKey = 'idem-001',
  expectedRevision = 0,
} = {}) {
  return [
    commandId,
    subjectId,
    'entity',
    'upsert',
    1,
    'mira-api-1',
    resourceId,
    JSON.stringify({state}),
    idempotencyKey,
    expectedRevision,
    '2026-08-29T20:00:00Z',
    'pending',
    '',
    '',
    '',
    '',
  ];
}

function enableAndQueue(app, ...commands) {
  const activation = app.context.miraEnableQueuedWriter();
  assert.equal(activation.mutation_mode, 'queued_writer');
  commands.forEach((row) => app.rows.Commands.push(row));
}

function entityRows(app, resourceId = 'shared-entity-001') {
  return app.rows.Resources.slice(1).filter(
    (row) => row[0] === 'entity' && row[1] === resourceId,
  );
}

function idempotencyRows(app, key = 'idem-001') {
  return app.rows.Idempotency.slice(1).filter((row) => row[0] === key);
}

function changeRows(app, resourceId = null) {
  const rows = app.rows.Changes.slice(1);
  return resourceId === null ? rows : rows.filter((row) => row[3] === resourceId);
}

function addCanonicalEntity(rows, {
  resourceId = 'existing-entity',
  revision = 2,
  state = 'already-here',
} = {}) {
  rows.Resources.push([
    'entity',
    resourceId,
    revision,
    JSON.stringify({state}),
    '2026-08-29T19:00:00Z',
    'prior-idem',
    'prior-hash',
  ]);
}

test('queued-writer activation creates Commands, Changes and exactly one one-minute trigger', () => {
  const app = runtime();
  const first = app.context.miraEnableQueuedWriter();
  assert.equal(first.mutation_mode, 'queued_writer');
  assert.equal(first.worker, 'miraProcessCommandQueue');
  assert.equal(first.interval_minutes, 1);
  assert.deepEqual(app.rows.Commands[0], COMMAND_HEADERS);
  assert.deepEqual(app.rows.Changes[0], CHANGE_HEADERS);
  assert.equal(metadataValue(app, 'mutation_mode'), 'queued_writer');
  assert.deepEqual(app.triggerCreations, [['miraProcessCommandQueue', 1]]);

  app.context.miraEnableQueuedWriter();
  assert.deepEqual(app.triggerCreations, [['miraProcessCommandQueue', 1]]);
  assert.equal(app.triggers.length, 1);
  assert.deepEqual(app.rows.Changes[0], CHANGE_HEADERS);
});

test('duplicate worker triggers fail before queued mode becomes authoritative', () => {
  const app = runtime({triggers: ['miraProcessCommandQueue', 'miraProcessCommandQueue']});
  assert.throws(
    () => app.context.miraEnableQueuedWriter(),
    (error) => error.miraCode === 'conflict',
  );
  assert.equal(metadataValue(app, 'mutation_mode'), null);
});

test('worker seeds current non-internal canonical Resources into verified Changes', () => {
  const rows = baseRows();
  addCanonicalEntity(rows);
  const app = runtime({rows});
  enableAndQueue(app);
  const result = app.context.miraProcessCommandQueue();

  assert.equal(result.processed, 0);
  assert.equal(changeRows(app).length, 1);
  const change = changeRows(app)[0];
  assert.equal(change[0], 1);
  assert.equal(change[2], 'entity');
  assert.equal(change[3], 'existing-entity');
  assert.equal(change[4], 2);
  assert.deepEqual(JSON.parse(change[5]), {state: 'already-here'});
  assert.equal(change[7], '');
  assert.equal(change[8], true);
  assert.match(change[1], /^[0-9a-f]{64}$/);

  app.context.miraProcessCommandQueue();
  assert.equal(changeRows(app).length, 1);
});

test('worker locks, commits one canonical create, reads it back, projects it and acknowledges command', () => {
  const app = runtime();
  enableAndQueue(app, commandRow());
  const result = app.context.miraProcessCommandQueue();

  assert.equal(result.processed, 1);
  assert.deepEqual(app.lockEvents, [['wait', 30000], ['release']]);
  assert.equal(entityRows(app).length, 1);
  assert.equal(entityRows(app)[0][2], 1);
  assert.deepEqual(JSON.parse(entityRows(app)[0][3]), {state: 'created'});
  assert.equal(idempotencyRows(app).length, 1);
  assert.equal(app.rows.Commands[1][11], 'succeeded');
  const commandResult = JSON.parse(app.rows.Commands[1][12]);
  assert.equal(commandResult.record.revision, 1);
  assert.equal(commandResult.idempotent_replay, false);
  assert.equal(commandResult.readback_verified, true);
  assert.equal(changeRows(app, 'shared-entity-001').length, 1);
  assert.equal(changeRows(app, 'shared-entity-001')[0][7], 'cmd-001');
  assert.equal(changeRows(app, 'shared-entity-001')[0][8], true);

  const second = app.context.miraProcessCommandQueue();
  assert.equal(second.processed, 0);
  assert.equal(entityRows(app).length, 1);
  assert.equal(idempotencyRows(app).length, 1);
  assert.equal(changeRows(app, 'shared-entity-001').length, 1);
});

test('two stale revision-zero commands serialize so only first commits', () => {
  const app = runtime();
  enableAndQueue(
    app,
    commandRow({commandId: 'cmd-a', idempotencyKey: 'idem-a', state: 'alpha'}),
    commandRow({commandId: 'cmd-b', idempotencyKey: 'idem-b', state: 'beta'}),
  );
  const result = app.context.miraProcessCommandQueue();
  assert.equal(result.processed, 2);

  assert.equal(app.rows.Commands[1][11], 'succeeded');
  assert.equal(app.rows.Commands[2][11], 'failed');
  assert.equal(app.rows.Commands[2][14], 'conflict');
  assert.equal(entityRows(app).length, 1);
  assert.equal(entityRows(app)[0][2], 1);
  assert.deepEqual(JSON.parse(entityRows(app)[0][3]), {state: 'alpha'});
  assert.equal(idempotencyRows(app, 'idem-a').length, 1);
  assert.equal(idempotencyRows(app, 'idem-b').length, 0);
  assert.equal(changeRows(app, 'shared-entity-001').length, 1);
});

test('crash after resource write leaves pending command and retry reconstructs idempotency without revision bump', () => {
  const app = runtime();
  enableAndQueue(app, commandRow({commandId: 'cmd-crash', idempotencyKey: 'idem-crash'}));
  const originalAppend = app.context.miraAppendIdempotency_;
  let crashed = false;
  app.context.miraAppendIdempotency_ = function (...args) {
    if (!crashed) {
      crashed = true;
      throw new Error('synthetic post-resource crash');
    }
    return originalAppend(...args);
  };

  const first = app.context.miraProcessCommandQueue();
  assert.equal(first.processed, 1);
  assert.equal(app.rows.Commands[1][11], 'pending');
  assert.equal(entityRows(app).length, 1);
  assert.equal(entityRows(app)[0][2], 1);
  assert.equal(idempotencyRows(app, 'idem-crash').length, 0);

  app.context.miraAppendIdempotency_ = originalAppend;
  const second = app.context.miraProcessCommandQueue();
  assert.equal(second.processed, 1);
  assert.equal(app.rows.Commands[1][11], 'succeeded');
  assert.equal(entityRows(app).length, 1);
  assert.equal(entityRows(app)[0][2], 1);
  assert.equal(idempotencyRows(app, 'idem-crash').length, 1);
  assert.equal(changeRows(app, 'shared-entity-001').length, 1);
  const commandResult = JSON.parse(app.rows.Commands[1][12]);
  assert.equal(commandResult.record.revision, 1);
  assert.equal(commandResult.idempotent_replay, true);
});

test('crash after verified change append leaves command pending and retry reuses one projection row', () => {
  const app = runtime();
  enableAndQueue(app, commandRow({commandId: 'cmd-change-crash', idempotencyKey: 'idem-change-crash'}));
  const originalEnsure = app.context.miraEnsureVerifiedChange_;
  let crashed = false;
  app.context.miraEnsureVerifiedChange_ = function (...args) {
    const result = originalEnsure(...args);
    if (!crashed) {
      crashed = true;
      throw new Error('synthetic post-change crash');
    }
    return result;
  };

  const first = app.context.miraProcessCommandQueue();
  assert.equal(first.processed, 1);
  assert.equal(app.rows.Commands[1][11], 'pending');
  assert.equal(entityRows(app).length, 1);
  assert.equal(idempotencyRows(app, 'idem-change-crash').length, 1);
  assert.equal(changeRows(app, 'shared-entity-001').length, 1);

  app.context.miraEnsureVerifiedChange_ = originalEnsure;
  const second = app.context.miraProcessCommandQueue();
  assert.equal(second.processed, 1);
  assert.equal(app.rows.Commands[1][11], 'succeeded');
  assert.equal(entityRows(app)[0][2], 1);
  assert.equal(idempotencyRows(app, 'idem-change-crash').length, 1);
  assert.equal(changeRows(app, 'shared-entity-001').length, 1);
  const commandResult = JSON.parse(app.rows.Commands[1][12]);
  assert.equal(commandResult.idempotent_replay, true);
});

test('exact duplicate physical command rows converge as one logical command', () => {
  const app = runtime();
  const first = commandRow({commandId: 'cmd-dup', idempotencyKey: 'idem-dup'});
  const second = first.slice();
  second[10] = '2026-08-29T20:00:05Z';
  enableAndQueue(app, first, second);

  const result = app.context.miraProcessCommandQueue();
  assert.equal(result.processed, 1);
  assert.equal(app.rows.Commands[1][11], 'succeeded');
  assert.equal(app.rows.Commands[2][11], 'succeeded');
  assert.equal(app.rows.Commands[1][12], app.rows.Commands[2][12]);
  assert.equal(entityRows(app).length, 1);
  assert.equal(entityRows(app)[0][2], 1);
  assert.equal(idempotencyRows(app, 'idem-dup').length, 1);
  assert.equal(changeRows(app, 'shared-entity-001').length, 1);
});

test('duplicate physical command ID with different material fails closed before mutation', () => {
  const app = runtime();
  enableAndQueue(
    app,
    commandRow({commandId: 'cmd-mismatch', idempotencyKey: 'idem-a', state: 'alpha'}),
    commandRow({commandId: 'cmd-mismatch', idempotencyKey: 'idem-b', state: 'beta'}),
  );

  const result = app.context.miraProcessCommandQueue();
  assert.equal(result.processed, 1);
  assert.equal(app.rows.Commands[1][11], 'failed');
  assert.equal(app.rows.Commands[2][11], 'failed');
  assert.equal(app.rows.Commands[1][14], 'conflict');
  assert.equal(app.rows.Commands[2][14], 'conflict');
  assert.equal(entityRows(app).length, 0);
  assert.equal(idempotencyRows(app, 'idem-a').length, 0);
  assert.equal(idempotencyRows(app, 'idem-b').length, 0);
  assert.equal(changeRows(app).length, 0);
});

test('contradictory same-revision change material fails closed', () => {
  const rows = baseRows();
  addCanonicalEntity(rows, {resourceId: 'existing-entity', revision: 2, state: 'canonical'});
  rows.Changes = [CHANGE_HEADERS, [
    1,
    '0'.repeat(64),
    'entity',
    'existing-entity',
    2,
    JSON.stringify({state: 'wrong'}),
    '2026-08-29T19:01:00Z',
    '',
    true,
  ]];
  const app = runtime({rows});
  enableAndQueue(app);

  assert.throws(
    () => app.context.miraProcessCommandQueue(),
    (error) => error.miraCode === 'readback_error',
  );
  assert.equal(changeRows(app).length, 1);
});

test('worker without queued mode fails closed and still releases ScriptLock', () => {
  const app = runtime();
  assert.throws(
    () => app.context.miraProcessCommandQueue(),
    (error) => error.miraCode === 'queued_writer_not_enabled',
  );
  assert.deepEqual(app.lockEvents, [['wait', 30000], ['release']]);
});

test('subject mismatch is terminal authorization failure with no entity mutation', () => {
  const app = runtime();
  enableAndQueue(
    app,
    commandRow({
      commandId: 'cmd-other',
      idempotencyKey: 'idem-other',
      subjectId: 'some-other-user',
    }),
  );
  const result = app.context.miraProcessCommandQueue();
  assert.equal(result.processed, 1);
  assert.equal(app.rows.Commands[1][11], 'failed');
  assert.equal(app.rows.Commands[1][14], 'authorization_error');
  assert.equal(entityRows(app).length, 0);
  assert.equal(idempotencyRows(app, 'idem-other').length, 0);
  assert.equal(changeRows(app).length, 0);
});
