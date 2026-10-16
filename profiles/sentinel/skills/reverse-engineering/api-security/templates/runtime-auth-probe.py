#!/usr/bin/env python3
# Reusable probe template for a LIVE deployed origin/CSRF/cookie/session-class gate.
# Adjust before running:
#   B    = mission/artifact root (holds maintenance/ and runtime-stage/)
#   O    = public origin under test
#   proof/private-config/fixture paths and their JSON key names
#   provider endpoint host/port for the refresh check
# Run as:  uv run --with requests python runtime-auth-probe.py
# Secrets stay in process memory: never print fixture credentials, cookie values or tokens.
import requests, json, pathlib, hashlib, base64, uuid, subprocess, sys

B = pathlib.Path('/mnt/CHANGE-ME')
O = 'https://CHANGE-ME'
checks, attrs = [], []


def check(name, ok, status=None):
    checks.append({'check': name, 'ok': bool(ok), 'status': status})
    if not ok:
        raise RuntimeError(name + ' failed')


def post(s, p, data, origin=O):
    return s.post(O + p, json=data, headers={} if origin is None else {'Origin': origin}, timeout=30)


def cookies(r, path):
    cs = list(r.cookies)
    check('cookie present ' + path, bool(cs))
    for c in cs:
        a = {'name': c.name, 'secure': c.secure, 'httpOnly': c.has_nonstandard_attr('HttpOnly'),
             'sameSite': c.get_nonstandard_attr('SameSite'), 'path': c.path}
        attrs.append(a)
        check('cookie attributes ' + path,
              a['secure'] and a['httpOnly'] and str(a['sameSite']).lower() == 'lax' and a['path'] == path)


def sessiondata(s):
    cs = sorted([c for c in s.cookies if c.name.startswith('CHANGE-ME-session')], key=lambda c: c.name)
    raw = ''.join(c.value for c in cs)
    check('session encoding', raw.startswith('base64-'))
    x = raw[7:]
    return json.loads(base64.urlsafe_b64decode(x + '=' * (-len(x) % 4)))


try:
    proof = json.loads((B / 'maintenance/runtime-origin-proof.json').read_text())
    hashes = {p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() for p in proof['hashes']}
    check('runtime hashes match handoff', hashes == proof['hashes'])
    check('deployed build matches', (B / 'release/.next/BUILD_ID').read_text().strip() == proof['build'])
    check('source matches', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=B / 'release', text=True).strip() == proof['source'])
    f = json.loads((B / 'maintenance/live-fixture.private.json').read_text())
    cfg = json.loads((B / 'runtime-stage/live-runtime.private.json').read_text())

    s = requests.Session()
    r = post(s, '/auth/login', {'email': f['email'], 'password': f['password']})
    check('public login', r.status_code == 200, r.status_code)
    cookies(r, '/')
    baseline = s.get(O + '/api/v1/classes', timeout=30).json()

    for origin in ['https://foreign.invalid', 'null', None]:
        r = post(s, '/api/v1/classes', {'id': str(uuid.uuid4()), 'label': 'probe synthetic'}, origin)
        check('write rejects ' + str(origin), r.status_code == 403, r.status_code)
        check('state unchanged ' + str(origin), s.get(O + '/api/v1/classes', timeout=30).json() == baseline)
        r = post(s, '/auth/logout', {}, origin)
        check('logout rejects ' + str(origin), r.status_code == 403, r.status_code)
        check('session retained ' + str(origin), s.get(O + '/api/v1/classes', timeout=30).status_code == 200)

    second = requests.Session()
    r = post(second, '/api/v1/board/identity', {})
    check('second-surface identity', r.status_code == 200, r.status_code)
    cookies(r, '/api/v1/board')
    forced = requests.get(O + '/api/v1/classes',
                          headers={'Cookie': '; '.join(c.name + '=' + c.value for c in second.cookies)}, timeout=30)
    check('second surface cannot reach first-surface API even with forced cookies', forced.status_code == 401, forced.status_code)

    token = sessiondata(s)['refresh_token']
    provider = 'http://127.0.0.1:CHANGE-ME/auth/v1/token?grant_type=refresh_token'
    ph = {'apikey': cfg['NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY']}
    r = requests.post(provider, json={'refresh_token': token}, headers=ph, timeout=30)
    check('same-login provider refresh succeeds', r.status_code == 200, r.status_code)
    renewed = r.json()
    check('refresh returns same user', renewed['user']['id'] == sessiondata(s)['user']['id'])
    encoded = 'base64-' + base64.urlsafe_b64encode(json.dumps(renewed, separators=(',', ':')).encode()).decode().rstrip('=')
    for c in list(s.cookies):
        if c.name.startswith('CHANGE-ME-session'):
            s.cookies.clear(c.domain, c.path, c.name)
    s.cookies.set('CHANGE-ME-session', encoded, domain='CHANGE-ME', path='/', secure=True)
    check('refreshed session works on public HTTPS', s.get(O + '/api/v1/classes', timeout=30).status_code == 200)

    r = post(s, '/auth/logout', {})
    check('normal logout succeeds', r.status_code == 200, r.status_code)
    check('post-logout API denied', s.get(O + '/api/v1/classes', timeout=30).status_code == 401)
    r = requests.post(provider, json={'refresh_token': renewed['refresh_token']}, headers=ph, timeout=30)
    check('logout invalidates newest refresh token', r.status_code in (400, 401, 403), r.status_code)
    meta = {k: v for k, v in r.json().items() if k in ('error', 'error_code', 'error_description', 'msg', 'code')}
    check('revocation is a token-level provider rejection',
          meta.get('code') == 'invalid_credentials' or meta.get('error_code') in
          ('refresh_token_not_found', 'refresh_token_already_used', 'session_not_found') or
          'refresh token' in str(meta.get('error_description', '')).lower())
    check('runtime hashes unchanged', hashes == {p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() for p in hashes})

    result = {'claim_type': 'OBSERVATION', 'verification_status': 'VERIFIED', 'build': proof['build'],
              'hashes': hashes, 'checks': checks, 'cookieAttributesOnly': attrs,
              'limits': ['Explicit provider refresh + public use only; expiry-driven automatic refresh not exercised.',
                         'Logout revocation covers the refresh token, not immediate access-JWT revocation.']}
    print(json.dumps(result, indent=2))
    pathlib.Path('runtime-security-proof.json').write_text(json.dumps(result, indent=2))
except Exception as e:
    print(json.dumps({'verification_status': 'BLOCKED', 'errorType': type(e).__name__, 'checks': checks}))
    sys.exit(1)
