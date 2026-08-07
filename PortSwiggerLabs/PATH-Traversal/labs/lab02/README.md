>> Target Lab: File path traversal, traversal sequences blocked with absolute path bypass

---

**Vuln**
- This lab contains a path traversal vulnerability in the display of product images. 
**Goal**
-  retrieve the contents of the /etc/passwd file. 

---


`note:` `The application blocks traversal sequences but treats the supplied filename as being relative to a default working directory.`

#### Steps:
1. #### On burp proxy and see images request in proxy history.
2. #### send simple payload bcz the application blocks traversal sequences but treats the supplied filename as being relative to a default working directory. 
    - /etc/passwd

3. #### we can see the content of /etc/passwd file in response.
    - ![alt text]({26A826C1-FC7F-4A60-8D9C-B67873332E29}.png)


4. #### solve the lab
    - ![alt text]({662BD3D3-C892-45B7-9150-F6B7A4A12F67}.png)


`check` POC.py