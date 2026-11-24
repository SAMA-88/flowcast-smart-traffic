# alerts

Cloud Run job every 15 minutes (+8 min after the collector). Owner: **DE2** (code) + **DA2** (rules) · Due: **D10**

- Open an alert when `congestion_ratio < 0.5` for 30 minutes (2 slots).
- Keep an `alert_state` table: send once when it opens, once when it resolves. No spam.
- Send a "data is stale" alert when the latest slot is older than 20 minutes.
- Channel: Telegram bot (token in Secret Manager), e-mail as backup.
