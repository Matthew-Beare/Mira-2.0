/*
 * MIRA Google Calendar projection adapter for the browser-first Personal lane.
 *
 * The default path is deliberately simple for ordinary users: MIRA creates and
 * owns one dedicated secondary Google Calendar after explicit Calendar opt-in.
 * The adapter uses Calendar REST v3 through UrlFetchApp so provider projection
 * can retain private extended properties, exact readback, and If-Match ETags.
 *
 * Calendar creation is also recovery-safe. A local installation UUID is stored
 * before the provider write and stamped into the calendar description. If the
 * create acknowledgement is lost, MIRA can rediscover the one matching calendar
 * through read-only CalendarList access instead of creating a duplicate.
 */

const MIRA_GOOGLE_CALENDAR_API_ROOT_ = 'https://www.googleapis.com/calendar/v3';
const MIRA_GOOGLE_CALENDAR_LANE_ = 'google';
const MIRA_GOOGLE_CALENDAR_NAME_ = 'MIRA';
const MIRA_GOOGLE_CALENDAR_ID_PROPERTY_ = 'MIRA_GOOGLE_CALENDAR_ID';
const MIRA_GOOGLE_CALENDAR_INSTALLATION_PROPERTY_ = 'MIRA_GOOGLE_CALENDAR_INSTALLATION_ID';
const MIRA_GOOGLE_CALENDAR_DESCRIPTION_PREFIX_ = 'Managed by MIRA. Installation: ';
const MIRA_CALENDAR_PROJECTION_PROPERTY_ = 'miraProjectionKey';
const MIRA_CALENDAR_IDEMPOTENCY_PROPERTY_ = 'miraIdempotencyKey';
const MIRA_CALENDAR_REQUEST_HASH_PROPERTY_ = 'miraRequestHash';
const MIRA_CALENDAR_TOKEN_RE_ = /^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/;

function miraGoogleCalendarCapability_() {
  return {
    provider_lane: MIRA_GOOGLE_CALENDAR_LANE_,
    writable: true,
    exact_readback: true,
    stable_projection_key: true,
    guarded_updates: true,
    provider_version_kind: 'etag',
    managed_calendar_bootstrap: true,
  };
}

function miraEnsureGoogleCalendar_() {
  const properties = PropertiesService.getScriptProperties();
  let installationId = properties.getProperty(MIRA_GOOGLE_CALENDAR_INSTALLATION_PROPERTY_);
  if (!installationId) {
    installationId = miraCalendarToken_(Utilities.getUuid(), 'calendar_installation_id');
    properties.setProperty(MIRA_GOOGLE_CALENDAR_INSTALLATION_PROPERTY_, installationId);
  } else {
    installationId = miraCalendarToken_(installationId, 'calendar_installation_id');
  }
  const description = MIRA_GOOGLE_CALENDAR_DESCRIPTION_PREFIX_ + installationId;

  const storedId = properties.getProperty(MIRA_GOOGLE_CALENDAR_ID_PROPERTY_);
  if (storedId) {
    const calendarId = miraCalendarText_(storedId, 'calendar_ref', 500);
    const metadata = miraGoogleCalendarReadCalendarMetadata_(calendarId);
    miraGoogleCalendarVerifyOwnedCalendarMetadata_(metadata, description);
    return {
      calendar_ref: calendarId,
      created: false,
      recovered: false,
    };
  }

  const matches = miraGoogleCalendarFindOwnedCalendars_(description);
  if (matches.length > 1) {
    throw miraCalendarError_(
      'conflict',
      'multiple Google Calendars match this MIRA installation marker'
    );
  }
  if (matches.length === 1) {
    const recoveredId = miraCalendarText_(matches[0].id, 'calendar_ref', 500);
    const recovered = miraGoogleCalendarReadCalendarMetadata_(recoveredId);
    miraGoogleCalendarVerifyOwnedCalendarMetadata_(recovered, description);
    properties.setProperty(MIRA_GOOGLE_CALENDAR_ID_PROPERTY_, recoveredId);
    return {
      calendar_ref: recoveredId,
      created: false,
      recovered: true,
    };
  }

  const createdRaw = miraGoogleCalendarRequest_(
    'post',
    '/calendars',
    {
      summary: MIRA_GOOGLE_CALENDAR_NAME_,
      description: description,
    },
    null
  );
  const createdId = miraCalendarText_(createdRaw.id, 'calendar_ref', 500);
  const created = miraGoogleCalendarReadCalendarMetadata_(createdId);
  miraGoogleCalendarVerifyOwnedCalendarMetadata_(created, description);
  properties.setProperty(MIRA_GOOGLE_CALENDAR_ID_PROPERTY_, createdId);
  return {
    calendar_ref: createdId,
    created: true,
    recovered: false,
  };
}

