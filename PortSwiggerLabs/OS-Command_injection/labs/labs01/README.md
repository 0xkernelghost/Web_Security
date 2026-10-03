>> Target Lab: OS command injection, simple case

---
**Vuln**
- OS command injection vulnerability in the product stock checker.  

**Goal**
- execute the whoami command to determine the name of the current user. 

---

### Steps:
1. #### Open the lab..
2. #### click any product detail and check stock id  
    - ![alt text]({A528DD5D-2B2D-4D72-8A71-335EDE503CDD}.png)
    - capture the request in burp suite
    - observe the request
    - send the request to repeater
    - ![alt text]({70DB0143-8CAE-4315-8C5A-F1A2346764A2}.png)

3. #### try to simple whoami execution on the stockid parameter.
    - ![alt text]({7A422873-F9F7-46AD-9707-97C378F5AABD}.png)
    - 200 ok
4. #### Solve the lab
    - ![alt text]({745113D8-A27E-49C4-AA2B-4C5CE92A04E7}.png)

`Check` POC.py for automation.