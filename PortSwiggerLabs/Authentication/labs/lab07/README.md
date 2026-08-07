>> ###  Target Lab: Username enumeration via account lock

```
**Vulnerability:**
- This lab is vulnerable to username enumeration. It uses account locking, but this contains a logic flaw.

**Goal:**
- To solve the lab, enumerate a valid username, brute-force this user's password, then access their account page. 


```

###  Steps:
1. #### Open the lab.
2. #### Submit random credentials on the login page and capture the request in Burp Suite.
3. #### Send the request to Intruder and set a username list as the payload.
    - The lab provides the username and password lists.
4. #### set payload with cluster bomb 
    - ![alt text]({34BEB7CD-61C8-4D30-88F5-E90508865B13}.png)

```markdown 
- Password left as "Null payload": we don't need real guesses here,
- just enough failed attempts to trigger the account lock.
-  Null payload = sends the same empty-password request 5 times per username.
-  Even a correct password wouldn't matter, since Position 2 stays empty/null.
-  Cluster bomb chosen because it tries every username with all 5 attempts
- (not aligned pairs like Pitchfork) - needed to lock every real username.

```

5. #### Start the attack and check each username's response length.
    - ![alt text]({A7298BC4-E0DD-4752-953B-470C5CB40A14}.png)

6. #### Once you have a valid username, brute-force the password.
    - ![alt text]({F75DEC0C-3B21-452B-95DF-D83BFA7F1F33}.png) 

7. #### Log in with the valid username and password, then open the account page.
    - ![alt text]({47D63070-64E5-473F-9724-A490BFA07808}.png)

8. #### Congratulations! You have successfully completed the lab.
    - ![alt text]({286C3CE6-31A3-46D1-B1D6-855CF6AB8FE3}.png)


Important note: `If valid credentials do not immediately open the account page, submit them three or four more times. Then inspect and render the response after the brute-force attack.`
