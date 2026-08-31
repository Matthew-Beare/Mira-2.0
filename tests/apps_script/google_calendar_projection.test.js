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
  const calendars = new Map();
  const properties = new Map();
  const requests = [];
  let nextId = 1;
  let nextVersion = 1;
  let nextCalendarId = 1;

  function copy(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function makeEvent(calendarId, body, id = `evt-${nextId++}`) {
    return {
      kind: 'calendar#event',
      id,
      calendarId,
      etag: `"v${nextVersion++}"`,
      summary: body.summary,
      description: Object.prototype.hasOwnProperty.call(body, 'description') ? body.description : undefined,
      location: Object.prototype.hasOwnProperty.call(body, 'location') ? body.location : undefined,
      start: copy(body.start),
      end: copy(body.end),
      extendedProperties: copy(body.extendedProperties || {private: {}}),
    };
  }

  function makeCalendar(body, id = `mira-${nextCalendarId++}@group.calendar.google.com`) {
    return {
      kind: 'calendar#calendar',
      id,
      summary: body.summary,
      description: body.description,
      timeZone: body.timeZone || 'Etc/UTC',
    };
  }

  function eventKey(calendarId, eventId) {
    return `${calendarId}|${eventId}`;
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
    const calendarListIndex = parts.indexOf('calendarList');
    if (calendarListIndex !== -1 && method === 'get') {
      const items = [...calendars.values()].map((calendar) => ({
        id: calendar.id,
        summary: calendar.summary,
        description: calendar.description,
      }));
      return response(200, {items: items.map(copy)});
    }

    const calendarsIndex = parts.indexOf('calendars');
    if (calendarsIndex === -1) return response(404, {error: {message: 'not found'}});
    const calendarId = parts.length > calendarsIndex + 1
      ? decodeURIComponent(parts[calendarsIndex + 1])
      : null;
    const eventsIndex = parts.indexOf('events');

    if (calendarId === null && eventsIndex === -1 && method === 'post') {
      const created = makeCalendar(request.body || {});
      calendars.set(created.id, created);
      return response(200, copy(created));
    }

    if (calendarId !== null && eventsIndex === -1 && method === 'get') {
      const current = calendars.get(calendarId);
      return current ? response(200, copy(current)) : response(404, {error: {message: 'missing'}});
    }

    if (eventsIndex === -1) return response(405, {error: {message: 'method not allowed'}});
    const eventId = parts.length > eventsIndex + 1 ? decodeURIComponent(parts[eventsIndex + 1]) : null;

    if (method === 'get' && eventId === null) {
      const constraint = url.searchParams.get('privateExtendedProperty');
      const [propertyName, propertyValue] = constraint ? constraint.split('=', 2) : [null, null];
      const items = [...events.values()].filter((event) => {
        if (event.calendarId !== calendarId) return false;
        if (!propertyName) return true;
        const privateProps = event.extendedProperties && event.extendedProperties.private;
        return privateProps && privateProps[propertyName] === propertyValue;
      });
      return response(200, {items: items.slice(0, 2).map(copy)});
    }

    if (method === 'get' && eventId !== null) {
      const current = events.get(eventKey(calendarId, eventId));
      return current ? response(200, copy(current)) : response(404, {error: {message: 'missing'}});
    }

    if (method === 'post' && eventId === null) {
      const created = makeEvent(calendarId, request.body);
      if (options.driftAfterCreate) created.location = 'Provider drift';
      events.set(eventKey(calendarId, created.id), created);
      return response(200, copy(created));
    }

    if (method === 'patch' && eventId !== null) {
      const key = eventKey(calendarId, eventId);
      const current = events.get(key);
      if (!current) return response(404, {error: {message: 'missing'}});
      if (request.headers['If-Match'] !== current.etag) {
        return response(412, {error: {message: 'precondition failed'}});
      }
      const updated = {
        ...current,
        ...copy(request.body),
        id: current.id,
        calendarId,
        etag: `"v${nextVersion++}"`,
      };
      if (options.driftAfterPatch) updated.summary = 'Provider drift';
      events.set(key, updated);
      return response(200, copy(updated));
    }

    return response(405, {error: {message: 'method not allowed'}});
  }

  const context = {
    console,
    PropertiesService: {
      getScriptProperties() {
        return {
          getProperty(key) {
            return properties.has(key) ? properties.get(key) : null;
          },
          setProperty(key, value) {
            properties.set(key, String(value));
            return this;
          },
          deleteProperty(key) {
            properties.delete(key);
            return this;
          },
        };
      },
    },
    ScriptApp: {
      getOAuthToken() {
        return 'synthetic-oauth-token';
      },
    },
    UrlFetchApp: {fetch},
    Utilities: {
      DigestAlgorithm: {SHA_256: 'SHA_256'},
      Charset: {UTF_8: 'UTF_8'},
      getUuid() {
        return '11111111-2222-3333-4444-555555555555';
      },
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
    calendars,
    properties,
    mutate(calendarId, eventId, patch) {
      const key = eventKey(calendarId, eventId);
      const current = events.get(key);
      assert.ok(current);
      const changed = {...current, ...copy(patch), etag: `"v${nextVersion++}"`};
      events.set(key, changed);
      return changed;
    },
    duplicateProjectionFrom(calendarId, eventId, duplicateId) {
      const current = events.get(eventKey(calendarId, eventId));
      assert.ok(current);
      const duplicate = copy(current);
      duplicate.id = duplicateId;
      duplicate.etag = `"v${nextVersion++}"`;
      events.set(eventKey(calendarId, duplicateId), duplicate);
    },
    clearManagedCalendarId() {
      properties.delete('MIRA_GOOGLE_CALENDAR_ID');
    },
    duplicateManagedCalendar() {
      const existing = [...calendars.values()].find((calendar) => calendar.summary === 'MIRA');
      assert.ok(existing);
      const duplicate = makeCalendar(existing);
      calendars.set(duplicate.id, duplicate);
      return duplicate;
    },
    deleteManagedCalendar() {
      const id = properties.get('MIRA_GOOGLE_CALENDAR_ID');
      assert.ok(id);
      calendars.delete(id);
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
    options.calendarRef || 'mira-dev-calendar',
    'calproj-test-001',
    material,
    options.idempotencyKey || 'provider-key-001',
    Object.prototype.hasOwnProperty.call(options, 'expectedVersion') ? options.expectedVersion : null,
  );
}

test('capability declares managed Calendar bootstrap, stable projection identity, exact readback, and guarded updates', () => {
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
      managed_calendar_bootstrap: true,
    },
  );
});

