# Lab: Web shell upload via Content-Type restriction bypass



---

**Vuln**
- Server trusts the user-controlled `Content-Type` header instead of validating the actual file content, allowing file type restrictions to be bypassed.

**Goal**
- Upload a PHP web shell by spoofing the `Content-Type` header, read `/home/carlos/secret`, and submit the secret.

---

### Steps

1. **Access the lab** and log in using the credentials `wiener:peter`.

2. **Navigate to your account page** and attempt to upload a PHP web shell directly.

```php
<?php system("cat /home/carlos/secret"); ?>
```

- The server rejects it — only image file types are allowed.

   ![Server blocks the PHP file upload]({8219914C-EB23-4A5F-9C33-82AA6F0CBFED}.png)

3. **Intercept the upload request in Burp Suite** and send it to Repeater.

   ![Upload request captured in Burp Suite](image.png)
   ![Request details in Burp Repeater]({4488B440-6FFB-40D7-81F1-4A96A39D502C}.png)

4. **Modify the `Content-Type` header** in the multipart form data.
   - Change `Content-Type: application/x-php` → `Content-Type: image/jpeg`
   - The server trusts the `Content-Type` header without verifying the actual file content.

   ![Original Content-Type header set to application/x-php]({791FFE79-CB0D-4989-B408-97C23D32BE2A}.png)

   - After changing the Content-Type to `image/jpeg`, the server accepts the file.

   ![Content-Type changed to image/jpeg — upload accepted]({C5DC9B09-42A4-4811-B521-C486B1945A33}.png)

5. **Execute the web shell** by navigating to the uploaded file URL.
   - Right-click on the avatar image and open it in a new tab to trigger the PHP execution.

   ![Navigating to the uploaded shell URL]({9A930E9E-4EDF-459B-97F3-E6F97A8B182B}.png)
   ![Secret file contents displayed in the browser](image-1.png)

   The contents of `/home/carlos/secret` are now visible in the response.

6. **Submit the secret** using the button in the lab banner to solve the lab.

   ![Lab solved — secret submitted successfully]({2326A264-E275-490C-9D69-D40C9E421C11}.png)

### Files Used

| File | Purpose |
|------|---------|
| `test.php` | Web shell — `<?php system("cat /home/carlos/secret"); ?>` |
| `POC.py` | Automated exploit script |

---

### Key Takeaway

> The server only validated the `Content-Type` header provided by the client, not the actual file content or extension. Since `Content-Type` is fully attacker-controlled, bypassing this restriction is trivial. Proper file upload validation should inspect the **magic bytes** (file signature) of the uploaded content, not trust client-supplied headers.
