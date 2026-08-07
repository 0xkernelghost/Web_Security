>> ### Target Lab: Password brute-force via password change

---
**Vulnerability**
- This lab's password change functionality makes it vulnerable to brute-force attacks.
**Goal**
- Use the candidate password list to brute-force Carlos's account and access his "My account" page.

---

### Steps:
1. #### Open the lab.
2. #### Log in to the Wiener account.
3. #### After logging in, open the password-change page.
    - ![alt text](image.png)
    - password change func...
4. #### Change Wiener's password, capture the request, and send it to Repeater.
    - ![alt text]({EE563506-17F4-4B12-B043-E429DE2304F7}.png)

5. #### Change `peter` to a test password such as `hello`.
    - ![alt text]({76DBC6D5-D105-4E26-9CC4-119B5514E255}.png)

6. #### The current password is correct, but the new passwords do not match:
    - ![alt text]({37CA5197-325A-4966-A2FA-F9D63D7E506C}.png)

7. #### bug reason
    - server trusts the username field from the form instead of checking the session
    - so changing username=carlos targets his account from my own session
    - An incorrect current password produces: "Current password is incorrect".
    - A correct current password (even when the new passwords mismatch) produces: "New passwords do not match".
    - this difference lets us brute-force carlos's password without changing it

8. #### Send the request to Intruder, set the current-password payload to the provided password list, and change the username to `carlos`.
    - ![alt text]({B36C9DF4-9C65-41C6-94BC-93C5F90F1607}.png)

9. #### The current password for Carlos is `michael`.
    - ![alt text]({D0D3B012-B5CC-4605-9CF9-C1A51C1B2B58}.png)

10. #### Log in with this password.
    - ![alt text]({817C08D2-55A8-4E5B-8FD0-5A68CDDA19B8}.png)
11. #### Solve the lab 







