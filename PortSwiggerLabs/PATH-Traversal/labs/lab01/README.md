>> ### Target Lab: File path traversal, simple case

--- 
**vuln**
- This lab contains a path traversal vulnerability in the display of product images. 

**Goal**
-  retrieve the contents of the /etc/passwd file.

---

### Steps:
1. #### on burp proxy 
2. #### and open the lab..
3. #### capture page load requests
    - ![alt text]({28CD395F-8320-4996-8597-7C77DA3300A5}.png)
    - send any jpg  request to repeater 
4. #### try simple traversal payloads
    - ![alt text](image.png)
    - no such file 
    - try ../etc/passwd
    - nothing work 
    - so i try remove the .jpg suffix and try /../../../etc/passwd
    - yes thats work 
    - ![alt text]({6ABDD464-0F6C-4651-A87E-5B55747E49B3}.png)

5. #### Solve the lab 
    - ![alt text]({5A9A1332-8F7D-40AB-AA44-E31908D4648A}.png)


`Check` POC.py