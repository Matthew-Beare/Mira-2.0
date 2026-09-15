package com.mira.client.core.sync;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.regex.Pattern;

/**
 * Read-only bounded query over the verified canonical Changes projection.
 *
 * <p>This surface deliberately owns no local cursor, command queue, provider identity, or mutation
 * path. It starts from the beginning of the verified change stream, folds the latest revision for
 * one data class in memory, and returns a result only after the remote projection is exhausted.
 * It never calls {@link ReconnectCoordinator.Transport#reconcileCommand} and therefore cannot
 * submit or acknowledge a canonical mutation as a side effect of a passive capture/read.</p>
 *
 * <p>The Workspace worker reconciles current canonical Resources into Changes before processing
 * queued commands, so this projection includes pre-Android canonical state as well as later
 * verified readback revisions. Changes remain transport evidence; every accepted page must assert
 * verified canonical readback.</p>
 */
public final class VerifiedChangeQuery {
    private static final Pattern DATA_CLASS_PATTERN =
            Pattern.compile("^[A-Za-z0-9][A-Za-z0-9._:-]{0,95}$");
    private static final int DEFAULT_PAGE_SIZE = 128;
    private static final int MAX_PAGE_SIZE = 128;
    private static final int MAX_PAGES = 128;

    private final ReconnectCoordinator.Transport transport;

    public VerifiedChangeQuery(ReconnectCoordinator.Transport transport) {
        this.transport = Objects.requireNonNull(transport, "transport");
    }

    public QueryResult queryLatest(String dataClass) {
        return queryLatest(dataClass, DEFAULT_PAGE_SIZE);
    }

    /**
     * Returns latest verified snapshots for {@code dataClass} only after reaching a terminal page.
     */
    public QueryResult queryLatest(String dataClass, int pageSize) {
        final String wantedClass;
        try {
            wantedClass = validateDataClass(dataClass);
            validatePageSize(pageSize);
        } catch (IllegalArgumentException exc) {
            return QueryResult.localFailure(exc.getMessage());
        }

        String cursor = null;
        Map<String, OfflineSyncStateStore.ResourceSnapshot> latest = new LinkedHashMap<>();

        for (int pageIndex = 0; pageIndex < MAX_PAGES; pageIndex++) {
            final ReconnectCoordinator.ChangePage page;
            try {
                page = transport.readChanges(cursor, pageSize);
            } catch (ReconnectCoordinator.TransportException exc) {
                return QueryResult.transportFailure(exc.code(), exc.getMessage());
            }

            String protocolError = validatePage(cursor, pageSize, page);
            if (protocolError != null) {
                return QueryResult.protocolFailure(protocolError);
            }

            for (OfflineSyncStateStore.ResourceSnapshot snapshot : page.verifiedSnapshots()) {
                if (!wantedClass.equals(snapshot.dataClass())) {
                    continue;
                }
                OfflineSyncStateStore.ResourceSnapshot prior = latest.get(snapshot.resourceId());
                if (prior == null || snapshot.revision() > prior.revision()) {
                    latest.put(snapshot.resourceId(), copy(snapshot));
                    continue;
                }
                if (snapshot.revision() == prior.revision()) {
                    if (!Arrays.equals(snapshot.payload(), prior.payload())) {
                        return QueryResult.protocolFailure(
                                "verified Changes contains a same-revision resource fork"
                        );
                    }
                    continue;
                }
                return QueryResult.protocolFailure(
                        "verified Changes regressed a resource revision"
                );
            }

            cursor = page.nextCursor();
            if (!page.moreAvailable()) {
                ArrayList<OfflineSyncStateStore.ResourceSnapshot> rows =
                        new ArrayList<>(latest.values());
                rows.sort(Comparator.comparing(OfflineSyncStateStore.ResourceSnapshot::resourceId));
                return QueryResult.complete(cursor, rows);
            }
        }

        return QueryResult.protocolFailure(
                "verified Changes exceeds the bounded full-projection page limit"
        );
    }

