# Crypto Blotter
*Version 0.01 Alpha*

Released as Open Source under MIT License. See LICENSE file for details.
Contributing guidelines are available on file CONTRIBUTING.md

Crypto Blotter (CB) is a portfolio tracking tool. It includes position monitoring
and other analytics. The main reason that led me to develop this tool is to
better manage cash inflows and outflows from digital positions. CB monitors
daily Net Asset Value (NAV). Similar to how a fund calculates performance.
So it's always tracking performance relative to current exposure.

### Why NAV is important?
NAV is particularly important to anyone #stackingsats since it tracks performance relative
to current capital allocated. A portfolio going from $100 to $200 may seem like it 2x
but the performance really depends if any new capital was invested or divested during
this period. NAV adjusts for cash inflows and outflows.

### Trade Pairs
Cryptoblotter is structured so that, by default, trades are included in pairs. This is similar
to accounting entries where a credit and a debit are included as separate entries.
This is helpful so you can track your positions (assets) and your cash flows.
By doing this, it's easier to see how much fiat was deployed. It's
particularly helpful in determining your historical average cost.
More info can be found here: [CSV import details](http://www.cryptoblotter.io/csvtemplate)

Readme.1st
-----------
**Please note that this is a "hobby project". There is no guarantee that the
information and analytics are correct. Also expect no customer support. Issues
are encouraged to be raised through GitHub but they will be answered on a best
efforts basis.**

Any issues, suggestions or comments should be done at Github ISSUES page.

Disclaimer: I am not a developer. Code is not optimal. Will probably run slower
than potentially possible. Code enhancements and suggestions are welcome! I am
also a beginner on GitHub so I may deviate from what is standard. If you see
potential for improvement, please let me know.


Installation instructions
----------------------------
Although Crypto Blotter can be accessed at cryptoblotter.io, we highly encourage
users to run locally. This would give the user control over database
(stored locally) and on whether on not to upgrade to new versions. When using the
online version, feel free to use a random username for privacy. Use the online
version for testing and install locally later if you prefer.

#How to install locally
'include installation details here'

Privacy
-------
Most portfolio tracking tools ask for personal information and may track
your IP and other information. By cloning CB and running locally you reduce
the risk of linkage of your IP, portfolio info and other information.

Asset and Liability tracking
-----------------------------
Different than most portfolio tracking tools, CB tracks both sides of transactions:
the crypto asset side and the fiat side. This helps in analyzing cost basis,
historical cash flows and fiat to crypto conversions along time.

NAV Tracking
-------------
Another major difference is the concept of tracking Net Asset Value (NAV).
NAV tracks performance based on amount of capital allocated. For example,
a portfolio starts at $100.00 on day 0. On day 1, there is a capital inflow
of an additional $50.00. Now, if on day 2, the Portfolio value is $200, it's
easy to conclude that there's a $50.00 profit. But in terms of % appreciation,
there are different ways to calculate performance.
CB Calculates a daily NAV (starting at 100 on day zero). In this case:


Day  | Portfolio Value*| Cash Flow  | NAV  | Performance |
-----|-----------------|------------|------|-------------|
0|$0.00|+ $100.00|100|--|
1|$110.00|+ $50.00 |110|+10.00% (1)|
2|$200.00|None|125|+25.00% (2)|

#### * Portfolio Market Value at beginning of day
#### (1) 10% = 110 / 100 - 1
#### (2) 25% = 200 / (110 + 50) - 1

Tracking NAV is particularly helpful when #stackingsats. It calculates
performance based on capital invested at any given time. A portfolio
starting at $100 and ending at $200 at a given time frame, at first sight, may
seem like is +100% but that depends entirely on amount of capital invested
along that time frame.


# FAQ
- Why include other Crypto Assets and not only Bitcoin?
We believe CB actually helps users realize the value of a Bitcoin only
portfolio. But that's our opinion. We preferred to give users the ability
to check their whole portfolio and provide them with the tools to assess how
much better (or maybe worse) they would have been with a Bitcoin only portfolio.
Most crypto investors go through a period of investing in other assets. The
quicker they realize this is a losing strategy, the better. We hope these tools
help them learn quicker.

- Why is NAV a better way to track a portfolio?
It takes into account deposits and withdraws. See table at NAV Tracking
for more info.

- Is there a mobile version available?
Not at this time.

- Do I need to run it locally or is there a website I can use?
Cryptoblotter.io has a running version but we encourage users to run locally
on their machines to better control their data.

- On the remote version at cryptoblotter.io, what kind of information is gathered?
The debug.log file logs the IP addresses accessing the website. Also, your
username is stored. We encourage users of the website to not use their real
e-mail address (use a burner only for password recovery).
