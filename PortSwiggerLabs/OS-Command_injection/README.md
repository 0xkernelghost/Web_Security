# OS Command Injection

> Professional study notes for authorised security testing and PortSwigger Web Security Academy labs.

---

## Contents

1. [Overview](#overview)
2. [How It Works](#how-it-works)
3. [Where It Appears](#where-it-appears)
4. [Impact](#impact)
5. [Finding Command Injection](#finding-command-injection)
6. [Blind Command Injection](#blind-command-injection)
7. [Safe Testing Workflow](#safe-testing-workflow)
8. [Defence and Mitigation](#defence-and-mitigation)
9. [PortSwigger Lab Map](#portswigger-lab-map)

---

## Overview

**OS command injection** occurs when an application builds an operating-system command with untrusted input and executes it through a shell or command interpreter. An attacker may alter the intended command and cause the server to run additional commands with the privileges of the application process.

It is closely related to **CWE-78: Improper Neutralization of Special Elements used in an OS Command**. It is also called *shell injection* or *command injection*.

```text
User input  ──► application builds command ──► shell interprets it ──► OS executes it
                    ^
                    └── unsafe trust boundary
```

> Only test systems you own or are explicitly authorised to assess. The examples here use harmless proof commands such as `whoami`, `id`, and `ping` for learning and lab validation.

### Command injection compared with other injection flaws

| Issue | What is executed? | Typical vulnerable sink |
| --- | --- | --- |
| OS command injection | A shell or OS command | `system()`, `exec()`, `Runtime.exec()` with a shell, `child_process.exec()` |
| SQL injection | A database query | Dynamic SQL string |
| Server-side template injection | Template expressions or code | Unsafe template rendering |

The shared issue is that untrusted data is treated as part of an instruction instead of as data.

---

## How It Works

### Vulnerable pattern

An application might run `ping` against a host supplied by the user:

```php
// Vulnerable: the shell receives one string containing untrusted input.
$host = $_POST['host'];
system("ping -c 1 " . $host);
```

If the input contains a shell control operator, the shell may parse it as another command rather than as part of the hostname.

```text
Expected command:  ping -c 1 example.com
Unsafe input:      example.com ; whoami
Resulting command: ping -c 1 example.com ; whoami
```

### Why the shell matters

Many process-execution APIs are safe only when they invoke a program directly and pass arguments as a list. Risk increases when code invokes a shell, for example `/bin/sh -c ...`, `cmd.exe /c ...`, `shell=True`, or Node.js `exec()`.

```text
Safer:  program + explicit argument array  → no shell grammar is parsed
Risky:  one command string through a shell → separators and substitutions may be parsed
```

Escaping individual characters is not a reliable primary defence: syntax changes by platform, quoting context, encoding, and interpreter. Avoid invoking a shell whenever possible.

---

## Where It Appears

Look for features that call an operating-system utility or wrap an external tool.

| Feature | Typical backend action | Inputs worth reviewing |
| --- | --- | --- |
| Network diagnostics | `ping`, `nslookup`, `traceroute` | Hostname, IP address, interface |
| File conversion | Image, document, archive utilities | Filename, path, conversion options |
| Media processing | Video or audio command-line tools | Source URL, filename, profile |
| Backup and export | Archive, database dump, sync tools | Destination, database name, filters |
| PDF or report generation | Headless browser or converter | URL, template name, output path |
| Deployment and administration | Git, package, service utilities | Branch, environment, service name |
| Email and notifications | Mail tools or scripts | Address, subject, attachment path |

### High-signal code patterns

Trace request-controlled values through these common APIs:

```text
PHP:        system, exec, shell_exec, passthru, popen, proc_open
Python:     os.system, os.popen, subprocess(..., shell=True)
Node.js:    child_process.exec, execSync, spawn(..., { shell: true })
Java:       Runtime.exec with a shell; ProcessBuilder("sh", "-c", userInput)
.NET:       ProcessStartInfo with a shell command or untrusted arguments
Ruby:       system(string), backticks, %x(), Open3 with a shell string
```

An API name is not proof of a vulnerability. Confirm that user-controlled data reaches a shell-parsed command string and that no strict allowlist or safe argument API is in use.

---

## Impact

Impact depends on command context, process privileges, network access, and containment controls. Successful exploitation can allow an attacker to:

- Read files and environment variables available to the application.
- Access internal services reachable from the application host.
- Alter or delete data accessible to the process.
- Execute programs as the web-service account.
- Use the server as a foothold for lateral movement.
- Disrupt availability through expensive or repeated commands.

| Context | Likely impact |
| --- | --- |
| Low-privilege, isolated container | Data exposure or disruption within that workload |
| Application host with secrets in environment variables | Credential theft and access to connected services |
| Privileged account or weak segmentation | Potential full host compromise and lateral movement |

Because execution occurs on the server, command injection is often **high or critical** after reachability and privileges are confirmed.

---

## Finding Command Injection

### 1. Map inputs and establish a baseline

Capture a normal request in Burp Suite and identify values that could influence a system call:

```text
Form fields · query parameters · JSON values · headers · cookies
File names · archive entries · imported configuration · URL parameters
```

Send a valid value first and record the response body, status, time, and any output shown by the application.

### 2. Test shell metacharacters methodically

Shell syntax differs between Unix-like shells and Windows `cmd.exe`. Try one operator at a time and compare it with the baseline.

```text
Unix-like:  ;  |  &  &&  ||  $(...)  `...`
Windows:    &  &&  |  ||
```

Do not treat a changed response as proof. Validation errors, filters, and reflected values can create false positives. Confirm with a reliable execution signal.

### 3. Confirm execution safely

Use a harmless command appropriate to the likely platform:

```text
Unix-like:  whoami     id
Windows:    whoami     ver
```

| Channel | Evidence |
| --- | --- |
| Direct | Command output appears in the HTTP response. |
| Error-based | A shell or utility error changes consistently with parsing. |
| Time-based | A controlled delay is consistently measurable. |
| Out-of-band | A controlled interaction reaches an authorised collaborator endpoint. |

### 4. Record the real context

Document the parameter, request method, effective separator, OS family, application user, confirmation channel, and authentication requirements. This makes the issue reproducible without overstating impact.

---

## Blind Command Injection

Blind command injection means a command executes but its output is not returned in the HTTP response. Confirmation relies on an indirect signal.

### Time delay

Compare multiple baseline requests with multiple delayed requests; account for network jitter and server load.

```text
Unix-like:  ; sleep 5
Windows:    & timeout /t 5 /nobreak
```

### Output redirection

In an authorised lab or controlled environment, harmless output may sometimes be redirected to an application-readable location. This is environment-specific and should never replace a proper execution proof or access control.

### Out-of-band interaction

For PortSwigger labs, Burp Collaborator can verify a DNS or HTTP interaction without reflected output. Use a unique payload, send one request, and correlate the interaction with its time and request ID.

---

## Safe Testing Workflow

```text
1. Define scope and obtain authorisation
2. Capture a normal request and preserve a baseline
3. Identify the likely OS and command context
4. Test one harmless separator and proof command at a time
5. Confirm through direct, timing, or out-of-band evidence
6. Document reproducible evidence and effective privileges
7. Stop after validation unless the rules of engagement permit further testing
```

### False-positive checks

- Repeat the same test and compare it with a clean baseline.
- Ensure a delay is not caused by application retries, rate limits, or network latency.
- Confirm output is produced by the server, not merely reflected input.
- Check whether validation rejects the payload before the vulnerable sink is reached.
- Do not infer root or administrator access from a successful command without evidence.

---

## Defence and Mitigation

### Preferred solution: avoid OS commands

Use a language-native library or service API instead of a shell utility whenever possible. For example, use a DNS library rather than running `nslookup`.

### If process execution is required

1. **Do not invoke a shell.** Use an API that accepts the executable and each argument separately.
2. **Allowlist inputs.** Validate against a narrow, business-appropriate set of known values.
3. **Keep arguments fixed.** Do not let a request choose flags, executable paths, or expressions.
4. **Use least privilege.** Run under a dedicated, unprivileged service account with restricted filesystem and network access.
5. **Limit resources.** Set timeouts and constrain process output, concurrency, memory, and CPU.
6. **Log safely.** Record rejected input and failures without exposing sensitive data or command output to users.

```python
# Safer: no shell; each argument is passed separately.
import subprocess

host = validated_host_from_allowlist()
result = subprocess.run(
    ["ping", "-c", "1", host],
    check=True,
    capture_output=True,
    text=True,
    timeout=5,
)
```

> Argument arrays reduce shell-injection risk, but validation remains necessary. Some utilities interpret their own options; use `--` to end options where supported and do not accept arbitrary flags.

| Risk | Primary control | Supporting control |
| --- | --- | --- |
| Shell metacharacters are interpreted | No shell; argument array | Strict allowlist validation |
| Attacker selects executable or flags | Fixed executable and fixed options | Use `--` where supported |
| Excessive process impact | Timeouts and resource limits | Rate limiting and queueing |
| Broad host access after compromise | Least-privilege account | Container and network segmentation |
| Vulnerability goes unnoticed | Process logs and alerting | Security testing in CI |

---

## PortSwigger Lab Map

| Lab type | Main lesson | Useful confirmation |
| --- | --- | --- |
| Simple command injection | Find a reflected output channel | `whoami` or `id` |
| Blind time-delay injection | Measure controlled execution without output | `sleep` or `timeout` |
| Blind output redirection | Find an alternate output channel | Harmless output in the lab |
| Blind out-of-band injection | Use Collaborator to detect server-side interaction | Unique DNS or HTTP callback |

## Further Reading

- [PortSwigger Web Security Academy — OS command injection](https://portswigger.net/web-security/os-command-injection)
- [OWASP — OS Command Injection Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)
- [CWE-78](https://cwe.mitre.org/data/definitions/78.html)
