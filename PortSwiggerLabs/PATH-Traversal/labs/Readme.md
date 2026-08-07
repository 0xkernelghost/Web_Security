# Path Traversal

> A practical introduction to finding, understanding, and reporting path traversal vulnerabilities during authorised web security testing.

---

## What Is Path Traversal?

Path traversal, also called **directory traversal**, is a vulnerability that lets an attacker access files or directories outside the location intended by the application.

It happens when user input is used to construct a filesystem path without safely validating the final, resolved path.

```text
Application expects:  /var/www/images/product.jpg
Attacker supplies:    ../../../etc/passwd
Resolved path:        /etc/passwd
```

The `../` sequence means “go up one directory”. By repeating it, an attacker may escape the intended directory.

---

## How It Works

```text
User-controlled input
        ↓
Application builds a path
        ↓
Filesystem resolves ../, encodings, or absolute paths
        ↓
Application reads, writes, or deletes an unintended file
```

### Vulnerable Logic

```python
# Never use user input directly in a filesystem path.
path = "/var/www/uploads/" + request.args["file"]
return open(path, "rb").read()
```

If `file` is `../../../etc/passwd`, the application can leave `/var/www/uploads/`.

---

## Where You Can Find It

Look for any feature that accepts a filename, path, archive entry, or resource identifier.

| Area | Typical examples |
| --- | --- |
| File downloads | `download?file=report.pdf` |
| Images and media | `image?filename=photo.jpg` |
| Document viewers | PDF, CSV, invoice, or report preview |
| Templates and themes | `template=default`, `theme=dark` |
| Log / backup viewers | `log=app.log`, backup restore/export |
| File upload and extraction | ZIP/TAR import, archive extraction (**Zip Slip**) |
| APIs | JSON fields such as `{"path":"invoice.pdf"}` |
| Static-file handlers | Misconfigured web-server aliases or routes |

Common parameter names:

```text
file · filename · path · image · img · document · download · template · page
```

---

## Types of Path Traversal

| Type | What happens | Example impact |
| --- | --- | --- |
| Arbitrary file read | Application returns a file outside the intended folder | Source code, configuration, logs, secrets |
| Arbitrary file write | An attacker-controlled path is used when saving a file | Overwrite application files or configuration |
| Arbitrary file deletion | A path is trusted in a delete operation | Delete data or application files |
| Archive traversal / Zip Slip | An archive entry such as `../../file` escapes during extraction | Write files outside the extraction directory |
| Absolute-path injection | A complete OS path overrides the expected base path | Read an unintended local file |
| Web-server path normalisation flaw | Server normalises URL paths incorrectly | File exposure; sometimes code execution |

> Path traversal is primarily a file-access problem. Whether it becomes critical depends on the process permissions and the accessible files.

---

## Impact

| Impact | Examples |
| --- | --- |
| Information disclosure | `/etc/passwd`, source code, log files, environment details |
| Secret exposure | API keys, database passwords, cloud credentials, private keys |
| Account compromise | Exposed session data or configuration enables further access |
| File overwrite / deletion | Application outage, configuration tampering, defacement |
| Remote code execution | A written file reaches an executable location, or a server-side handler executes it |

Severity ranges from **medium** to **critical**. A read-only issue in a restricted container may have lower impact; unauthenticated access to secrets or arbitrary writes to a web root can be critical.

---

## Real-World CVE Examples

| CVE | Product | What it demonstrates |
| --- | --- | --- |
| [CVE-2021-41773](https://nvd.nist.gov/vuln/detail/CVE-2021-41773) | Apache HTTP Server 2.4.49 | A URL path-normalisation flaw enabled traversal outside aliased directories; CGI configuration could turn the issue into RCE. |
| [CVE-2021-42013](https://nvd.nist.gov/vuln/detail/CVE-2021-42013) | Apache HTTP Server 2.4.50 | The initial fix was incomplete; traversal and possible RCE remained under certain configurations. |
| [CVE-2018-13379](https://nvd.nist.gov/vuln/detail/CVE-2018-13379) | Fortinet FortiOS / FortiProxy SSL VPN | Unauthenticated crafted requests could download system files through a traversal flaw. |
| [CVE-2022-4030](https://nvd.nist.gov/vuln/detail/CVE-2022-4030) | Simple:Press WordPress plugin | A low-privileged user could manipulate a file path during avatar deletion, demonstrating the destructive impact of traversal. |

---

## High-Level Testing Methodology

```text
1. Map all file-related functionality and identify controllable values.
2. Capture a normal request and establish a baseline response.
3. Test whether the value accepts relative traversal or absolute paths.
4. If filtered, evaluate normalisation, encoding, separator, and suffix handling.
5. Confirm with predictable, in-scope proof content—not status codes alone.
6. Assess the application account's filesystem permissions and accessible data.
7. Document a minimal reproducible request, evidence, impact, and remediation.
```

For payload patterns, bypasses, tools, technology notes, and a detailed workflow, see [Cheatsheet.md](Cheatsheet.md).

---

## Secure Design and Remediation

The strongest solution is to avoid accepting filesystem paths from users. Use an allowlisted logical identifier mapped to a server-side file.

```python
FILES = {"invoice-2026": "invoice-2026.pdf"}
filename = FILES.get(request.args.get("id"))
if filename is None:
    abort(404)
```

When a relative path is genuinely required, canonicalise it and confirm that the resolved path remains under one fixed base directory.

```python
from pathlib import Path

BASE = Path("/srv/app/public-files").resolve()
candidate = (BASE / user_input).resolve()

if BASE not in candidate.parents or not candidate.is_file():
    raise ValueError("Invalid file request")
```

```text
[ ] Prefer allowlisted identifiers instead of paths
[ ] Resolve / canonicalise before the access-control check
[ ] Enforce containment within an approved base directory
[ ] Never rely on stripping ../ or checking file extensions alone
[ ] Use least-privilege filesystem permissions
[ ] Keep secrets outside web-accessible directories
[ ] Return generic errors and log rejected path attempts
```

---

*Use these techniques only on systems you own or are explicitly authorised to test.*
