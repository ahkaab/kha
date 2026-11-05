import numpy as np

class Portfolio():
    def __init__(self,price_dict, Initial_Value, Bond_Holdings, Initial_Holdings, Stock_Prices,Company_Names, daily_intrest_Rate = 0, Random = False,):
        self.value = Initial_Value + Bond_Holdings
        self.price_dict = price_dict
        self.company_names = list(Company_Names)
        if not Random: 
            holdings = Initial_Holdings
            self.bonds = Bond_Holdings
            self.portfolio = dict()
            for i in range(len(Company_Names)):
                self.portfolio[Company_Names[i]] = holdings[i]
        else: 
            self.bonds = 0
            holdings = np.ones(len(Stock_Prices))
            xi = np.random.randint(0,100,size=(len(holdings)))
            A = np.dot(xi,Stock_Prices)
            holdings = xi * Initial_Value/(A)
            self.value = np.dot(holdings, Stock_Prices) + Bond_Holdings
            self.portfolio = dict()
            for i in range(len(Company_Names)):
                self.portfolio[Company_Names[i]] = holdings[i]
        if np.abs(self.value - Initial_Value - Bond_Holdings) > 0.5:
                raise Exception(f'Random portfolio Value has change of {np.abs(self.value - Initial_Value)}')
    @property
    def holdings(self):
        return np.array([
            self.portfolio[company]
            for company in self.company_names
        ])
    
    def update_Portfolio(self,time_step, to_Sell, to_Buy):
        stock_prices = np.array([
            self.price_dict[company][time_step]
            for company in self.company_names
        ])

        start_value = self.holdings @ stock_prices + self.bonds

        for company in to_Sell:
            self.bonds += self.portfolio[company] * self.price_dict[company][time_step]
            self.portfolio[company] = 0
        if len(to_Buy) >0:
            available_funds = self.bonds
            even_funds = available_funds/len(to_Buy)
        for company in to_Buy:                
            self.portfolio[company] += even_funds/self.price_dict[company][time_step]
            self.bonds -= even_funds

        self.value = self.holdings @ stock_prices + self.bonds
        if not np.isclose(start_value , self.value):
            raise ValueError(f'Portfolio Value changed by {self.value - start_value} unexpectedly!')
#TO DO:
# Portfolio dynamic changing 

   