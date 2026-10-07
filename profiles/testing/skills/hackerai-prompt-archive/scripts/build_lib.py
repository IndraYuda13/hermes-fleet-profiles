import re

COMMIT = '6cf55ed545a59b1a61740a857b505cf18b8fad2b'

def read(p):
    return open(p, encoding='utf-8', errors='ignore').read()

def find_close(s, start):
    i = start + 1
    while i < len(s):
        c = s[i]
        if c == chr(92):
            i += 2
            continue
        if c == '`':
            return i
        i += 1
    return -1

def unesc(t):
    out = []
    i = 0
    n = len(t)
    while i < n:
        c = t[i]
        if c == chr(92) and i + 1 < n:
            d = t[i+1]
            if d == 'n':
                out.append(chr(10)); i += 2; continue
            if d == 't':
                out.append(chr(9)); i += 2; continue
            if d == '`':
                out.append('`'); i += 2; continue
            if d == chr(92):
                out.append(chr(92)); i += 2; continue
            if d == '"':
                out.append('"'); i += 2; continue
            if d == "'":
                out.append("'"); i += 2; continue
            if d == chr(10):
                i += 2; continue
            if d == 'r':
                out.append(chr(13)); i += 2; continue
        out.append(c); i += 1
    return ''.join(out)

def decl_span(s, name):
    m = re.search(r'^(?:export )?(?:const|function|type) ' + re.escape(name) + r'\b', s, re.M)
    if not m:
        raise ValueError('decl not found: ' + name)
    start = m.start()
    m2 = re.search(r'^(?:export )?(?:const|function|type) \w+', s[m.end():], re.M)
    end = m.end() + m2.start() if m2 else len(s)
    return s[start:end]

def tlit(span, contains=None, idx=0):
    outs = []
    pos = 0
    while True:
        b = span.find('`', pos)
        if b == -1:
            break
        e = find_close(span, b)
        if e == -1:
            break
        outs.append(span[b+1:e])
        pos = e + 1
    if contains is not None:
        for o in outs:
            if contains in o:
                return o
        raise ValueError('literal containing not found: ' + repr(contains[:60]))
    return outs[idx]

def js_strings(span, minlen=30):
    outs = []
    for m in re.finditer(r'"((?:[^"\\]|\\.)*)"', span, re.DOTALL):
        raw = m.group(1)
        if len(raw) >= minlen:
            outs.append(unesc(raw))
    return outs

def block(span, start_marker, end_marker):
    i = span.find(start_marker)
    if i == -1:
        raise ValueError('block start missing: ' + start_marker)
    j = span.find(end_marker, i)
    if j == -1:
        raise ValueError('block end missing: ' + end_marker)
    return span[i:j + len(end_marker)]

def scan_literals(src):
    spans = []
    pos = 0
    while True:
        b = src.find('`', pos)
        if b == -1:
            break
        e = find_close(src, b)
        if e == -1:
            break
        spans.append((b, e+1, 'tpl', src[b+1:e]))
        pos = e + 1
    for m in re.finditer(r'"((?:[^"\\]|\\.)*)"', src, re.DOTALL):
        s0, s1 = m.start(), m.end()
        if any(a <= s0 < b for a, b, _, _ in spans):
            continue
        raw = m.group(1)
        if len(raw) >= 60:
            spans.append((s0, s1, 'str', raw))
    spans.sort()
    out = []
    for a, b, kind, raw in spans:
        val = unesc(raw)
        if kind == 'str' and len(val) < 60:
            continue
        out.append((a, kind, raw, val))
    return out

