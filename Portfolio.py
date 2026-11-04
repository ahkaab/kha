import numpy as np

class Portfolio():
    def __init__(self, Initial_Value, Initial_Holdings, Stock_Prices, Random = False,):
        self.value = Initial_Value
        if not Random: 
            self.holdings = Initial_Holdings
        else: 
            self.holdings = np.ones(len(Stock_Prices))
            xi = np.random.randint(0,100,size=(len(self.holdings)))
            A = np.dot(xi,Stock_Prices)
            self.holdings = xi * Initial_Value/(A)
            self.value = np.dot(self.holdings, Stock_Prices)

            if np.abs(self.value - Initial_Value) > 0.5:
                raise Exception(f'Random portfolio Value has change of {np.abs(self.value - Initial_Value)}')

#TO DO:
# adding bonds as an axis to shift money  
# Portfolio dynamic changing 

   