function miraGoogleCalendarReadCalendarMetadata_(calendarRef) {
  const calendar = miraCalendarText_(calendarRef, 'calendar_ref', 500);
  const raw = miraGoogleCalendarRequest_(
    'get',
    '/calendars/' + encodeURIComponent(calendar),
    null,
    null
  );
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
    throw miraCalendarError_('readback_error', 'Google Calendar metadata response is malformed');
  }
  return raw;
}

function miraGoogleCalendarVerifyOwnedCalendarMetadata_(raw, expectedDescription) {
  if (raw.summary !== MIRA_GOOGLE_CALENDAR_NAME_) {
    throw miraCalendarError_('conflict', 'stored MIRA Calendar was renamed or points to the wrong calendar');
  }
  if (raw.description !== expectedDescription) {
    throw miraCalendarError_('conflict', 'stored MIRA Calendar ownership marker does not match this installation');
  }
}

function miraGoogleCalendarFindOwnedCalendars_(description) {
  const expectedDescription = miraCalendarText_(description, 'calendar_description', 1000);
  const matches = [];
  let pageToken = null;
  do {
    let path = '/users/me/calendarList?maxResults=250';
    if (pageToken) path += '&pageToken=' + encodeURIComponent(pageToken);
    const raw = miraGoogleCalendarRequest_('get', path, null, null);
    const items = Array.isArray(raw.items) ? raw.items : [];
    items.forEach(function (item) {
      if (
        item &&
        item.summary === MIRA_GOOGLE_CALENDAR_NAME_ &&
        item.description === expectedDescription
      ) {
        matches.push({id: miraCalendarText_(item.id, 'calendar_ref', 500)});
      }
    });
    if (matches.length > 1) break;
    pageToken = typeof raw.nextPageToken === 'string' && raw.nextPageToken
      ? raw.nextPageToken
      : null;
  } while (pageToken);
  return matches;
}

