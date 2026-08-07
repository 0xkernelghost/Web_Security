>> Target -> Lab: Password reset broken logic


---- 
**Vulnerability**: Password-reset logic flaw  
**Goal**: Reset Carlos's password, then log in and access the My account page.

---


### Steps: 
1. #### Open the lab.
2. #### Request a password reset for the Wiener account to understand the flow:
     ![alt text](image.png)
3. #### Confirm that the password-reset link is sent by email:
     ![alt text](image-1.png)
4. #### Check the email:
     ![alt text](image-2.png)
5. #### Open the reset link and reset the password:
    ![alt text](image-3.png)

6. #### Inspect this request in Burp Proxy and send it to Repeater:
    - ![alt text](image-4.png)
    - ![alt text](image-5.png)
7. #### Change `username=wiener` to `username=carlos` (the server does not validate the token value).
8. #### Replace the temporary token with a random value and change Carlos's password:
    - ![alt text](image-6.png)
    - ![alt text](image-7.png)
     **Change the temporary-token value in both locations.**

9. #### Log in with Carlos's new password.
10. #### The lab is solved:
     ![alt text](image-8.png)


>> ### See `poc.py` to automate this attack.
