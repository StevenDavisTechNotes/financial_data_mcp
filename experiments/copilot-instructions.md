Please use your mcp servers available, and do not write code for the terminal.  If the mcp servers cannot provide the necessary information, then please say so and stop.
Please use subqueries instead of CTE's in SQL.

### SQLite MCP server

The tables available within the SQLite MCP server are:
- account:
  - acct_cd (TEXT, PRIMARY KEY): Account code.
  - mkt_val (REAL): Market value.
- issuer:
  - issuer_cd (TEXT, PRIMARY KEY): Issuer code.
- security:
  - sec_id (TEXT, PRIMARY KEY): Security ID.
  - issuer_cd (TEXT): Issuer code foreign key to issuer
  - cusip (TEXT): CUSIP.
  - mkt_price (REAL): Market price.
  - beta_value (REAL): Beta value.
  - duration (REAL): Duration.
- investment:
  - acct_cd (TEXT, PRIMARY KEY): Account code which is a foreign key to account
  - sec_id (TEXT, PRIMARY KEY): Security ID which is a foreign key to security
  - weight (REAL): Weight.

The cash balance of an Account is recorded as an investment in the security with CUSIP 'CASH'.
The contribution to duration for an investment is the product of the weight and the duration of the security.
The contribution to beta for an investment is the product of the weight and the beta value of the security.
The total duration for an account is the sum of the contributions to duration for all investments in that account.
The total beta for an account is the sum of the contributions to beta for all investments in that account.