function miraGoogleCalendarUpsertEvent_(
  calendarRef,
  projectionKey,
  eventMaterial,
  idempotencyKey,
  expectedProviderVersion
) {
  const calendar = miraCalendarText_(calendarRef, 'calendar_ref', 500);
  const projection = miraCalendarToken_(projectionKey, 'projection_key');
  const idempotency = miraCalendarToken_(idempotencyKey, 'idempotency_key');
  const expectedEtag = miraCalendarOptionalVersion_(expectedProviderVersion);
  const desired = miraCalendarEventMaterial_(eventMaterial);
  const requestHash = miraCalendarSha256_(miraCalendarCanonicalJson_({
    calendar_ref: calendar,
    projection_key: projection,
    event: desired,
    expected_provider_version: expectedEtag,
  }));

  const matches = miraGoogleCalendarFindByProjectionKey_(calendar, projection);
  if (matches.length > 1) {
    throw miraCalendarError_('conflict', 'multiple Google Calendar events share one MIRA projection key');
  }

  let current = null;
  if (matches.length === 1) {
    current = miraGoogleCalendarReadEvent_(calendar, matches[0].id);
    const privateProps = miraGoogleCalendarPrivateProperties_(current.raw);
    if (
      privateProps[MIRA_CALENDAR_IDEMPOTENCY_PROPERTY_] === idempotency &&
      privateProps[MIRA_CALENDAR_REQUEST_HASH_PROPERTY_] !== requestHash
    ) {
      throw miraCalendarError_('idempotency_conflict', 'Google Calendar idempotency key was reused for different material');
    }
  }

  if (expectedEtag === null) {
    if (current !== null) {
      if (!miraCalendarMaterialMatches_(current.event, desired)) {
        throw miraCalendarError_('conflict', 'stable Google Calendar projection key already exists with different material');
      }
      return miraGoogleCalendarResult_(current, true);
    }

    const body = miraGoogleCalendarEventBody_(projection, idempotency, requestHash, desired);
    const createdRaw = miraGoogleCalendarRequest_(
      'post',
      '/calendars/' + encodeURIComponent(calendar) + '/events?sendUpdates=none',
      body,
      null
    );
    const created = miraGoogleCalendarReadEvent_(calendar, miraCalendarToken_(createdRaw.id, 'provider_event_id'));
    miraGoogleCalendarVerifyReadback_(created, projection, desired, idempotency, requestHash);
    return miraGoogleCalendarResult_(created, false);
  }

  if (current === null) {
    throw miraCalendarError_('conflict', 'expected Google Calendar provider event is missing');
  }
  if (current.provider_version !== expectedEtag) {
    throw miraCalendarError_('conflict', 'Google Calendar provider ETag precondition is stale');
  }
  if (miraCalendarMaterialMatches_(current.event, desired)) {
    return miraGoogleCalendarResult_(current, false);
  }

  const updateBody = miraGoogleCalendarEventBody_(projection, idempotency, requestHash, desired);
  const updatedRaw = miraGoogleCalendarRequest_(
    'patch',
    '/calendars/' + encodeURIComponent(calendar) + '/events/' +
      encodeURIComponent(current.event_id) + '?sendUpdates=none',
    updateBody,
    {'If-Match': expectedEtag}
  );
  const updated = miraGoogleCalendarReadEvent_(calendar, miraCalendarToken_(updatedRaw.id, 'provider_event_id'));
  miraGoogleCalendarVerifyReadback_(updated, projection, desired, idempotency, requestHash);
  return miraGoogleCalendarResult_(updated, false);
}

function miraGoogleCalendarReadEvent_(calendarRef, eventId) {
  const calendar = miraCalendarText_(calendarRef, 'calendar_ref', 500);
  const event = miraCalendarToken_(eventId, 'provider_event_id');
  const raw = miraGoogleCalendarRequest_(
    'get',
    '/calendars/' + encodeURIComponent(calendar) + '/events/' + encodeURIComponent(event),
    null,
    null
  );
  return miraGoogleCalendarProviderEvent_(calendar, raw);
}

function miraGoogleCalendarFindByProjectionKey_(calendarRef, projectionKey) {
  const calendar = miraCalendarText_(calendarRef, 'calendar_ref', 500);
  const projection = miraCalendarToken_(projectionKey, 'projection_key');
  const constraint = MIRA_CALENDAR_PROJECTION_PROPERTY_ + '=' + projection;
  const raw = miraGoogleCalendarRequest_(
    'get',
    '/calendars/' + encodeURIComponent(calendar) + '/events' +
      '?maxResults=2&showDeleted=false&privateExtendedProperty=' + encodeURIComponent(constraint),
    null,
    null
  );
  const items = Array.isArray(raw.items) ? raw.items : [];
  return items.map(function (item) {
    return {id: miraCalendarToken_(item.id, 'provider_event_id')};
  });
}

function miraGoogleCalendarVerifyReadback_(provider, projectionKey, desired, idempotencyKey, requestHash) {
  if (provider.provider_lane !== MIRA_GOOGLE_CALENDAR_LANE_) {
    throw miraCalendarError_('readback_error', 'Google Calendar readback lane mismatch');
  }
  if (provider.projection_key !== projectionKey) {
    throw miraCalendarError_('readback_error', 'Google Calendar projection key readback mismatch');
  }
  if (!miraCalendarMaterialMatches_(provider.event, desired)) {
    throw miraCalendarError_('readback_error', 'Google Calendar event readback differs from desired material');
  }
  const privateProps = miraGoogleCalendarPrivateProperties_(provider.raw);
  if (privateProps[MIRA_CALENDAR_IDEMPOTENCY_PROPERTY_] !== idempotencyKey) {
    throw miraCalendarError_('readback_error', 'Google Calendar idempotency readback mismatch');
  }
  if (privateProps[MIRA_CALENDAR_REQUEST_HASH_PROPERTY_] !== requestHash) {
    throw miraCalendarError_('readback_error', 'Google Calendar request-hash readback mismatch');
  }
}