test('one-click bootstrap creates one dedicated MIRA Calendar and persists its provider ID', () => {
  const rt = runtime();
  const result = rt.context.miraEnsureGoogleCalendar_();

  assert.equal(result.created, true);
  assert.equal(result.recovered, false);
  assert.match(result.calendar_ref, /^mira-1@group\.calendar\.google\.com$/);
  assert.equal(rt.calendars.size, 1);
  const calendar = rt.calendars.get(result.calendar_ref);
  assert.equal(calendar.summary, 'MIRA');
  assert.equal(
    calendar.description,
    'Managed by MIRA. Installation: 11111111-2222-3333-4444-555555555555',
  );
  assert.equal(rt.properties.get('MIRA_GOOGLE_CALENDAR_ID'), result.calendar_ref);
  assert.equal(
    rt.properties.get('MIRA_GOOGLE_CALENDAR_INSTALLATION_ID'),
    '11111111-2222-3333-4444-555555555555',
  );
  assert.equal(
    rt.requests.filter((request) => request.method === 'post' && request.path.endsWith('/calendars')).length,
    1,
  );
});

test('repeat bootstrap performs no duplicate calendar creation', () => {
  const rt = runtime();
  const first = rt.context.miraEnsureGoogleCalendar_();
  const second = rt.context.miraEnsureGoogleCalendar_();

  assert.equal(second.calendar_ref, first.calendar_ref);
  assert.equal(second.created, false);
  assert.equal(second.recovered, false);
  assert.equal(rt.calendars.size, 1);
  assert.equal(
    rt.requests.filter((request) => request.method === 'post' && request.path.endsWith('/calendars')).length,
    1,
  );
});

