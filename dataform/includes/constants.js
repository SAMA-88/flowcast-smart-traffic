// Shared constants for all SQLX files. Use as ${constants.LOCAL_TZ}.
const LOCAL_TZ = "Africa/Cairo";

// First collected slot (UTC). Set on D1 after the first successful run.
const COLLECTION_START = "2026-01-01 00:00:00+00";

// Congestion class thresholds on congestion_ratio. DA1 owns these (D2).
const CLASS_THRESHOLDS = { low: 0.75, medium: 0.5 };

module.exports = { LOCAL_TZ, COLLECTION_START, CLASS_THRESHOLDS };
