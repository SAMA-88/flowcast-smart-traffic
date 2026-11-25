# api

FastAPI service on Azure Container Apps (external ingress, scales to zero), plus a Leaflet live map
served from the same service. Owner: **DE2** · Due: **D10**

Planned endpoints: `/health`, `/segments/latest`, `/kpis`, `/forecast`, and `/` for the map.
Reads gold tables from PostgreSQL with a read-only role.
Serves derived data only (no raw TomTom values) and shows OpenStreetMap / TomTom attribution.

Scale to zero means the first request after idle takes a few seconds. Set `min_replicas = 1` on demo day.
