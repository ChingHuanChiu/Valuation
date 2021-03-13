import pandas as pd
import numpy as np
from datagetter import Data
from utility import filter_extreme_case


class Dcf:

    def __init__(self, symbol):
        super(Dcf, self).__init__()
        self.s = symbol
        self.Data = Data(symbol)

    def _calculate_margin(self) -> (pd.Series, pd.Series):
        """
        算出過去平均 'Fcf / Ni' 與 'Ni/Rev'
        """
        fcf_income = self.Data.get_fcf_income()

        profit_margin = fcf_income['NI'] / fcf_income['Sales/Revenue']
        profit_margin = filter_extreme_case(profit_margin)
        profit_margin_mean = profit_margin.mean()

        FCF_margin = fcf_income['FCF'] / fcf_income['NI']
        FCF_margin = filter_extreme_case(FCF_margin)
        FCF_margin_mean = FCF_margin.mean()
        return FCF_margin_mean, profit_margin_mean

    def _calculate_predict_revenue_growth_ratio(self):
        """
        如果分析師沒預測，則用過去平均的營收成長率當作預測營收成長率
        """
        fcf_income = self.Data.get_fcf_income()

        mean_revenue_growth = fcf_income['Sales/Revenue'].pct_change().dropna().mean()

        return round(mean_revenue_growth, 2)

    def predict_data(self):
        """
         算出預期營收、預期NI、預期FCF
        """
        ave_FCF_margin, ave_profit_margin = self._calculate_margin()
        current_year, next_year, sales_growth_ave = self.Data.get_predict_revenue_growth_eps()[0:3]
        hint = None
        if sales_growth_ave == 'N/A':
            sales_growth_ave = self._calculate_predict_revenue_growth_ratio()
            hint = '沒有分析師預測，所以用過去平均營收成長率進行評價'

        # 4年的預期營收, 2年分析師預測加上2年推算
        predict_rev_data = [current_year, next_year]
        predict_rev = next_year
        for _ in range(2):
            predict_rev = predict_rev * (1 + sales_growth_ave)
            predict_rev_data.append(predict_rev)

        # 4年的預期NI
        pre_NI_data = [x * ave_profit_margin for x in predict_rev_data]

        # 4年的預期FCF
        pre_fcf_data = [x * ave_FCF_margin for x in pre_NI_data]
        return predict_rev_data, pre_NI_data, pre_fcf_data, hint

    def valuation(self, perpetual_growth, wacc_adj):
        out, close, name = self.Data.get_out_close_name()
        wacc = self.Data.get_wacc(wacc_adj=wacc_adj)
        fcf = self.predict_data()[2]

        #終值
        terminal_fcf = fcf[-1] * (1 + perpetual_growth) / ((wacc[-1] - 1) - perpetual_growth)
        fcf = np.array(fcf)
        if all(x > 0 for x in fcf):
            fcf = fcf
        else:
            return 'There is a negative value in fcf'

        pv = (fcf / wacc).sum() + (terminal_fcf / wacc[-1])
        if out == 'N/A':
            return 'the data of outstanding is NaN'
        else:
            fair_value = pv / out

            return round(fair_value, 2)

    def hint(self):
        if self.predict_data()[3] is not None:
            hint = self.predict_data()[3]
            return hint
        else:
            return None


class GrowthValuation:
    def __init__(self, ticker):
        self.ticker = ticker
        self.Data = Data(ticker)
        self.growth_estimate, self.eps_current_year_estimate = self.Data.get_predict_revenue_growth_eps()[3:5]

    def calculate_pe(self):

        discount_factor = float(self.Data.get_wacc(wacc_adj=0)[0]) - 1
        discount_duration = 20

        def pe(g, n, k):
            factor1 = (1 + g) ** n
            factor2 = (1 + k) ** n

            return factor1 / factor2

        PE = sum(pe(g=self.growth_estimate, k=discount_factor, n=i) for i in range(discount_duration))

        return PE

    def valuation(self):
        PE = self.calculate_pe()
        EPS = float(self.eps_current_year_estimate)
        price = PE * EPS
        return price



if __name__ == '__main__':
    # D = Dcf('MMM')
    # pr = D.present_value_of_cf(perpetual_growth=0.03, wacc_adj=-0.03)
    G = GrowthValuation('AAPL')
    value = G.valuation()

