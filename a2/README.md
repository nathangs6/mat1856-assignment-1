# Assignment 2 - Probability of Default
In this assignment, I found the probability that RBC will default in the future.

## RBC Financials
Here are some financials I needed to gather from RBC's financial statements. Data can be found [here](https://www.rbc.com/investor-relations/financial-information.html):
- Shares Out: 1,408,257,000
- Liabilities: 1,857.917B
- Current Debt: 1,241.168B (deposits)

## Methodology - Merton Model
The method for the Merton method is as follows,
- First, we gather some data:
    - Equity = (Shares Out) * (Share Price) = (1,408,257,000) * 135.17 = 190.354B
    - Assets = Equity + Liability (Accounting Equation) = 2,048.271B
    - Current Debt: from financials
    - Future Debt (Strike Price) = (Current Debt) * e^(Risk-Free Interest Rate)