    private static String validatePage(
            String requestedCursor,
            int requestedLimit,
            ReconnectCoordinator.ChangePage page
    ) {
        if (page == null) {
            return "transport returned null change page";
        }
        if (!Objects.equals(requestedCursor, page.fromCursor())) {
            return "remote change page does not start at the requested cursor";
        }
        if (!page.readbackVerified()) {
            return "remote change page is missing verified canonical readback";
        }
        List<OfflineSyncStateStore.ResourceSnapshot> snapshots = page.verifiedSnapshots();
        if (snapshots.size() > requestedLimit) {
            return "remote change page exceeds requested snapshot limit";
        }
        if (Objects.equals(requestedCursor, page.nextCursor()) && !snapshots.isEmpty()) {
            return "remote change page contains snapshots without cursor progress";
        }
        if (page.moreAvailable() && snapshots.isEmpty()) {
            return "remote change page claims more data without advancing verified snapshots";
        }
        return null;
    }

    private static String validateDataClass(String value) {
        if (value == null || !DATA_CLASS_PATTERN.matcher(value).matches()) {
            throw new IllegalArgumentException("dataClass is invalid");
        }
        return value;
    }

    private static void validatePageSize(int value) {
        if (value < 1 || value > MAX_PAGE_SIZE) {
            throw new IllegalArgumentException("pageSize must be from 1 through " + MAX_PAGE_SIZE);
        }
    }

    private static OfflineSyncStateStore.ResourceSnapshot copy(
            OfflineSyncStateStore.ResourceSnapshot snapshot
    ) {
        return new OfflineSyncStateStore.ResourceSnapshot(
                snapshot.dataClass(),
                snapshot.resourceId(),
                snapshot.revision(),
                snapshot.payload()
        );
    }

    public enum Status {
        COMPLETE,
        TRANSPORT_FAILURE,
        PROTOCOL_FAILURE,
        LOCAL_FAILURE
    }

    /** Immutable bounded query result. */
    public static final class QueryResult {
        private final Status status;
        private final String cursor;
        private final List<OfflineSyncStateStore.ResourceSnapshot> snapshots;
        private final String errorCode;
        private final String message;

        private QueryResult(
                Status status,
                String cursor,
                List<OfflineSyncStateStore.ResourceSnapshot> snapshots,
                String errorCode,
                String message
        ) {
            this.status = Objects.requireNonNull(status, "status");
            this.cursor = cursor;
            this.snapshots = immutableCopies(snapshots);
            this.errorCode = errorCode;
            this.message = message;
        }

        static QueryResult complete(
                String cursor,
                List<OfflineSyncStateStore.ResourceSnapshot> snapshots
        ) {
            return new QueryResult(
                    Status.COMPLETE,
                    requireText(cursor, "cursor"),
                    snapshots,
                    null,
                    null
            );
        }

        static QueryResult transportFailure(String code, String message) {
            return new QueryResult(
                    Status.TRANSPORT_FAILURE,
                    null,
                    Collections.emptyList(),
                    requireText(code, "code"),
                    requireText(message, "message")
            );
        }

        static QueryResult protocolFailure(String message) {
            return new QueryResult(
                    Status.PROTOCOL_FAILURE,
                    null,
                    Collections.emptyList(),
                    "protocol_error",
                    requireText(message, "message")
            );
        }

        static QueryResult localFailure(String message) {
            return new QueryResult(
                    Status.LOCAL_FAILURE,
                    null,
                    Collections.emptyList(),
                    "local_query_error",
                    requireText(message, "message")
            );
        }

        public Status status() {
            return status;
        }

        public String cursor() {
            return cursor;
        }

        public List<OfflineSyncStateStore.ResourceSnapshot> snapshots() {
            return immutableCopies(snapshots);
        }

        public String errorCode() {
            return errorCode;
        }

        public String message() {
            return message;
        }

        private static List<OfflineSyncStateStore.ResourceSnapshot> immutableCopies(
                List<OfflineSyncStateStore.ResourceSnapshot> rows
        ) {
            ArrayList<OfflineSyncStateStore.ResourceSnapshot> copies = new ArrayList<>();
            if (rows != null) {
                for (OfflineSyncStateStore.ResourceSnapshot row : rows) {
                    copies.add(copy(Objects.requireNonNull(row, "snapshot")));
                }
            }
            return Collections.unmodifiableList(copies);
        }

        private static String requireText(String value, String field) {
            if (value == null || value.trim().isEmpty() || !value.equals(value.trim())) {
                throw new IllegalArgumentException(field + " must be non-empty trimmed text");
            }
            return value;
        }
    }
}