function miraGoogleCalendarProviderEvent_(calendarRef, raw) {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
    throw miraCalendarError_('readback_error', 'Google Calendar event response is malformed');
  }
  const eventId = miraCalendarToken_(raw.id, 'provider_event_id');
  const etag = miraCalendarVersion_(raw.etag, 'provider_version');
  const privateProps = miraGoogleCalendarPrivateProperties_(raw);
  const projectionKey = miraCalendarToken_(
    privateProps[MIRA_CALENDAR_PROJECTION_PROPERTY_],
    'projection_key'
  );
  const event = miraCalendarEventMaterial_({
    title: raw.summary,
    start_at: raw.start && raw.start.dateTime,
    end_at: raw.end && raw.end.dateTime,
    timezone: raw.start && raw.start.timeZone,
    location: Object.prototype.hasOwnProperty.call(raw, 'location') ? raw.location : null,
    description: Object.prototype.hasOwnProperty.call(raw, 'description') ? raw.description : null,
  });
  if (!raw.end || raw.end.timeZone !== event.timezone) {
    throw miraCalendarError_('readback_error', 'Google Calendar end timezone readback mismatch');
  }
  return {
    provider_lane: MIRA_GOOGLE_CALENDAR_LANE_,
    calendar_ref: calendarRef,
    event_id: eventId,
    provider_version: etag,
    projection_key: projectionKey,
    event: event,
    raw: raw,
  };
}

function miraGoogleCalendarEventBody_(projectionKey, idempotencyKey, requestHash, event) {
  const body = {
    summary: event.title,
    start: {dateTime: event.start_at, timeZone: event.timezone},
    end: {dateTime: event.end_at, timeZone: event.timezone},
    extendedProperties: {private: {}},
  };
  body.extendedProperties.private[MIRA_CALENDAR_PROJECTION_PROPERTY_] = projectionKey;
  body.extendedProperties.private[MIRA_CALENDAR_IDEMPOTENCY_PROPERTY_] = idempotencyKey;
  body.extendedProperties.private[MIRA_CALENDAR_REQUEST_HASH_PROPERTY_] = requestHash;
  body.location = event.location;
  body.description = event.description;
  return body;
}

function miraGoogleCalendarPrivateProperties_(raw) {
  const extended = raw && raw.extendedProperties;
  const privateProps = extended && extended.private;
  return privateProps && typeof privateProps === 'object' && !Array.isArray(privateProps)
    ? privateProps
    : {};
}

function miraGoogleCalendarRequest_(method, path, body, extraHeaders) {
  const headers = Object.assign(
    {Authorization: 'Bearer ' + ScriptApp.getOAuthToken()},
    extraHeaders || {}
  );
  const options = {
    method: method,
    headers: headers,
    muteHttpExceptions: true,
  };
  if (body !== null && body !== undefined) {
    options.contentType = 'application/json; charset=utf-8';
    options.payload = JSON.stringify(body);
  }
  const response = UrlFetchApp.fetch(MIRA_GOOGLE_CALENDAR_API_ROOT_ + path, options);
  const status = response.getResponseCode();
  const text = response.getContentText() || '';
  let parsed = {};
  if (text) {
    try {
      parsed = JSON.parse(text);
    } catch (error) {
      throw miraCalendarError_('provider_error', 'Google Calendar returned non-JSON response');
    }
  }
  if (status >= 200 && status < 300) return parsed;
  if (status === 404) throw miraCalendarError_('not_found', 'Google Calendar resource was not found');
  if (status === 409 || status === 412) {
    throw miraCalendarError_('conflict', 'Google Calendar provider precondition/conflict failed');
  }
  if (status === 401 || status === 403) {
    throw miraCalendarError_('authorization_error', 'Google Calendar authorization or permission failed');
  }
  throw miraCalendarError_('provider_error', 'Google Calendar provider request failed with HTTP ' + status);
}

