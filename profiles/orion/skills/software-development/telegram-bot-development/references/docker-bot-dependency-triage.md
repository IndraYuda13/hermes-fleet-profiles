# Dockerized Telegram Bot Outage & Dependency Triage

## Context & Symptoms
In multi-container Telegram bot setups (e.g. `jualubot-platform`), bots frequently separate concerns into distinct containers:
- `bot`: Polling listener (Aiogram / Pyrogram).
- `api`: Fast/Uvicorn HTTP API and webhooks.
- `worker`: Celery / Telethon background async task execution.
- `scheduler`: Periodic job loop.
- `mysql` / `redis`: Backing datastores.

### Common Failure Mode: Silent Dead Bot with Running Container
1. Backing datastore container (MySQL/Redis) is killed, stopped, or recreated.
2. `docker ps` reports `bot` status as `Up (hours)` because the main process hasn't exited.
3. However, the bot is stuck in a silent connection failure loop (e.g. `OperationalError: Can't connect to MySQL server on 'mysql'`, `Cannot connect to redis://redis:6379/0`).
4. Updates from Telegram are completely ignored because the event loop/dispatcher crashed or is blocked trying to acquire connections.

## Resolution Workflow
1. **Find Project Root & Compose Config:**
   ```bash
   docker inspect <container_name> | jq '.[0].Config.Labels["com.docker.compose.project.working_dir"]'
   ```
2. **Inspect All Stack Services:**
   ```bash
   cd <project_dir>
   docker compose ps -a
   ```
3. **Bring Up Missing/Unhealthy Dependencies:**
   ```bash
   docker compose up -d mysql redis
   # Wait for healthchecks to become healthy
   ```
4. **Restart Dependent Application Services:**
   ```bash
   docker compose restart bot api worker scheduler
   ```
5. **Verify Bot Polling & Health Endpoint:**
   ```bash
   docker logs --tail 30 <bot_container>
   # Look for: "Run polling for bot @<BotUsername>"
   curl -s http://127.0.0.1:<port>/health
   ```
