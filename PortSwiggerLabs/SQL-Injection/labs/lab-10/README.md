## platform portswigger
### target => Lab: SQL injection UNION attack, retrieving multiple values in a single column

**where is Vuln: product category filter**

**Goal: gain admin password for login as admin**

#### analysis
##### understand the limitation
- Only one column in the original query results supports string/text data.
- Standard `UNION SELECT username, password` will fail due to column count or data type mismatch.
- Solution: We need to combine (concatenate) both values into a single column.

##### identify concatenation syntax
- Depending on the database, the string concatenation method varies:
  - Oracle / PostgreSQL / SQLite: `||` operator
  - MySQL: `CONCAT()` function
  - Microsoft SQL Server (MSSQL): `+` operator

#### Exploitation
- **Payload Logic:** Use the `||` operator to combine `username` and `password`, separated by a delimiter like `~` for readability.
- **Inject the Payload:**
  - `' UNION SELECT NULL, username || '~' || password FROM users --`
  - *Note: `NULL` is used for the first column to match the column count without causing a data type error.*

- **Expected Result:**
  - The query will return concatenated strings in the product listing.
  - Example: `administrator~password123`

#### step:
1. access the lab
2. select any product category to see the URL parameter (e.g., `category=Gifts`)
3. inject the concatenation payload into the category parameter
4. analyze the response to find the administrator's credentials in the format `username~password`
5. login as admin with the extracted username and password
6. now lab is solve
