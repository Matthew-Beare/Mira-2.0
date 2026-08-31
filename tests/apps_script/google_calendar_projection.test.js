'use strict';

const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const SOURCE = fs.readFileSync(
  path.join(process.cwd(), 'workspace', 'apps_script', 'GoogleCalendarProjection.gs'),
  'utf8',
);

function response(status, body) {
  return {
    getResponseCode() {
      return status;
    },
    getContentText() {
      return body === null || body === undefined ? '' : JSON.stringify(body);
    },
  };
}

function runtime(options = {}) {
  const events = new Map();
  const requests = [];
  let nextId = 1;
  let nextVersion = 1;

  function eventCopy(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function makeEvent(body, id = `evt-${nextId++}`) {
    return {
      kind: 'calendar#event',
      id,
      etag: `"v${nextVersion++}"`,
      summary: body.summary,
      description: Object.prototype.hasOwnProperty.call(body, 'description') ? body.description : undefined,
      location: Object.prototype.hasOwnProperty.call(body, 'location') ? body.location : undefined,
      start: eventCopy(body.start),
      end: eventCopy(body.end),
      extendedProperties: eventCopy(body.extendedProperties || {private: {}}),
    };
  }

  function fetch(urlText, requestOptions) {
    const url = new URL(urlText);
    const method = String(requestOptions.method || 'get').toLowerCase();
    const request = {
      method,
      url: urlText,
      path: url.pathname,
      query: Object.fromEntries(url.searchParams.entries()),
      headers: {...(requestOptions.headers || {})},
      body: requestOptions.payload ? JSON.parse(requestOptions.payload) : null,
    };
    requests.push(request);

    if (options.authorizationFailure) return response(403, {error: {message: 'forbidden'}});

    const parts = url.pathname.split('/').filter(Boolean);
    const eventsIndex = parts.indexOf('events');
    if (eventsIndex === -1) return response(404, {error: {message: 'not found'}});
    const eventId = parts.length > eventsIndex + 1 ? decodeURIComponent(parts[eventsIndex + 1]) : null;

    if (method === 'get' && eventId === null) {
      const constraint = url.searchParams.get('privateExtendedProperty');
      const [propertyName, propertyValue] = constraint ? constraint.split('=', 2) : [null, null];
      const items = [...events.values()].filter((event) => {
        if (!propertyName) return true;
        const privateProps = event.extendedProperties && event.extendedProperties.private;
        return privateProps && privateProps[propertyName] === propertyValue;
      });
      return response(200, {items: items.slice(0, 2).map(eventCopy)});
    }

    if (method === 'get' && eventId !== null) {
      const current = events.get(eventId);
      return current ? response(200, eventCopy(current)) : response(404, {error: {message: 'missing'}});
    }

    if (method === 'post' && eventId === null) {
      const created = makeEvent(request.body);
      if (options.driftAfterCreate) created.location = 'Provider drift';
      events.set(created.id, created);
      return response(200, eventCopy(created));
    }

    if (method === 'patch' && eventId !== null) {
      const current = events.get(eventId);
      if (!current) return response(404, {error: {message: 'missing'}});
      if (request.headers['If-Match'] !== current.etag) {
        return response(412, {error: {message: 'precondition failed'}});
      }
      const updated = {
        ...current,
        ...eventCopy(request.body),
        id: current.id,
        etag: `"v${nextVersion++}"`,
      };
      if (options.driftAfterPatch) updated.summary = 'Provider drift';
      events.set(eventId, updated);
      return response(200, eventCopy(updated));
    }

    return response(405, {error: {message: 'method not allowed'}});
  }

  const context = {
    console,
    ScriptApp: {
      getOAuthToken() {
        return 'synthetic-oauth-token';
      },
    },
    UrlFetchApp: {fetch},
    Utilities: {
      DigestAlgorithm: {SHA_256: 'SHA_256'},
      Charset: {UTF_8: 'UTF_8'},
      computeDigest(algorithm, text) {
        assert.equal(algorithm, 'SHA_256');
        return [...crypto.createHash('sha256').update(text, 'utf8').digest()].map((value) => (
          value > 127 ? value - 256 : value
        ));
      },
    },
  };
  vm.createContext(context);
  vm.runInContext(SOURCE, context, {filename: 'GoogleCalendarProjection.gs'});

  return {
    context,
    requests,
    events,
    mutate(eventId, patch) {
      const current = events.get(eventId);
      assert.ok(current);
      const changed = {...current, ...eventCopy(patch), etag: `"v${nextVersion++}"`};
      events.set(eventId, changed);
      return changed;
    },
    duplicateProjectionFrom(eventId, duplicateId) {
      const current = events.get(eventId);
      assert.ok(current);
      const duplicate = eventCopy(current);
      duplicate.id = duplicateId;
      duplicate.etag = `"v${nextVersion++}"`;
      events.set(duplicateId, duplicate);
    },
  };
}

function event(overrides = {}) {
  return {
    title: 'Synthetic appointment',
    start_at: '2026-09-10T09:00:00-04:00',
    end_at: '2026-09-10T10:00:00-04:00',
    timezone: 'America/New_York',
    location: 'Synthetic Clinic',
    description: 'Synthetic provider-proof event',
    ...overrides,
  };
}

function upsert(rt, material = event(), options = {}) {
  return rt.context.miraGoogleCalendarUpsertEvent_(
    'mira-dev-calendar',
    'calproj-test-001',
    material,
    options.idempotencyKey || 'provider-key-001',
    Object.prototype.hasOwnProperty.call(options, 'expectedVersion') ? options.expectedVersion : null,
  );
}

test('capability declares stable projection identity, exact readback, and guarded updates', () => {
  const rt = runtime();
  assert.deepEqual(
    JSON.parse(JSON.stringify(rt.context.miraGoogleCalendarCapability_())),
    {
      provider_lane: 'google',
      writable: true,
      exact_readback: true,
      stable_projection_key: true,
      guarded_updates: true,
      provider_version_kind: 'etag',
    },
  );
});

test('create writes one event with private projection metadata then independently reads it back', () => {
  const rt = runtime();
  const result = upsert(rt);

  assert.equal(result.idempotent_replay, false);
  assert.equal(result.event.event_id, 'evt-1');
  assert.equal(result.event.provider_version, '"v1"');
  assert.equal(result.event.projection_key, 'calproj-test-001');
  assert.deepEqual(JSON.parse(JSON.stringify(result.event.event)), event());
  assert.equal(rt.requests.filter((request) => request.method === 'post').length, 1);
  assert.equal(rt.requests.filter((request) => request.method === 'get').length, 2);
  const created = rt.events.get('evt-1');
  assert.equal(created.extendedProperties.private.miraProjectionKey, 'calproj-test-001');
  assert.equal(created.extendedProperties.private.miraIdempotencyKey, 'provider-key-001');
});

test('lost-acknowledgement retry recovers by stable private projection key without duplicate create', () => {
  const rt = runtime();
  const first = upsert(rt);
  const second = upsert(rt);

  assert.equal(second.idempotent_replay, true);
  assert.equal(second.event.event_id, first.event.event_id);
  assert.equal(rt.events.size, 1);
  assert.equal(rt.requests.filter((request) => request.method === 'post').length, 1);
});

test('guarded update uses the exact prior ETag in If-Match and preserves event identity', () => {
  const rt = runtime();
  const first = upsert(rt);
  const second = upsert(rt, event({title: 'Synthetic appointment updated'}), {
    idempotencyKey: 'provider-key-002',
    expectedVersion: first.event.provider_version,
  });

  assert.equal(second.idempotent_replay, false);
  assert.equal(second.event.event_id, first.event.event_id);
  assert.equal(second.event.provider_version, '"v2"');
  assert.equal(second.event.event.title, 'Synthetic appointment updated');
  const patch = rt.requests.find((request) => request.method === 'patch');
  assert.ok(patch);
  assert.equal(patch.headers['If-Match'], '"v1"');
});

test('stale provider ETag fails closed before Calendar mutation', () => {
  const rt = runtime();
  const first = upsert(rt);
  rt.mutate(first.event.event_id, {summary: 'External edit'});
  const writesBefore = rt.requests.filter((request) => ['post', 'patch'].includes(request.method)).length;

  assert.throws(
    () => upsert(rt, event({title: 'Source update'}), {
      idempotencyKey: 'provider-key-002',
      expectedVersion: first.event.provider_version,
    }),
    (error) => error.miraCode === 'conflict',
  );
  const writesAfter = rt.requests.filter((request) => ['post', 'patch'].includes(request.method)).length;
  assert.equal(writesAfter, writesBefore);
});

test('same provider idempotency key with different material is an explicit conflict', () => {
  const rt = runtime();
  upsert(rt);
  assert.throws(
    () => upsert(rt, event({title: 'Different material'})),
    (error) => error.miraCode === 'idempotency_conflict',
  );
  assert.equal(rt.requests.filter((request) => request.method === 'post').length, 1);
});

test('duplicate private projection keys fail closed rather than picking one event', () => {
  const rt = runtime();
  const first = upsert(rt);
  rt.duplicateProjectionFrom(first.event.event_id, 'evt-duplicate');
  assert.throws(
    () => upsert(rt),
    (error) => error.miraCode === 'conflict',
  );
});

test('immediate provider readback drift is rejected', () => {
  const rt = runtime({driftAfterCreate: true});
  assert.throws(
    () => upsert(rt),
    (error) => error.miraCode === 'readback_error',
  );
});

test('provider permission errors are translated without pretending success', () => {
  const rt = runtime({authorizationFailure: true});
  assert.throws(
    () => upsert(rt),
    (error) => error.miraCode === 'authorization_error',
  );
  assert.equal(rt.events.size, 0);
});

test('adapter only writes event endpoints and never creates calendars or attendee notifications', () => {
  const rt = runtime();
  upsert(rt);
  const writes = rt.requests.filter((request) => ['post', 'patch', 'put', 'delete'].includes(request.method));
  assert.ok(writes.length > 0);
  for (const request of writes) {
    assert.match(request.path, /\/calendars\/[^/]+\/events(?:\/[^/]+)?$/);
    assert.equal(request.query.sendUpdates, 'none');
    assert.equal(request.body.attendees, undefined);
    assert.equal(request.body.conferenceData, undefined);
  }
});
