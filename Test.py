import numpy as np 
import matplotlib.pyplot as plt
from Data_reader import read_prices, plot_prices, keep_complete_dates
from Portfolio import Portfolio

price_dict,time = read_prices("test_data.csv")
price_dict,time = keep_complete_dates(price_dict,time)
companies = [i for i in price_dict]
initial_prices = np.zeros(len(price_dict))
time_steps = len(price_dict[companies[0]])
for i in range(len(price_dict)):
    initial_prices[i] = price_dict[companies[i]][0]
print(companies)



N =100
test_portfolios = np.zeros(shape=(N,time_steps))
works = False

def portfolio_evolution(portfolio):
    price_matrix = np.array(list(price_dict.values()))
    return portfolio.holdings @ price_matrix

for i in range(N):
    test_portfolios[i] = portfolio_evolution(
    Portfolio(
    price_dict=price_dict,
    Initial_Bond_Holdings=0,
    Initial_Holdings=np.ones(len(initial_prices)),
    Stock_Prices=initial_prices,
    Company_Names=companies,
    Random=True,
    Initial_Value=10000,))

plt.style.use('dark_background')
#for i in range(10):
    #plt.plot(test_portfolios[i])
plt.plot( time, np.mean(test_portfolios, axis=0), color = 'red')
plt.fill_between(x=time, y1= np.mean(test_portfolios, axis=0)-np.std(test_portfolios, axis= 0), y2= np.mean(test_portfolios, axis=0)+np.std(test_portfolios, axis= 0))
plt.grid()
plt.show()
