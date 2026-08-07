>> ### Target Lab: File path traversal, traversal sequences stripped non-recursively

---

**Vuln**
- in product image 

**Goal**
- Lab: File path traversal, traversal sequences stripped non-recursively

---

### Steps:
1. #### On burp proxy and see images request in proxy history.
2. #### try simple payload 
    - ![alt text](image.png)
    - they did not work 
    - try this 
    - ![alt text]({163D906E-847F-47AD-9505-52C501B36264}.png)
    - but they did not work
 
3. #### Try Non-Recursive Filter Bypass — server strips `../` only once (non-recursive)
   - Payload: `....//....//....//etc/passwd`
   - Logic: after removing inner `../`, outer `..` + `/` reforms into `../`
   - Worked!
    - ![alt text]({D5A58793-E0CD-4BD3-BEAF-5C514E5D24D6}.png)

4. #### solve the lab
    - ![alt text]({BF293529-3FB5-4483-A43B-9E6C3286DC45}.png)

`check` POC.py