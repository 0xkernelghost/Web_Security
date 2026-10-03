>> Target Lab: Blind OS command injection with time delays

--- 
**Vulnerability**
- Blind OS command injection vulnerability in the feedback function.

**Goal**
- Exploit the blind OS command injection vulnerability to cause a 10-second delay.

---

### Steps:

#### 1. Open the Lab
- Access the lab interface in the browser.

#### 2. Locate the Feedback Feature
- Navigate to the **Submit feedback** page.
- ![alt text]({8DA60AA1-6372-4050-9617-2A33C5074E3A}.png)

#### 3. Intercept and Analyze Request
- Fill out the feedback form with dummy data.
- Capture the POST request in Burp Suite and send it to **Repeater**.
- ![alt text]({8187C29D-1B3B-44A7-8E1E-0DD3D4EA05EF}.png)
- ![alt text]({CD00CA00-EF97-4137-A148-DA2F1CE2C122}.png)

#### 4. Testing for Blind OS Command Injection (Time Delays)
> **Note:** Always URL-encode special characters / spaces in Burp Repeater using `Ctrl + U` before sending.

- **Test Payload:**
  ```bash
  & sleep 10 #
  ```

- **Testing other input fields (e.g., name / subject / message):**
  - Response returns `200 OK` immediately without any delay (Not vulnerable).
  - ![alt text]({4317FA61-804E-4836-899E-C1538CB90FA2}.png)

- **Testing the `email` field (Vulnerable Parameter):**
  - Inject the payload into the `email` parameter and URL-encode it (`Ctrl + U`):
    ```http
    email=test@testgmail.edu & sleep 10 #
    ```
    *(URL-encoded in POST body: `email=test%40testgmail.edu+%26+sleep+10+%23`)*
  - ![alt text]({B6DDD16F-4F89-41A6-822A-38D88F7770E4}.png)
  - The server delays response by **~10 seconds** (10,000+ ms in Burp Repeater), confirming command execution!
  - ![alt text]({EB8D8BA0-F2ED-4735-877E-00CC32166ADF}.png)

#### 5. Lab Solved
- The lab is successfully solved once the 10-second delay is triggered.
- ![alt text]({D2383828-3C95-4AD5-A248-549DC58F1E2D}.png)
