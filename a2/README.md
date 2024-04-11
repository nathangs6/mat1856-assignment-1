# Assignment 2 - Probability of Default
In this assignment, I found the probability that Brookfield Renewable Partners (BEP) will default in the future.

## Running the Code
To run the code, please do the following:
- Clone this github to your computer
- In the `a2` folder, run `python -m venv env`
- Run `source env/bin/activate` if on Linux, `.\env\Scripts\Activate.ps1` if on Windows
- Run `python -m pip install -r requirements.txt`
- Run `python -m main`

## Methodology
For both methods, I need the rates for the Canadian government bonds. These are treated as the risk-free interest rates for both methods. This was implemented in assignment 1, and similar code is used here.

### CreditMetrics
For CreditMetrics, the goal is to find a Markov transition matrix, $M$, containing probabilities of moving different credit ratings at each tmie step. The form of $M$ is special as the probability of staying in default once defaulted *must be* $1$. Once $M$ is found, you can find the probability of being in default at time $T$ by computing $M^T$. In this assignment, I used two Markov states, solvency and default, so that
$$M = \begin{pmatrix} q & 1 - q \\ 0 & 1 \end{pmatrix}$$
where $q$ is the probability of staying solvent. Thus, the probability of being in default at time $T$ is $M^T_{0,1}$.

So the goal is to find $q$. To do so, we select one of BEP's bonds and find it's YTM. Then, we compute the hazard rate, $h = YTM - r$ where $r$ is the risk-free interest rate. Finally, we can get $q$ via
$$
q = \frac{e^{-h} - R}{1 - R}
$$
where $R$ is the recovery rate (assumed to be $0.5$ in this assignment).

### Merton Model
In the Merton model, we model a company's equity as a call option on its assets. If the call option is exercised, the company as defaulted. The input data we need for the Merton model is as follows:
- Number of outstanding shares ($N$)
- Stock price ($P$)
- Historical stock prices
- Debt ($K$)
- Risk-free rate ($r$)

After this, the following basic values are computed:
- Equity: $S = N \times P$
- Stock (equity) volatility: $\sigma_S$

The next step is to derive the market value of the companies assets, $V$, and the volatility of its assets, $\sigma_V$. This is done by simultaneously solving the following equation:
$$
\sigma_V = \sigma_S \frac{S}{V} \frac{\partial V}{\partial S}
$$
Here, $\frac{\partial V}{\partial S} = 1/\Delta = 1/\mathcal{N}(d_1)$ where $\mathcal{N}(\cdot)$ is the normal cumulative distribution function and
$$
d_1 = \frac{\log \frac{V}{Ke^{-rt}} + \frac{\sigma_V^2 t}{2}}{\sigma_V \sqrt{t}}
$$

Finally, with $V$ and $\sigma_V$ in hand, it can be shown that the probability of default at time $t$ is $\mathcal{N}(-d_2)$ where $d_2 = 1 - d_1$. Note that we can vary time in the formula for $d_2$ while keeping $V$ and $\sigma_V$ fixed. *In theory*, we should have specific asset value and asset volatility for each time, based on which debt expires when, but in this solution I kept it simple.

## Data
I got the data for this assignment from a variety of sources.
- Bond information: RBC Direct Investments, [Market Insiders](https://markets.businessinsider.com/?op=1)
- Historical stock prices: [Yahoo! Finance](https://ca.finance.yahoo.com/)
- Stock and company information: RBC Direct Investments

## More Information
If you'd like to learn more about this, you can see the Financial Credit Models lecture my professor gave here: [YouTube](https://www.youtube.com/@luisangelseco).