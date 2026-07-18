# 🎯 Platform: PortSwigger
### 📝 Target: Lab - Blind SQL injection with time delays

> **Vulnerability Location:** `TrackingId` cookie
> **Goal:** Exploit the SQL injection vulnerability to cause a 10-second time delay.

---

## 🔍 Analysis
### Understand the Vulnerability
*   **Fully Blind:** The application does not return any query results in the page, nor does it display any database errors. The response is identical whether the query is true, false, or malformed.
*   **Synchronous Execution:** Because the database query executes synchronously, we can inject a command that instructs the database to pause (sleep) before returning the response. By measuring the time it takes for the HTTP response to arrive, we can confirm the injection exists.
*   **Database Fingerprinting:** Different databases use different syntax for time delays:
    *   MySQL/MariaDB: `SLEEP()`
    *   PostgreSQL: `pg_sleep()`
    *   Microsoft SQL Server: `WAITFOR DELAY`
    *   Oracle: `dbms_pipe.receive_message()`

---

## 🚀 Exploitation

### Step 1: Fingerprint and Trigger the Delay
*   **Initial Attempt:** Injected `' || (SELECT sleep(20))--`. The response returned in ~5 seconds, which was likely normal server latency or a syntax error, meaning it did not execute the 20-second sleep.
*   **Successful Payload (PostgreSQL):**
    ```sql
    ' || (SELECT pg_sleep(20))--
    ```
*   **Result:** The HTTP request hung and took over 20 seconds to receive a response, confirming that the backend database is **PostgreSQL** and is vulnerable to time-based blind SQL injection.

---

## 🛠️ Steps to Reproduce
1. **Access** the lab environment.
2. **Capture** the GET request in Burp Suite (e.g., browsing the home page) and locate the `TrackingId` cookie.
3. **Inject Payload:** Modify the `TrackingId` cookie value to append the PostgreSQL time delay payload: `' || (SELECT pg_sleep(10))--`.
4. **Send and Observe:** Send the request in Burp Repeater. Look at the bottom-right corner of the Repeater tab to monitor the response time (in milliseconds).
5. **Verify:** The application will take 10+ seconds to respond.
6. 🎉 **Lab is solved!**