def resolve_all(src):
    R = {}
    sp = decl_span(src, 'systemPrompt')
    ident = unesc(tlit(sp, contains='You are HackerAI'))
    ident = ident.replace('You are currently powered by ${modelDisplayName}.' + chr(10), '')
    agent_instr = sorted(js_strings(decl_span(src, 'getAgentModeInstructions'), 10), key=len)[-1]
    ident = ident.replace('${agentInstructions}', agent_instr)
    if 'You are an agent' not in ident:
        raise ValueError('agent instructions missing')
    R['identity'] = ident.strip()
    for key, name in [('language','LANGUAGE_SECTION'),('general','GENERAL_RESPONSE_SECTION'),('style','RESPONSE_STYLE_SECTION'),('evidence','EVIDENCE_AND_INFERENCE_SECTION'),('deliverable','AGENT_DELIVERABLE_SECTION')]:
        R[key] = unesc(tlit(decl_span(src, name))).strip()
    fresh_span = decl_span(src, 'getFreshnessAndWebSearchSection')
    fresh = unesc(tlit(fresh_span, contains='<freshness_and_web_search>'))
    g = re.search(r'"(Your reliable knowledge cutoff is not specified\.[^"]*)"', fresh_span)
    guidance = unesc(g.group(1)) if g else 'Your reliable knowledge cutoff is not specified.'
    fresh = fresh.replace('${knowledgeCutoffGuidance}', guidance)
    R['freshness'] = fresh.strip()
    agent_sec = decl_span(src, 'getAgentModeSection')
    R['mode_agent'] = unesc(block(agent_sec, '<current_mode>', '</current_mode>')).strip()
    R['tool_calling'] = unesc(block(agent_sec, '<tool_calling>', '</tool_calling>')).strip()
    R['lifecycle'] = unesc(block(agent_sec, '<agent_lifecycle>', '</agent_lifecycle>')).strip()
    R['hygiene'] = unesc(tlit(decl_span(src, 'AGENT_ARTIFACT_HYGIENE_SECTION'))).strip()
    R['parallel'] = unesc(block(agent_sec, '<maximize_parallel_tool_calls>', '</maximize_parallel_tool_calls>')).strip()
    R['scan'] = unesc(block(agent_sec, '<scan_methodology>', '</scan_methodology>')).strip()
    R['finding_quality'] = unesc(block(agent_sec, '<finding_quality>', '</finding_quality>')).strip()
    appr = []
    ap_span = decl_span(src, 'getAgentToolApprovalSection')
    for m in re.finditer(r'return `', ap_span):
        b = m.end() - 1
        e = find_close(ap_span, b)
        appr.append(unesc(ap_span[b+1:e]).strip())
    R['approval_ask'] = next(a for a in appr if 'Ask for approval' in a)
    R['approval_auto'] = next(a for a in appr if 'Approve for me' in a)
    R['approval_full'] = next(a for a in appr if 'Full access' in a)
    sec = decl_span(src, 'getSecurityInstructions')
    sec_lit = unesc(tlit(sec, contains='<authorized_security_posture>'))
    env_span = decl_span(src, 'getExecutionEnvironmentSecurityText')
    env_prefix = unesc(tlit(env_span, contains='Tool operations execute'))
    env_prefix = env_prefix.replace('${safetyText}', '@@SAFETY@@')
    local_txt = "This chat is connected to a local or remote host without Docker isolation, so terminal commands can affect the user's host OS."
    cloud_txt = "For the default cloud sandbox, commands run in an isolated container with no direct access to the user's host OS."
    ask_txt = 'This chat has no terminal command environment.'
    for t in [local_txt, cloud_txt, ask_txt]:
        if t not in env_span:
            raise ValueError('env text missing: ' + t[:40])
    def resolve_posture(env_value):
        p = sec_lit
        p = re.sub(r'\$\{executionEnvironment === "cloud" \?[\s\S]*? : ""\}', '', p)
        p = p.replace('${getExecutionEnvironmentSecurityText(executionEnvironment)}', env_value)
        return p.strip()
    R['posture_local'] = resolve_posture(env_prefix.replace('@@SAFETY@@', local_txt))
    R['posture_cloud'] = resolve_posture(env_prefix.replace('@@SAFETY@@', cloud_txt))
    R['posture_ask'] = resolve_posture(ask_txt)
    dg = unesc(tlit(decl_span(src, 'getGenericDelegationSection')))
    dg2 = re.sub(r'\$\{agentPermissionMode === "full_access" \?[\s\S]*? : "Ask for approval"\}', 'Full access', dg)
    if dg2 == dg:
        raise ValueError('delegation placeholder not replaced')
    R['delegation'] = dg2.strip()
    sb_span = decl_span(src, 'getDefaultSandboxEnvironmentSection')
    sb = unesc(tlit(sb_span, contains='<sandbox_environment>'))
    port_sec = unesc(tlit(sb_span, contains='Port-scanning limitation')).strip()
    sysenv = unesc(tlit(sb_span, contains='Debian GNU/Linux 12')).strip()
    devenv = unesc(tlit(sb_span, contains='Python 3.12.11')).strip()
    tools_chain = chr(10).join(['', '']).join([])  # placeholder no-op
    tools_chain = (unesc(tlit(decl_span(src, 'PREINSTALLED_PENTESTING_TOOLS'))).strip()
                   + chr(10) + chr(10)
                   + unesc(tlit(decl_span(src, 'SANDBOX_TOOL_RECIPES_SECTION'))).strip()
                   + chr(10) + chr(10)
                   + unesc(tlit(decl_span(src, 'AGENT_BROWSER_SECTION'))).strip())
    sb = sb.replace('${portScanningSection}', port_sec)
    sb = sb.replace('${systemEnvironment}', sysenv)
    sb = sb.replace('${developmentEnvironment}', devenv)
    if '${installedTools}' not in sb:
        raise ValueError('installedTools placeholder missing')
    sb = sb.replace('${installedTools}', tools_chain)
    R['sandbox_default'] = sb.strip()
    ask_span = decl_span(src, 'getAskModeSection')
    reminder = unesc(tlit(ask_span, contains='<current_mode>'))
    reminder = reminder.replace('${notesCapability}', ' and manage notes')
    cta = next(s for s in js_strings(ask_span, 40) if 'AGENT MODE runs commands' in s)
    reminder = reminder.replace('${agentModeCTA}', cta)
    prod_span = decl_span(src, 'getProductQuestionsSection')
    prod = unesc(tlit(prod_span))
    free_branch = 'For local-machine access questions, follow the requirements in <local_machine_access>. For all other'
    prod_free = re.sub(r'\$\{subscription === "free" \?[\s\S]*? : "For"\}', free_branch, prod)
    prod_pro = re.sub(r'\$\{subscription === "free" \?[\s\S]*? : "For"\}', 'For', prod)
    R['product_free'] = prod_free.strip()
    R['product_pro'] = prod_pro.strip()
    R['ask_pro'] = (reminder + prod_pro).strip()
    R['ask_free'] = (reminder + prod_free).strip()
    R['local_machine'] = unesc(tlit(decl_span(src, 'LOCAL_MACHINE_ACCESS_SECTION'))).strip()
    R['deepseek'] = unesc(tlit(decl_span(src, 'getDeepSeekToolUsageInstructions'))).strip()
    R['boundary'] = js_strings(decl_span(src, 'SYSTEM_PROMPT_RUNTIME_BOUNDARY'), 1)[0]
    return R
