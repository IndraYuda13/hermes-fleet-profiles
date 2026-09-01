# x.ai & Grok Auth Flow Reference

## gRPC-Web Endpoints (`accounts.x.ai`)
- **Email Validation**: `POST https://accounts.x.ai/auth_mgmt.AuthManagement/CreateEmailValidationCode`
- **OTP Verification**: `POST https://accounts.x.ai/auth_mgmt.AuthManagement/VerifyEmailValidationCode`
- **Password Validation**: `POST https://accounts.x.ai/auth_mgmt.AuthManagement/ValidatePassword`

## Cloudflare Turnstile Sitekey & Clearance
- **Page Widget Sitekey**: `0x4AAAAAAAhr9JGVDZbrZOo0`
- **Solver Endpoint**: `http://127.0.0.1:5072/cf_clearance?url=https://accounts.x.ai/sign-up`
- **Widget Solver Endpoint**: `http://127.0.0.1:5072/turnstile?url=https://accounts.x.ai/sign-up&sitekey=0x4AAAAAAAhr9JGVDZbrZOo0`

## OAuth Device Flow Details (`grok-cli`)
- **Client ID**: `b1a00492-073a-47ea-816f-4c329264a828`
- **Device Authorization Request**: `POST https://auth.x.ai/oauth2/device/code` (Body: `client_id=...&scope=openid profile email offline_access grok-cli:access api:access conversations:read conversations:write`)
- **Token Poll**: `POST https://auth.x.ai/oauth2/token` (Grant type: `urn:ietf:params:oauth:grant-type:device_code`)
- **Device Verification Page**: `https://accounts.x.ai/oauth2/device?user_code=<USER_CODE>`

## 9Router Database Location & Hot-Reload
- **Database File**: `/root/.9router/db/data.sqlite` (`providerConnections` table)
- **Caution**: Executing `fuser -k 20128/tcp` terminates 9Router instantly. If the agent session routes through 9Router, this will disconnect the agent turn.
