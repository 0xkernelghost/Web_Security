>>> ### Target Lab: Brute-forcing a stay-logged-in cookie

---
**Vulnerability:**
- This lab allows users to stay logged in after closing their browser session. The cookie used for this functionality is vulnerable to brute-forcing.

**Goal**
- To solve the lab, brute-force Carlos's cookie and access his My account page.

---

### Steps:
1. #### Open the lab.
2. #### Log in with `wiener:peter` and capture the request in Burp Suite.
    - ![alt text](image.png)
3. #### I see stay log in value 
    - ![alt text]({3E56A8A7-124C-4544-9D09-AD091CDE7641}.png)
    - Decode the value from Base64.
    - ![alt text]({7B275C4A-AF03-4B4A-9A72-D9643BEEFD8C}.png)
    - wiener and password (md5 hash)
    ```like this base64(wiener:md5(peter))```

4. #### Send the request to Intruder for brute-forcing.
    - ![alt text]({11993184-B17E-464A-9F7A-B1278BFD45B1}.png)
    - remove session cookie and add stay-logged-in cookie
    - remove ?id=wiener -> ![alt text]({1643507B-C088-4B38-B868-64A7A3965602}.png)
    - Paste the password list provided by the lab.
    - and add processing rules
    - start attack and check the response

5. #### and now 
    - ![alt text]({D589F045-A8D7-4EDA-B8F0-D4F2E017A86A}.png)
    - A `200 OK` response indicates that the lab is solved and Carlos's page is accessible.
    - double check -> ![alt text]({A8ECEEAB-C0D5-435A-9ED5-1CD4F50B7239}.png)
    - solve the lab

- ![alt text]({EDE0F391-3A91-445E-844E-24BFF6A729A8}.png)



``check`` POC.py

```python 


python .\POC.py "https://0a7200470423125282db33c6005e0047.web-security-academy.net"
Brute-force Carlos's password
Carlos's password: `matrix`

```
