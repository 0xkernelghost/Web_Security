>> Lab: URL-based access control can be circumvented

---- 
**Where is Vuln..** : unauthenticated admin panel
**Goal**: access the admin panel and delete the user carlos.

----

### Steps:

1. #### open lab.![alt text](image.png) already provided admin panel
2. #### click admin panel ![alt text](image-1.png)
3. #### access denied now check in burp suite ![alt text](image-2.png) there is also denied
4. #### add X-Original-URL header in host below and remove admin parameter in get -> ![alt text](image-3.png)
5. #### successfully ok 200 
6. #### now delete carlos user ![alt text](image-5.png)
7. #### solve the lab..... ![alt text](image-6.png)


## Check `poc.py` for automate attack
