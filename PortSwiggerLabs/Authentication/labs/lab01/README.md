>>> Target -> Lab: Username enumeration via different responses

----
**Vulnerability**: No rate limiting
**Goal**: Enumerate a valid username, brute-force its password, and log in.

----


### Steps:
1. #### Open the lab and perform a test login.
   ![alt text](image.png)

2. #### Capture the request in Burp Suite and send it to Intruder.

3. #### First, enumerate usernames:
   ![alt text](image-1.png)
   - The lab provides username and password wordlists:
   ![alt text](image-2.png)

4. #### Identify the valid username:
     ![alt text](image-3.png)

5. #### Then brute-force the password for this username in Intruder:
    ![alt text](image-4.png)

6. #### The valid username and password are:
    - `application`:`iloveyou`
    ![alt text](image-5.png)
7. #### Log in with these credentials.

8. #### The lab is solved.
    ![alt text](image-6.png)



