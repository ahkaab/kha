import numpy as np 
import matplotlib.pyplot as plt
from Data_reader import read_prices, plot_prices
from Portfolio import Portfolio
price_dict = read_prices("test_data.csv")
companies = [i for i in price_dict]
initial_prices = np.zeros(len(price_dict))
time_steps = len(price_dict[companies[1]])
for i in range(len(price_dict)):
    initial_prices[i] = price_dict[companies[i]][0]
print(len(companies))  
 
N =100
test_portfolios = np.zeros(shape=(N,time_steps))

def portfolio_evolution(portfolio):
    portfolio_Value_Evolution = np.zeros(time_steps)
    portfolio_Value_Evolution[0] = portfolio.value
    for j in range(1,time_steps):
        portfolio_Value_Evolution[j] = 0
        for i in range(len(price_dict)):
            portfolio_Value_Evolution[j] +=  portfolio.holdings[i] * price_dict[companies[i]][j]
    return portfolio_Value_Evolution

for i in range(N):
    test_portfolios[i] = portfolio_evolution(Portfolio(10000, np.ones(len(initial_prices)), initial_prices, Random= True))

plt.style.use('dark_background')
#for i in range(10):
    #plt.plot(test_portfolios[i])
plt.plot(np.mean(test_portfolios, axis=0), color = 'red')
plt.fill_between(x=np.arange(time_steps), y1= np.mean(test_portfolios, axis=0)-np.std(test_portfolios, axis= 0), y2= np.mean(test_portfolios, axis=0)+np.std(test_portfolios, axis= 0))
plt.grid()
plt.show()
