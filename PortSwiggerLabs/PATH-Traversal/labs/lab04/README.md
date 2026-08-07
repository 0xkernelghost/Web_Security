### Target Lab: File path traversal, traversal sequences stripped with superfluous URL-decode

---
**Vuln**
- in product image

**Goal**
- retrieve the contents of the /etc/passwd file.

---

### Steps:
1. #### On burp proxy and see images request in proxy history.
2. #### send image request to repeater
    - try `../../../etc/passwd` and some other payloads
    - ![alt text]({52B9C194-D75A-4C8F-9E6E-01ED7F154F45}.png)
    - they did not work
    - try single URL-encoding the payload: `%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd`
    -> ![alt text]({FF23AF10-FC10-435E-8C7D-838F34B2137E}.png)
    - still did not work so use double encoding: `..%252f..%252f..%252fetc%252fpasswd`
    - ![alt text]({293997C7-469A-408B-A374-178E06972CFE}.png)
    - this worked and we can see the content of /etc/passwd file in response.
3. #### solve the lab
    - ![alt text]({37B5A59F-6F35-49DE-88CE-5B344C900CB6}.png)

**Key Takeaway:**
> Root cause = decoding AFTER filter validation instead of BEFORE.
> Filter validates a still-encoded string, but the value used in the actual
> file operation is decoded again post-validation — creating a mismatch
> between "what was checked" and "what was used".