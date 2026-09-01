# Cloudflare Temp Email Deployment (Self-Hosting Guide)

## Overview
`cloudflare_temp_email` (by dreamhunter2333) is a zero-cost temporary email service running on Cloudflare's serverless free tier (Email Routing, Workers, D1, Pages, KV/R2).

## Core Requirements & Stack
- **Domain**: Registered domain managed on Cloudflare DNS with Email Routing enabled.
- **Workers**: Backend API & Rust WASM MIME parser (`worker.ts`).
- **D1**: SQLite database (`temp-email-db`) storing users, emails, settings.
- **Pages**: Vue 3 SPA frontend (`frontend/dist`).
- **KV / R2 (Optional)**: KV for OTP/limits/Telegram bot state; R2 for email attachments.

## Deployment Options

### Option A: GitHub Actions (Recommended for zero-maintenance updates)
1. Fork `dreamhunter2333/cloudflare_temp_email`.
2. Add Cloudflare `ACCOUNT_ID` & `CLOUDFLARE_API_TOKEN` to GitHub Secrets.
3. Create D1 database in Cloudflare dashboard (`temp-email-db`).
4. Trigger GitHub Actions deployment workflow.
5. Set Email Routing Catch-all rule to point to Worker.

### Option B: CLI Deployment via Wrangler
1. **Prerequisites & Setup**:
   - Note for remote Linux/headless environments: `wrangler login` triggers an interactive OAuth browser callback on `localhost:8976` which times out. Prefer creating a Cloudflare API Token (`Edit Workers/D1/Pages` permissions) and setting `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` environment variables.
   - **API Token Permissions Required**: 
     - **Accounts**: Workers KV Storage (Edit), Workers Scripts (Edit), Account Settings (Read), Workers Tail (Read), Workers R2 Storage (Edit), Cloudflare Pages (Edit), Workers Builds Configuration (Edit), Workers Agents Configuration (Edit), Workers Observability (Edit), Containers (Edit), **D1 (Edit)**.
     - **Zones**: Workers Routes (Edit), **DNS (Edit)** (required for automated CNAME record creation), **Email Routing Rules (Edit)** (required for automated Catch-all routing setup).
     - **Users**: User Details (Read), Memberships (Read).
   - **API Token Troubleshooting**: If creating DNS records or Email Routing rules via Cloudflare REST API returns `code 10000` (`Authentication error`), the token lacks **Zones -> DNS -> Edit** or **Zones -> Email Routing Rules -> Edit** permissions.
   - **IP & Expiration Restrictions**: If Client IP filtering is required by UI, set IP to the server's public IP (e.g. `20.192.4.173`). Set TTL to 1-5 years or Never.
   ```bash
   npm i -g wrangler pnpm
   # If running locally with GUI browser:
   wrangler login
   # If on headless/remote server:
   export CLOUDFLARE_API_TOKEN="<your-api-token>"
   export CLOUDFLARE_ACCOUNT_ID="<your-account-id>"

   git clone https://github.com/dreamhunter2333/cloudflare_temp_email.git
   cd cloudflare_temp_email/worker
   cp wrangler.toml.template wrangler.toml
   ```
2. **Database Initialization**:
   ```bash
   wrangler d1 create temp-email-db
   wrangler d1 execute temp-email-db --file=../db/schema.sql --remote
   ```
3. **Configure `worker/wrangler.toml`**:
   - Set `routes` for custom backend domain (e.g. `api-tempmail.indrayuda.my.id`).
   - Set `[vars]`: `DOMAINS`, `PREFIX`, `JWT_SECRET`, `ADMIN_PASSWORDS`.
   - Set `[[d1_databases]]`: `database_name` & `database_id`.
4. **Deploy Backend**:
   ```bash
   cd worker && pnpm install && pnpm run deploy
   ```
5. **Deploy Frontend (Pages)**:
   ```bash
   cd ../frontend
   pnpm install
   echo "VITE_API_BASE=https://<worker-api-domain>" > .env.prod
   pnpm build --emptyOutDir
   # First time deploying Pages via Wrangler CLI:
   npx wrangler pages project create <project-name> --production-branch=production
   npx wrangler pages deploy dist --project-name=<project-name> --branch=production
   ```
   - **Custom Domain for Pages**: Link custom domain to Pages project in Cloudflare Dashboard (or via Cloudflare API endpoint `/accounts/{account_id}/pages/projects/{project_name}/domains`) and add CNAME record pointing to `<project-name>.pages.dev` with proxy enabled (orange cloud).
6. **Cloudflare Email Routing**:
   - Open Cloudflare Console -> Domain -> Email Routing -> Routing Rules.
   - Edit **Catch-all rule** -> Action: **Send to Worker** -> Select Worker.
