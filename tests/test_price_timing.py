import tempfile
import unittest
from pathlib import Path

import numpy as np

from Data_reader import read_open_close_prices
from Portfolio import Portfolio


class PriceTimingTests(unittest.TestCase):
    def test_reader_applies_one_date_mask_to_both_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'prices.csv'
            path.write_text(
                'company,date,open,close\n'
                'B,2024-01-03,30,31\n'
                'A,2024-01-01,10,11\n'
                'B,2024-01-01,20,21\n'
                'A,2024-01-02,12,13\n'
                'A,2024-01-03,14,15\n'
            )
            opens, closes, dates = read_open_close_prices(str(path))
        self.assertEqual(list(dates.astype('datetime64[D]').astype(str)),
                         ['2024-01-01', '2024-01-03'])
        np.testing.assert_array_equal(opens['B'], [20, 30])
        np.testing.assert_array_equal(closes['B'], [21, 31])
        np.testing.assert_array_equal(opens['A'], [10, 14])
        np.testing.assert_array_equal(closes['A'], [11, 15])

    def test_signal_uses_only_past_closes_and_execution_uses_open(self):
        opens = {'A': np.full(6, 100.)}
        closes = {'A': np.array([8., 10., 12., 9., 999., 999.])}
        portfolio = Portfolio(
            open_price_dict=opens, close_price_dict=closes,
            Initial_Bond_Holdings=100., Initial_Holdings=np.array([0.]),
            Stock_Prices=np.array([100.]), Company_Names=['A'], Initial_Value=0,
        )
        buys, sells = portfolio.naive_stock_valuation(4, check_interval=3)
        self.assertEqual(buys, {'A'})
        self.assertEqual(sells, set())
        closes['A'][4:] = -999.
        self.assertEqual(portfolio.naive_stock_valuation(4, 3), (buys, sells))
        portfolio.update_Portfolio(4, to_buy=buys, to_sell=sells)
        self.assertAlmostEqual(portfolio.holdings[0], 1.)
        self.assertAlmostEqual(portfolio.bonds, 0.)
        self.assertAlmostEqual(portfolio.value, 100.)
        self.assertEqual(portfolio.naive_stock_valuation(3, 3), (set(), set()))


if __name__ == '__main__':
    unittest.main()
