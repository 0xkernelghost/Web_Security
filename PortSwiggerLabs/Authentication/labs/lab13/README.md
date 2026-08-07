>> ### Target Lab: Broken brute-force protection, multiple credentials per request

---

**Vulnerability**
- This lab is vulnerable due to a logic flaw in its brute-force protection.

**Goal**
- Brute-force Carlos's password, then access his account page.

---


### Steps:
1. #### Open the lab.
2. #### Click My account, submit a random value, and capture the request in Burp Suite.
    - ![alt text]({88F2A697-B6DD-419E-A958-84B85D0ACE3B}.png)
    - The login request contains credentials in JSON format.

3. #### Add another value to the password field.
    - ![alt text]({542C58A7-B9D2-4887-8CDB-33ABCEFBF5CA}.png)
    - Send the request and render the response.
    - ![alt text]({2E10BFAE-9378-4BCF-B6CD-B0B501C3A803}.png) - Invalid credentials.
    - The response is `200 OK`, which exposes the logic flaw.
    - ![alt text]({CCC72B2C-3EEC-49F9-9CD5-90754766DD96}.png)

4. #### Add all passwords provided by the lab to the password array.
    - ![alt text]({14DCAD56-2A1F-4F01-A3C8-8C2465B1CB58}.png)
    - Change the username to `carlos` and send the request.
    - ![alt text]({A3F1D234-251E-4390-B039-B7963835B08C}.png)
    - copy session cookie -> on 302 response `P2oo4pnjDIQp969Efg3Ijs4T1JEf89VZ`
    - and paste in browser cookie  
    - ![alt text]({E271B758-033F-4F9F-9A91-F170DE3FEEDC}.png) 
    - Click My account to view Carlos's account page.

5. #### Congratulations! You have successfully brute-forced Carlos's password and accessed his account page.
    - ![alt text]({0F513B1A-47B7-48AF-B886-0E8A86688163}.png)
