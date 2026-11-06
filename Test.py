import numpy as np 
import matplotlib.pyplot as plt
from Data_reader import read_open_close_prices
from Portfolio import Portfolio

open_prices, close_prices, time = read_open_close_prices("test_data.csv")
companies = list(open_prices)
initial_prices = np.zeros(len(open_prices))
time_steps = len(open_prices[companies[0]])
for i in range(len(open_prices)):
    initial_prices[i] = open_prices[companies[i]][0]



N =100
test_portfolios = np.zeros(shape=(N,time_steps))
works = False

def portfolio_evolution(portfolio):
    price_matrix = np.array([open_prices[c] for c in companies])
    return portfolio.holdings @ price_matrix

for i in range(N):
    test_portfolios[i] = portfolio_evolution(
    Portfolio(
    open_price_dict=open_prices,
    close_price_dict=close_prices,
    Initial_Bond_Holdings=0,
    Initial_Holdings=np.ones(len(initial_prices)),
    Stock_Prices=initial_prices,
    Company_Names=companies,
    Random=True,
    Initial_Value=10000,))

original_portfolio = Portfolio(
    open_price_dict=open_prices,
    close_price_dict=close_prices,
    Initial_Bond_Holdings=0,
    Initial_Holdings=np.ones(len(initial_prices)),
    Stock_Prices=initial_prices,
    Company_Names=companies,
    Random=True,
    Initial_Value=10000,)

Value_test_portfolios = np.array([Portfolio(
    open_price_dict=open_prices,
    close_price_dict=close_prices,
    Initial_Bond_Holdings=0,
    Initial_Holdings=original_portfolio.holdings,
    Stock_Prices=initial_prices,
    Company_Names=companies,
    Random=False,
    Initial_Value=original_portfolio.value,) for i in range(5) ])
intervals = [3, 5,6,7,9]
Value_test_portfolio_histories = np.zeros(shape= (5,time_steps))
for j in range(5):
    for i in range(time_steps):
        to_buy, to_sell = set(), set()

        if i >= intervals[j] + 1 and (i + 1) % 7 == 0:
            to_buy, to_sell = Value_test_portfolios[j].naive_stock_valuation(time_step=i, check_interval = intervals[j])

        Value_test_portfolios[j].update_Portfolio(time_step =i, to_buy=to_buy, to_sell=to_sell)

        # Record at today's open, consistently with the buy-and-hold curves.
        current_prices = np.array([open_prices[c][i] for c in companies])
        Value_test_portfolio_histories[j][i] = (
        Value_test_portfolios[j].holdings @ current_prices
        + Value_test_portfolios[j].bonds)

        
plt.style.use('dark_background')
#for i in range(10):
    #plt.plot(test_portfolios[i])
plt.plot( time, np.mean(test_portfolios, axis=0), color = 'red', label = 'market average')
for i in range(5):
    plt.plot(time, Value_test_portfolio_histories[i], label = f'naive trading stragey ({intervals[i]})')
plt.fill_between(x=time, y1= np.mean(test_portfolios, axis=0)-np.std(test_portfolios, axis= 0), y2= np.mean(test_portfolios, axis=0)+np.std(test_portfolios, axis= 0), label = 'Martket std')
plt.grid()
plt.legend()
plt.title('Test of same portfolio with random lookback')
plt.show()