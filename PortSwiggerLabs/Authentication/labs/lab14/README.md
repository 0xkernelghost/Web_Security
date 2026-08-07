# Lab: 2FA Bypass Using a Brute-Force Attack (with Session Handling Rules)

**Category:** Authentication
**Vulnerability:** Brute-forceable 2FA code, combined with account lockout after failed attempts

---

## Goal

Log in to Carlos's account by brute-forcing his 4-digit 2FA code, and solve the lab by
accessing his "My account" page.

---

## The problem this lab adds

In a normal 2FA brute-force, you'd just fire 10,000 requests at `/login2` with every
possible code. But this app has a twist:

- Enter the **wrong 2FA code twice in a row**, and the account gets **logged out /
  locked** automatically.
- This means a simple Intruder attack fails almost immediately — by request #3, the
  session is dead and every remaining guess just gets rejected.

So the real challenge isn't guessing the code — it's **staying logged in** while
guessing it.

---

## The idea: log back in before every single guess

Instead of sending one giant batch of requests on one session, we do this:

1. Start a **brand new login** (fresh session).
2. Walk through the normal login flow: load the login page, submit
   username/password, land on the 2FA page.
3. Immediately submit **one** 2FA code guess.
4. Whatever the result — throw the session away and repeat from step 1 with the
   next code.

Since each guess gets its own fresh session, the "2 wrong attempts = lockout" rule
never triggers (we only ever make 1 attempt per session).

---

## Doing it in Burp: Session Handling Rules + Macro

Burp has a built-in feature for exactly this — a **macro** that runs automatically
before every request Intruder sends.

### Steps

1. **Settings → Sessions → Session handling rules → Add**
2. **Scope tab** → set URL scope to **"Include all URLs"**
3. **Details tab** → **Rule Actions → Add → Run a macro**
4. Click **Add** to open the Macro Recorder, and select these 3 requests
   **in order**:
   - `GET /login`
   - `POST /login`
   - `GET /login2`
5. Click **Test macro** — the final response should show the 2FA code entry page.
   This confirms the macro can log in successfully on its own.
6. Close all the dialogs (OK → OK → OK).

Now, every time Intruder sends a request, Burp will silently run this 3-step login
first, so we always have a fresh, valid session.

### Intruder setup

- Send the `POST /login2` request (the one where you submitted a wrong code) to
  Intruder.
- Mark `mfa-code` as the payload position.
- Payload type: **Numbers**, range `0–9999`, step `1`, min/max digits = `4`
  (this generates every code from `0000` to `9999`).
- **Resource pool → Maximum concurrent requests = 1**
  (important — the macro must run one at a time, or logins will collide with
  each other).
- Start the attack, sort by **Status code**, and look for **302**. That row's
  payload is Carlos's correct 2FA code.

---

## Why the macro sometimes fails in practice

In real use, the macro can be flaky — some requests return `400 Bad Request`
instead of `200`/`302`. This usually means:

- The macro didn't complete the login flow correctly for that request (timing,
  stale CSRF token, cookie jar not updating in time).
- Under `Maximum concurrent requests = 1` this should mostly not happen, but
  Burp's macro engine isn't 100% reliable for large brute-force runs.

If Burp's macro keeps failing, the same logic can be scripted directly — see
`solve.go`. It does exactly what the macro does (fresh login → 2FA guess →
throw away session) but with full control and much faster, since it can run
guesses in parallel.

---

## Solving the lab

1. Find the row with **status 302** (or the request with a very different
   response length, if the app auto-follows redirects).
2. Right-click that row → **Show response in browser**.
3. Open the resulting URL, click **My account**.
4. Lab solved.
