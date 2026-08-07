>> Target Lab: Offline password cracking

--- 
**Vuln**
This lab stores the user's password hash in a cookie. The lab also contains an XSS vulnerability in the comment functionality.

**Goal**
To solve the lab, obtain Carlos's stay-logged-in cookie and use it to crack his password. Then, log in as carlos and delete his account from the "My account" page. 

---



### Steps:
1. #### Open the lab.
2. #### Log in with the credentials `wiener:peter`.
3. #### Open any post's comment section and test a basic XSS payload.
    - ![alt text]({170A4B0D-841F-4CE8-A651-3031169738CF}.png)
    - ![alt text]({45F0F1AD-5233-4B38-8592-DE892B64AA1E}.png)
    - The comment contains stored XSS: ![alt text](image.png)

4. #### Steal Carlos's cookie through XSS.
    - ![alt text]({E72BCDD8-E5A5-47C9-A48C-F69CF81921D3}.png)
    - After injecting the payload, check the Exploit Server access log and wait for Carlos to visit the page.
    - When Carlos visits the page:
    - ![alt text]({45F5B9FF-32A5-4D06-9FA9-230229A59029}.png)
    - decode stay-logged-in value
    - ![alt text]({9127B231-6CEE-408D-9269-6DFD42E2F49D}.png)
    - We now have Carlos's credentials.
    - decode password hash 
    - ![alt text]({2C2774D7-C766-4403-A83D-94189CE5C7E6}.png)

5. #### Log in with Carlos's credentials and delete his account.
    - ![alt text]({51CED15D-6EBF-4231-8ED3-23CC4D79C15F}.png)

6. #### The lab is solved.
    - ![alt text]({E5CAF903-36F0-43F5-9B3A-367274120555}.png)
