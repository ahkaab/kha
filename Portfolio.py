import numpy as np

class Portfolio():
    """A portfolio of stock share quantities and a separate cash-bond balance."""

    def __init__(self,price_dict, Initial_Bond_Holdings, Initial_Holdings , Stock_Prices,Company_Names, trading_step_interest_rate = 0, Random = False, Initial_Value = 10000):
        self.stagnant_days = 0 
        self.value = Initial_Holdings @ Stock_Prices + Initial_Bond_Holdings
        self.trading_step_interest_rate = trading_step_interest_rate
        self.price_dict = price_dict
        self.company_names = list(Company_Names)
        if not Random: 
            holdings = Initial_Holdings
            self.bonds = Initial_Bond_Holdings
            self.portfolio = dict()
            for i in range(len(Company_Names)):
                self.portfolio[Company_Names[i]] = holdings[i]
        else: 
            self.bonds = 0
            holdings = np.ones(len(Stock_Prices))
            xi = np.random.randint(1,100,size=(len(holdings)))
            A = np.dot(xi,Stock_Prices)
            holdings = xi * Initial_Value/(A)
            self.value = np.dot(holdings, Stock_Prices) + Initial_Bond_Holdings
            self.portfolio = dict()
            for i in range(len(Company_Names)):
                self.portfolio[Company_Names[i]] = holdings[i]
        if np.abs(self.value - Initial_Value - Initial_Bond_Holdings) > 0.5:
                raise Exception(f'Random portfolio Value has change of {np.abs(self.value - Initial_Value)}')
    @property
    def holdings(self):
        # Return shares in the same order as company_names and the price matrix.
        return np.array([
            self.portfolio[company]
            for company in self.company_names
        ])
    
    def update_Portfolio(self,time_step, to_sell, to_buy):
        stock_prices = np.array([
                    self.price_dict[company][time_step]
                    for company in self.company_names
                ])
        #Bond intrest 
        self.bonds = self.bonds * (1+self.trading_step_interest_rate)
    
        # This is the portfolio's value immediately before any sale or purchase.
        start_value = self.holdings @ stock_prices + self.bonds

        if len(to_buy) == 0 and len(to_sell) == 0:
            self.stagnant_days += 1
        
        #remove duplicates
        to_buy = list(dict.fromkeys(to_buy))
        to_sell = list(dict.fromkeys(to_sell))
        # Use prices from one time step so a rebalance can preserve value.

        for company in to_sell:
            self.bonds += (self.portfolio[company] * self.price_dict[company][time_step])
            self.portfolio[company] = 0
        if len(to_buy)>0:
            available_funds = self.bonds
            even_funds = available_funds/len(to_buy)
        for company in to_buy:                
            self.portfolio[company] += even_funds/self.price_dict[company][time_step]
            self.bonds -= even_funds

        # Recalculate after trading; at unchanged prices this should equal start_value.
        self.value = self.holdings @ stock_prices + self.bonds
        if not np.isclose(start_value , self.value):
            raise ValueError(f'Portfolio Value changed by {self.value - start_value} unexpectedly!')

    def naive_stock_valuation(self, time_step, check_interval = 7):
        #Method to calculate the last weeks mean and Std and assess wether or not to buy off of that
        to_buy = set()
        to_sell = set()
        if time_step >= check_interval:
            for company in self.company_names:
                current_price = self.price_dict[company][time_step]
                week_mean = np.mean(self.price_dict[company][time_step-check_interval:time_step])
                week_std = np.std(self.price_dict[company][time_step-check_interval:time_step])
                # likely in a dip and will regain
                if  week_mean - week_std <current_price < week_mean:
                    to_buy.add(company)
                # likely to be peak
                elif week_mean + week_std <current_price:
                    to_sell.add(company)
        return to_buy,to_sell

#TO DO:
# Add weights to selling buy so not buy all and sell all
   
