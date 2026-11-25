# loader

Container Apps Job with an **event trigger**: it starts when a Service Bus queue has messages
and stops when the queues are empty. It replaces the BigQuery subscription of the GCP design.
Owner: **DE1 + DE2** · Due: **D1**

What one run does:

1. Receive a batch (up to 100) from `traffic-events` and `weather-events`.
2. Validate each body against `infra/schemas/*.schema.json`.
3. `INSERT ... ON CONFLICT (event_id) DO NOTHING` into `raw.traffic_events` / `raw.weather_events`,
   with `message_id` and `enqueued_time` from the message.
4. Complete the messages after the transaction commits. Invalid body = dead-letter it with a reason.
   Database error = abandon it (Service Bus retries, and dead-letters after 5 deliveries).

Auth: managed identity for Service Bus (Data Receiver). Postgres password comes from Key Vault.
