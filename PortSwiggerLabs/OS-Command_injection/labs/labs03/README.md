>> Target Lab: Blind OS command injection with output redirection

---
**Vulnerability**
- Blind OS command injection vulnerability in the feedback function.

**Goal**
- Execute the `whoami` command and retrieve the output using output redirection.

---

### Steps:

#### 1. Open the Lab
- Access the lab interface in the browser.

#### 2. Locate the Feedback Feature
- Navigate to the **Submit feedback** page.
- ![alt text]({270D7BD3-E558-412B-B549-A32F22BA73C9}.png)


#### 3. Intercept and Analyze Request
- Fill out the feedback form with dummy data.
- Capture the POST request in Burp Suite and send it to **Repeater**.
- ![alt text]({66EFD58C-BBA3-469A-9F8E-E4F8A99CDA0F}.png)
- our vuln endpoint is email field 

#### 4. Identify the Writable Directory
- The lab tells us there's a writable folder at:
**/var/www/images/**
- The application serves product catalog images from this location. We can use output redirection to send the command's output into a file here, then retrieve it via the image loading URL.

#### 5. Inject Command with Output Redirection
> **Note:** Always URL-encode special characters / spaces in Burp Repeater using `Ctrl + U` before sending.

- **Test Payload:**
```bash
  || whoami > /var/www/images/output.txt ||
```

- **Testing other input fields (e.g., name / subject / message):**
  - No change in behavior, response is identical to normal (Not vulnerable).

- **Testing the `email` field (Vulnerable Parameter):**
  - Modify the `email` parameter:
```http
    email=||whoami>/var/www/images/output.txt||
```
  - URL-encode the payload (`Ctrl + U`) before sending.

  - Send the request — nothing visible in the response body (blind injection), but the command executes on the backend.

#### 6. Retrieve the Output via Image Loading Request
- Intercept the request that loads a product image — it uses a `filename` parameter to fetch images.
- Modify the `filename` parameter to point to the file just created:
```http
  filename=output.txt
```
- Forward the request.
- ![alt text]({2BC930A6-5AEF-4692-962C-754C00544928}.png)

#### 7. Confirm Command Execution
- The response body now contains the output of the `whoami` command (e.g., `peter-XXXX` or similar user).

- This confirms successful exploitation of the blind OS command injection via output redirection.

#### 8. Lab Solved
- As soon as the `whoami` output appears in the response, the lab is automatically marked "Solved".
- ![alt text]({315C3EAB-358B-4DB9-B831-81B7D9BF5C4C}.png)