function miraCalendarEventMaterial_(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw miraCalendarError_('validation_error', 'calendar event material must be an object');
  }
  const title = miraCalendarText_(value.title, 'event.title', 500);
  const startAt = miraCalendarTimestamp_(value.start_at, 'event.start_at');
  const endAt = miraCalendarTimestamp_(value.end_at, 'event.end_at');
  if (Date.parse(endAt) <= Date.parse(startAt)) {
    throw miraCalendarError_('validation_error', 'event.end_at must be later than event.start_at');
  }
  const timezone = miraCalendarText_(value.timezone, 'event.timezone', 128);
  return {
    title: title,
    start_at: startAt,
    end_at: endAt,
    timezone: timezone,
    location: miraCalendarOptionalText_(value.location, 'event.location', 1000),
    description: miraCalendarOptionalText_(value.description, 'event.description', 4000),
  };
}

function miraCalendarMaterialMatches_(left, right) {
  return (
    left.title === right.title &&
    Date.parse(left.start_at) === Date.parse(right.start_at) &&
    Date.parse(left.end_at) === Date.parse(right.end_at) &&
    left.timezone === right.timezone &&
    left.location === right.location &&
    left.description === right.description
  );
}

function miraCalendarTimestamp_(value, field) {
  const text = miraCalendarText_(value, field, 128);
  if (!/(Z|[+-]\d{2}:\d{2})$/.test(text) || Number.isNaN(Date.parse(text))) {
    throw miraCalendarError_('validation_error', field + ' must be RFC3339 with an explicit offset');
  }
  return text;
}

function miraCalendarToken_(value, field) {
  if (typeof value !== 'string') {
    throw miraCalendarError_('validation_error', field + ' must be text');
  }
  const normalized = value.trim();
  if (!MIRA_CALENDAR_TOKEN_RE_.test(normalized)) {
    throw miraCalendarError_('validation_error', field + ' must be a safe token of 1-128 characters');
  }
  return normalized;
}

function miraCalendarText_(value, field, maximum) {
  if (typeof value !== 'string') {
    throw miraCalendarError_('validation_error', field + ' must be text');
  }
  const normalized = value.replace(/\s+/g, ' ').trim();
  if (!normalized) throw miraCalendarError_('validation_error', field + ' must be non-empty');
  if (normalized.length > maximum) {
    throw miraCalendarError_('validation_error', field + ' is too long');
  }
  return normalized;
}

function miraCalendarOptionalText_(value, field, maximum) {
  if (value === null || value === undefined || value === '') return null;
  return miraCalendarText_(value, field, maximum);
}

function miraCalendarVersion_(value, field) {
  if (typeof value !== 'string' || !value.trim()) {
    throw miraCalendarError_('readback_error', field + ' must be a non-empty opaque token');
  }
  if (value.length > 1024) throw miraCalendarError_('readback_error', field + ' is too long');
  return value.trim();
}

function miraCalendarOptionalVersion_(value) {
  if (value === null || value === undefined) return null;
  return miraCalendarVersion_(value, 'expected_provider_version');
}

function miraCalendarCanonicalJson_(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) {
    return '[' + value.map(miraCalendarCanonicalJson_).join(',') + ']';
  }
  const keys = Object.keys(value).sort();
  return '{' + keys.map(function (key) {
    return JSON.stringify(key) + ':' + miraCalendarCanonicalJson_(value[key]);
  }).join(',') + '}';
}

function miraCalendarSha256_(text) {
  const bytes = Utilities.computeDigest(
    Utilities.DigestAlgorithm.SHA_256,
    text,
    Utilities.Charset.UTF_8
  );
  return bytes.map(function (value) {
    const unsigned = value < 0 ? value + 256 : value;
    return ('0' + unsigned.toString(16)).slice(-2);
  }).join('');
}

function miraGoogleCalendarResult_(provider, replay) {
  return {
    event: {
      provider_lane: provider.provider_lane,
      calendar_ref: provider.calendar_ref,
      event_id: provider.event_id,
      provider_version: provider.provider_version,
      projection_key: provider.projection_key,
      event: provider.event,
    },
    idempotent_replay: Boolean(replay),
  };
}

function miraCalendarError_(code, message) {
  const error = new Error(message);
  error.miraCode = code;
  return error;
}