test('lost calendar-create acknowledgement is recovered by installation marker without duplicate creation', () => {
  const rt = runtime();
  const first = rt.context.miraEnsureGoogleCalendar_();
  rt.clearManagedCalendarId();

  const recovered = rt.context.miraEnsureGoogleCalendar_();
  assert.equal(recovered.calendar_ref, first.calendar_ref);
  assert.equal(recovered.created, false);
  assert.equal(recovered.recovered, true);
  assert.equal(rt.calendars.size, 1);
  assert.equal(rt.properties.get('MIRA_GOOGLE_CALENDAR_ID'), first.calendar_ref);
  assert.equal(
    rt.requests.filter((request) => request.method === 'post' && request.path.endsWith('/calendars')).length,
    1,
  );
});

test('ambiguous managed calendar ownership markers fail closed', () => {
  const rt = runtime();
  rt.context.miraEnsureGoogleCalendar_();
  rt.clearManagedCalendarId();
  rt.duplicateManagedCalendar();

  assert.throws(
    () => rt.context.miraEnsureGoogleCalendar_(),
    (error) => error.miraCode === 'conflict',
  );
});

test('explicitly missing stored managed calendar fails closed instead of silently recreating it', () => {
  const rt = runtime();
  rt.context.miraEnsureGoogleCalendar_();
  rt.deleteManagedCalendar();

  assert.throws(
    () => rt.context.miraEnsureGoogleCalendar_(),
    (error) => error.miraCode === 'not_found',
  );
  assert.equal(rt.calendars.size, 0);
  assert.equal(
    rt.requests.filter((request) => request.method === 'post' && request.path.endsWith('/calendars')).length,
    1,
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
  assert.equal(rt.requests.filter((request) => request.method === 'post' && request.path.includes('/events')).length, 1);
  assert.equal(rt.requests.filter((request) => request.method === 'get' && request.path.includes('/events')).length, 2);
  const created = [...rt.events.values()][0];
  assert.equal(created.extendedProperties.private.miraProjectionKey, 'calproj-test-001');
  assert.equal(created.extendedProperties.private.miraIdempotencyKey, 'provider-key-001');
});

test('lost-acknowledgement retry recovers by stable private projection key without duplicate event create', () => {
  const rt = runtime();
  const first = upsert(rt);
  const second = upsert(rt);

  assert.equal(second.idempotent_replay, true);
  assert.equal(second.event.event_id, first.event.event_id);
  assert.equal(rt.events.size, 1);
  assert.equal(rt.requests.filter((request) => request.method === 'post' && request.path.includes('/events')).length, 1);
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
  rt.mutate('mira-dev-calendar', first.event.event_id, {summary: 'External edit'});
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
  assert.equal(rt.requests.filter((request) => request.method === 'post' && request.path.includes('/events')).length, 1);
});

test('duplicate private projection keys fail closed rather than picking one event', () => {
  const rt = runtime();
  const first = upsert(rt);
  rt.duplicateProjectionFrom('mira-dev-calendar', first.event.event_id, 'evt-duplicate');
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
    () => rt.context.miraEnsureGoogleCalendar_(),
    (error) => error.miraCode === 'authorization_error',
  );
  assert.equal(rt.calendars.size, 0);
});

test('event mutation never adds attendees, Meet links, or attendee notifications', () => {
  const rt = runtime();
  upsert(rt);
  const writes = rt.requests.filter((request) => (
    ['post', 'patch'].includes(request.method) && request.path.includes('/events')
  ));
  assert.ok(writes.length > 0);
  for (const request of writes) {
    assert.match(request.path, /\/calendars\/[^/]+\/events(?:\/[^/]+)?$/);
    assert.equal(request.query.sendUpdates, 'none');
    assert.equal(request.body.attendees, undefined);
    assert.equal(request.body.conferenceData, undefined);
  }
});
