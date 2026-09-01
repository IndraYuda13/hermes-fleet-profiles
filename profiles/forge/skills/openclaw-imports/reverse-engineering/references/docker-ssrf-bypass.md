# SSRF and Docker Isolation Bypasses

When reverse engineering and bypassing SSRF (Server-Side Request Forgery) protections in containerized applications (like Docker), the following patterns apply:

### 1. The `localhost` Docker Trap
When an application runs inside a standard Docker `bridge` network, `localhost` or `127.0.0.1` refers to the container's *internal* loopback interface, NOT the host machine's loopback interface. 
- If a target service (like a proxy or gateway) runs on the host OS but the application runs in a container, telling the application to connect to `localhost:PORT` will fail with "Connection Refused" or similar.
- **Solution**: Use the Docker host's bridge IP. On Linux, this is almost always `172.17.0.1` (or the default gateway of the specific Docker network). On macOS/Windows (Docker Desktop), use `host.docker.internal`.

### 2. Hardcoded SSRF Validations in Go
Modern Go applications often use strict URL validation before passing the URL to `http.Client`. 
- **Pattern**: A custom `http.Transport` or `DialContext` is used to resolve the hostname to an IP, and then that IP is checked against a list of private CIDR blocks (e.g., `127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`).
- **Pattern**: Explicit string matches block hostnames like `localhost`, `0.0.0.0`, or `metadata.google.internal`.
- **Bypass (Source Patching)**: If you control the source and can recompile, find the `isPrivateIP` or equivalent function and insert `return false` at the very top. Also, remove explicit string checks for `localhost` if necessary.

### 3. Proxy Interference
Applications with `HTTP_PROXY`, `HTTPS_PROXY`, or `ALL_PROXY` environment variables set will route all traffic through that proxy.
- Even if you successfully bypass SSRF checks and use `172.17.0.1`, the proxy might intercept the request and fail to route it back to the host machine.
- **Bypass**: You may need to bypass the proxy entirely for local traffic. While `NO_PROXY=172.17.0.1` works in some environments, in others you may need to strip the proxy environment variables from the container or bypass them at the HTTP client level in the code.