>> ### Target Lab: 2FA broken logic

```
**Vulnerability:**
- This lab's two-factor authentication is vulnerable due to its flawed logic.

**Goal:**
- To solve the lab, access Carlos's account page. 


```


### Steps:
1. #### Open the lab.
2. #### Log in with the credentials `wiener:peter`.
3. #### Capture the requests in Burp Suite.
    - ![alt text]({FA626769-11E6-43D2-9214-0A2532D29032}.png)
    - try to remove session cookie and send 
    - ![alt text]({056DB506-7081-48D4-A307-B7F501D32EF5}.png) no cookie needed
    - log out wiener account and play in burp with login2 request

4. #### Change the verification username from `wiener` to `carlos` and send the request.
    - ![alt text]({C00CFCE8-5EB9-463D-9ABD-B51466BBFD00}.png)
    - The code is incorrect, but the request redirects to Carlos's page.
    - After changing `wiener` to `carlos`, the server generates a new code for Carlos's account.
    - Log in again with the Wiener account and submit an incorrect code for the valid pending 2FA session.
    - ![alt text]({FC118651-E216-45DD-BD44-4FE8F4CEEA91}.png) The test code is incorrect.

5. #### Send the `login2` request with the fake code to Intruder and brute-force the MFA code.
    - ![alt text]({A4136E35-8521-436E-BA48-F3EA75901B4A}.png)
    - ![alt text]({B591F3AF-3425-4553-ABBA-D49D321276DC}.png)
    - ![alt text]({6105B069-AD5A-44D0-A67B-9C50C4E4FA48}.png) set payload and change wiener to carlos and start attack

6. #### Wait while Intruder brute-forces the code.
    - ![alt text]({0B27774F-BF4A-45F5-928A-9881F245210A}.png)


7. #### After some time, the correct code will be found and the request will redirect to Carlos's page (`302 Found`).
    - ![alt text]({F0A09CEA-3787-4564-8377-F198881C589E}.png)
    - right click on the page and SHOW RESPONSE IN BROWSER 

8. #### You will see Carlos's page, which confirms that you have solved the lab.
    - ![alt text]({4252CF73-C86C-4EBC-A0BF-AAA53103A9AA}.png)






