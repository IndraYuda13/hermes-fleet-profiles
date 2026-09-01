"""
Helper template for Cloudflare bypass in Hermes browser_exec sessions.
"""
import urllib.request
import json
import time

def bypass_and_navigate(target_url: str, solver_url: str = "http://127.0.0.1:8191/v1"):
    # 1. Fetch solution from FlareSolverr
    payload = json.dumps({
        "cmd": "request.get",
        "url": target_url,
        "maxTimeout": 60000
    }).encode("utf-8")
    
    req = urllib.request.Request(solver_url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        solution = json.loads(resp.read().decode("utf-8"))["solution"]
        
    ua = solution["userAgent"]
    cookies = solution["cookies"]
    
    # 2. Emulate UA and disable webdriver flag
    cdp("Emulation.setUserAgentOverride", userAgent=ua)
    cdp("Page.addScriptToEvaluateOnNewDocument", source="""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    """)
    
    # 3. Inject cookies
    for c in cookies:
        cdp("Network.setCookie",
            name=c["name"],
            value=c["value"],
            domain=c["domain"],
            path=c.get("path", "/"),
            secure=c.get("secure", False),
            httpOnly=c.get("httpOnly", False)
        )
        
    # 4. Navigate
    goto_url(target_url)
    wait_for_load()
    time.sleep(3)
    return page_info()
