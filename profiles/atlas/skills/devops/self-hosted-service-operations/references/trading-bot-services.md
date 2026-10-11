# Trading Bot Service Deployments

Deployment depth for OctoBot, NoFx AI Trading OS, and Hummingbot/Condor. The general operating loop lives in SKILL.md; apply it here.

## OctoBot (Docker)

- Official stable v3 compose maps the web UI on internal port `5001`. Standalone bot mode: `command: ["--standalone"]` and map `127.0.0.1:<host>:5001`. Node distribution mode: `args.no_web = True`, Uvicorn Node API on internal port `8000`.
- Web UI activation: `"WebInterface": true` and `"WebService": true` under `tentacle_activation.Services` in `/opt/octobot/user/profiles/<profile_id>/tentacles_config.json` — otherwise the boot log says `Web interface disabled`.
- Strategy config files (e.g. `specific_config/SimpleStrategyEvaluator.json`) must include `"required_time_frames": ["1h"]` — startup fails with `'required_time_frames' is missing in configuration file` otherwise.
- LLM service key must be capitalized `"GPT"` under `services` in `/octobot/user/config.json` (lowercase `"gpt"` makes `_get_api_key()` return `None` because `LLMService.get_type()` returns `'GPT'`). `chmod 600` the file after writing keys.
- Custom LLM routing from inside Docker: add `extra_hosts: ["host.docker.internal:host-gateway"]` to compose and point `llm-custom-base-url` at `http://host.docker.internal:<port>/v1`.
- Paper-trading safeguard: `"trader": {"enabled": true, "simulator": {"enabled": true}}` and no real exchange API credentials during setup.
- The web UI redirects `/` to `/terms` (302) or `/app` (307) — probe with `curl -sL`, not plain `curl -I`.
- GPTEvaluator parses prediction strings like `Predict: up 53%` into direction (`-1` UP / `1` DOWN), confidence (`53.0%`), and `eval_note` (`-0.53`).

## NoFx AI Trading OS (purge & reinstall)

1. Inspect before removing: `docker ps -a | grep <name>`, `docker images | grep <name>`, volumes, and `find /root /mnt -maxdepth 3 -iname "*<name>*"`.
2. Sequential removal: `docker rm -f <containers>` → `docker rmi -f <images>` → `rm -rf /mnt/<service-dir>`.
3. Installer scripts default to `$HOME` — pass the target path explicitly (`bash -s -- /mnt/nofx`) to protect the root partition.
4. Ports: `3000` web UI, `8080` backend API. Update BOTH ingress entries when re-pointing (app domain → 3000, API domain → 8080).
5. The web UI `/data` tab depends on internal `/api/vergex/*` backend routes — a wrong/unmapped proxy port shows connection-refused or 502 in the UI.
6. Adding OpenAI-compatible models: insert into `/mnt/nofx/data/data.db` → `ai_models` with `provider='openai'`, `custom_api_url`, `custom_model_name`, `enabled=1`. The `api_key` MUST be AES-GCM encrypted as `ENC:v1:<b64(12-byte nonce)>:<b64(ciphertext)>` using `DATA_ENCRYPTION_KEY` from the container env (`docker exec nofx-trading env`). Restart the container afterwards.
7. Verify: `docker ps`, `curl -s http://localhost:8080/api/health`, `curl -s -I http://localhost:3000`.

## Hummingbot API & Condor

- Stack: `postgres:16` + EMQX MQTT broker. If host 5432 is already bound (e.g. Firecrawl), map `5433:5432`; map API `8010:8000`.
- Condor `config.yml` `servers.<name>` entries MUST explicitly include `host`, `port`, `url`, `username`, `password` — `url` alone raises `KeyError: 'host'` when `mcp-hummingbot` initializes.
- Condor `.env`: set `WEB_PORT` explicitly (a `WEB_URL` alone can default the port to 443), and set `CONDOR_DEFAULT_AGENT` to a saved endpoint name to avoid `No saved endpoint named ...` fallback errors.
- Before pointing tunnel ingress at a local port, run `ss -tlpn` — a port already held by Nginx serves the Nginx default page on the new domain (move to a free port instead).
