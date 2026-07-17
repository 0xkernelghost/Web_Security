>> Target -> Lab: User ID controlled by request parameter, with unpredictable user IDs

---

**Where is Vuln**: url id parameter.

**Goal**: access the carlos account and retrieve the api key 

---

**How to reach the Goal**: 
### Steps

1. - #### Open the lab..
2. - #### login as wiener user
3. - #### i see now is unique IDs for users, so i need to find carlos id -> ![alt text](image.png)
4. - #### check comments in the page and find this -> ![alt text](image-1.png) 
5. - #### click the carlos and see -> id ![alt text](image-2.png)
6. - #### go my-account and change carlos userid get api key -> ![alt text](image-3.png) submit this
7. - #### solve the lab..... ![alt text](image-4.png)


## Check `poc.py` for automate attack and .sh and .ps1 exprimental they work exactly like python POC

