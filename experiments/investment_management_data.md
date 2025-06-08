# Script of exercising investment management capabilities

## Credits


### Setup Server

- Run `python -m src.test_data.populate_db --data financial`
- Run `python -m src.sqlite-explorer-fastmcp-mcp-server.main`

### Setup Client
Use a separate mcp client rather than the same VSCode project, or Github Copilot will just read the code and not call the server!
- Use the System Prompt at `experiments\copilot-instructions.md`

#### Tables
The following prompt should not need to access the MCP Server.

```txt
What are the tables available within the SQLite MCP server?
The SQLite MCP server has the following tables:

- account: Stores account information.
  - acct_cd (TEXT, PRIMARY KEY): Account code.
  - mkt_val (REAL): Market value.
- issuer: Stores issuer information.
  - issuer_cd (TEXT, PRIMARY KEY): Issuer code.
- security: Stores security information.
  - sec_id (TEXT, PRIMARY KEY): Security ID.
  - issuer_cd (TEXT): Issuer code (foreign key to issuer).
  - cusip (TEXT): CUSIP.
  - mkt_price (REAL): Market price.
  - beta_value (REAL): Beta value.
  - duration (REAL): Duration.
- investment: Stores investment information.
  - acct_cd (TEXT, PRIMARY KEY): Account code (foreign key to account).
  - sec_id (TEXT, PRIMARY KEY): Security ID (foreign key to security).
  - weight (REAL): Weight.

```

#### Single table query

```txt
Display the largest investment per account by weight.

Ran read_query
{
  "fetch_all": true,
  "query": "SELECT\n    t.acct_cd,\n    t.sec_id,\n    t.weight\nFROM\n    (SELECT\n        acct_cd,\n        sec_id,\n        weight,\n        RANK() OVER (PARTITION BY acct_cd ORDER BY weight DESC) as rnk\n    FROM\n        investment) AS t\nWHERE\n    t.rnk = 1;"
}

Returned table

```

#### Analytic calculation single table query

```txt
Display the market weight and contribution to duration for investments in the security with ID "SEC0016" by account?

Ran read_query
{
 "fetch_all": true, "query": "SELECT \n    i.acct_cd,\n    i.weight AS market_weight,\n    (i.weight * s.duration) AS contribution_to_duration\nFROM \n    investment i\nJOIN \n    security s ON i.sec_id = s.sec_id\nWHERE \n    i.sec_id = 'SEC0016';" 
 }

Returned table

```

#### Subquery multiple tables

```txt
Display the issuer per account with the largest net investment by weight.

Ran read_query
{
  "fetch_all": true,
  "query": "SELECT\n    t.acct_cd,\n    t.issuer_cd,\n    t.total_weight\nFROM\n    (SELECT\n        i.acct_cd,\n        s.issuer_cd,\n        SUM(i.weight) AS total_weight,\n        RANK() OVER (PARTITION BY i.acct_cd ORDER BY SUM(i.weight) DESC) as rnk\n    FROM\n        investment i\n    JOIN\n        security s ON i.sec_id = s.sec_id\n    GROUP BY\n        i.acct_cd, s.issuer_cd) AS t\nWHERE\n    t.rnk = 1;"
}

Returned table

```

#### Constraint based reasoning

```txt
Display the CUSIP for a security held in account ACCT010 for issuer ISS_UOQI.

Answer included 89CRZGE4V.

If I buy 100 shares of 89CRZGE4V in ACCT010, how much market value would that be before and after the purchase?

Answer included $3,986,556.37 + $39,352.00 = $4,025,908.37.

What is the most weight of 89CRZGE4V that I could buy in exchange for cash in account ACCT010 without
- buying more than 5%,
- depleting the cash balance below 1%,
- extending account duration beyond 5.9, and
- extending the issuer weight beyond 16%?

Answer

Constraints:
- Maximum Purchase of 89CRZGE4V: 5% of the portfolio weight.
- Minimum Cash Balance: 1% of the portfolio weight. This means you can use a maximum of 10% - 1% = 9% of your cash weight for purchases.
- Maximum Account Duration: 5.9. The current duration is 4.870625. The allowable increase in duration is 5.9 - 4.870625 = 1.029375.
- Maximum Issuer Weight (ISS_UOQI): 16%. The current issuer weight is 62.26%. This constraint is already violated, meaning you cannot increase your holdings in any security from issuer ISS_UOQI, including 89CRZGE4V, without further exceeding this limit.

Conclusion:
Based on the existing issuer weight of 62.26% for ISS_UOQI in account ACCT010, which already exceeds the 16% limit, you cannot buy any more shares of 89CRZGE4V (which is issued by ISS_UOQI) without further violating this constraint.

Therefore, the most weight of 89CRZGE4V that you could buy under these conditions is 0%.

```


