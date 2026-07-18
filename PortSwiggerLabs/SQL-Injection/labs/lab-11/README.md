# 🎯 Platform: PortSwigger
### 📝 Target: Lab - Blind SQL injection with conditional responses

> **Vulnerability Location:** `TrackingId` cookie
> **Goal:** Find out the password of the `administrator` user and log in.

---

## 🔍 Analysis
### Find the Indicator for True/False Conditions
*   ✅ **True Condition:** If the SQL query returns data (true), the response contains a `Welcome back!` message.
*   ❌ **False Condition:** If the SQL query returns no data (false), the `Welcome back!` message is missing.
*   🗄️ **Database Info:** Contains a `users` table with `username` and `password` columns.

---

## 🚀 Exploitation

### Step 1: Find the Length of the Administrator Password
*   **Tool Used:** Burp Intruder (Numbers payload: `1` to `100`)
*   **Payload:**
    ```sql
    ' AND LENGTH((SELECT password from users where username='administrator'))=§1§--
    ```
*   **Result:** The response showed `Welcome back!` when the length was exactly **`20`**.

### Step 2: Brute-force the Password Characters
*   **Logic / Format:** Extract characters one by one using the `SUBSTRING` function.
*   **Example Payload:**
    ```sql
    ' AND SUBSTRING((SELECT password FROM users WHERE username='administrator'), 1, 1)='a'--
    ```
*   **Automation:** Used a custom fuzzing script in the terminal (`./fuzz`) to extract all 20 characters automatically based on the true/false conditional responses.
*   **Extracted Password:** `jpmuf0s942xzfj36m0lh`

---

## 🛠️ Steps to Reproduce
1. **Access** the lab environment.
2. **Capture** the GET request in Burp Suite and locate the `TrackingId` cookie.
3. **Enumerate Length:** Use Burp Intruder to find the exact password length by injecting the length payload.
4. **Execute Script:** Run the custom `./fuzz` script in your terminal to brute-force each character of the password.
5. **Authenticate:** Log in to the application using the username `administrator` and the extracted password.
6. 🎉 **Lab is solved!**


### exploit.py
