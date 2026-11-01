import matplotlib.pyplot as plt
from Data_reader import read_prices, plot_prices

prices = read_prices("test_data.csv")
plot_prices(prices)
plt.show()