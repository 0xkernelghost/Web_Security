>> Lab: Method-based access control can be circumvented

----
**Vulnerability**: Admin promotion endpoint (method-based access control bypass)

**Goal**: Promote the user `wiener` to the administrator role.

---

### Steps:

1. #### Open the lab.
2. #### Log in as an administrator. ![alt text](image.png)
3. #### Promote `carlos` to the admin role. -> ![alt text](image-1.png)
4. #### Capture this promotion request in Burp Suite. -> ![alt text](image-2.png)
5. #### Log out of the admin account, log in as `wiener`, and obtain `wiener`'s session cookie. ![alt text](image-3.png)
6. #### Replace the session cookie in the captured admin promotion request with `wiener`'s cookie, modify the request method (e.g., from POST to GET), and send it. -> ![alt text](image-4.png)
7. #### The lab is successfully solved, and you now have admin privileges. -> ![alt text](image-5.png)

----

>> ### Check `poc.py` for automated exploitation


