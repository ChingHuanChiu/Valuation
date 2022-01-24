from calendar import c
from typing import Union, Dict
import asyncio
import warnings
warnings.simplefilter("ignore")

import pandas as pd
import numpy as np



from datagetter import Data
from utility import filter_extreme_case


class Dcf:

    def __init__(self, current_year: float, next_year: float, sales_growth_ave: float, fcf_income: pd.DataFrame):
 
        self.fcf_income = fcf_income
        self.current_year = current_year
        self.next_year = next_year 
        self.sales_growth_ave = sales_growth_ave

    def _calculate_margin(self):
        """
        算出過去平均 'Fcf / Ni' 與 'Ni/Rev'
        """

        profit_margin = self.fcf_income['NI'] / self.fcf_income['Sales/Revenue']
        profit_margin = filter_extreme_case(profit_margin)
        profit_margin_mean = profit_margin.mean()

        FCF_margin = self.fcf_income['FCF'] / self.fcf_income['NI']
        FCF_margin = filter_extreme_case(FCF_margin)
        FCF_margin_mean = FCF_margin.mean()
        return FCF_margin_mean, profit_margin_mean

    def _calculate_predict_revenue_growth_ratio(self):
        """
        如果分析師沒預測，則用過去平均的營收成長率當作預測營收成長率
        """

        mean_revenue_growth = self.fcf_income['Sales/Revenue'].pct_change().dropna().mean()

        return round(mean_revenue_growth, 2)

    def predict_data(self):
        """
         算出預期營收、預期NI、預期FCF
        """
        ave_FCF_margin, ave_profit_margin = self._calculate_margin()
        # current_year, next_year, sales_growth_ave = self.Data.get_predict_revenue_growth_eps()[0:3]
        hint = None
        if self.sales_growth_ave == 'N/A':
            self.sales_growth_ave = self._calculate_predict_revenue_growth_ratio()
            hint = '沒有分析師預測，所以用過去平均營收成長率進行評價'

        # 4年的預期營收, 2年分析師預測加上2年推算
        predict_rev_data = [self.current_year, self.next_year]
        predict_rev = self.next_year
        for _ in range(2):
            predict_rev = predict_rev * (1 + self.sales_growth_ave)
            predict_rev_data.append(predict_rev)

        # 4年的預期NI
        pre_NI_data = [x * ave_profit_margin for x in predict_rev_data]

        # 4年的預期FCF
        pre_fcf_data = [x * ave_FCF_margin for x in pre_NI_data]
        return predict_rev_data, pre_NI_data, pre_fcf_data, hint


    def valuation(self, perpetual_growth, wacc: np.array, out: float, close: float) -> Union[str, float]:
        fcf = self.predict_data()[2]
        #終值
        terminal_fcf = fcf[-1] * (1 + perpetual_growth) / ((wacc[0] - 1) - perpetual_growth)
        fcf = np.array(fcf)
        if all(x > 0 for x in fcf):
            fcf = fcf
        else:
            return f'the DCF is not suitable for {self.s} '

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
    def __init__(self, growth_estimate: float, wacc: float):
        self.wacc = wacc
        self.growth_estimate = growth_estimate

    def calculate_pe(self):

        discount_factor = self.wacc - 1
        discount_duration = 20

        def pe(g, n, k):
            factor1 = (1 + g) ** n
            factor2 = (1 + k) ** n

            return factor1 / factor2

        PE = sum(pe(g=self.growth_estimate, k=discount_factor, n=i) for i in range(discount_duration))

        return PE

    def valuation(self, eps_current_year_estimate: float):
        PE = self.calculate_pe()
        EPS = eps_current_year_estimate

        price = PE * EPS
        return price


class Valuation:
    def __init__(self, ticker, wacc_adj: float = 0.01):
        self.data = Data(ticker)
        res_data: Dict[str, Union[str, float, np.array, pd.DataFrame]] = asyncio.run(self.data.get(wacc_adj))

        self.fcf_income: float = res_data['fcf_ni_rev']
        self.current_year: float = res_data['current_year']
        self.next_year: float = res_data['next_year'] 
        self.sales_growth_ave: float = res_data['sales_growth_ave']
        self.growth_estimate: float = res_data['growth_estimate']
        self.eps_current_year_estimate: float = res_data['eps_current_year_estimate']
        self.wacc: np.array= res_data['wacc']
        self.outstadings: float = res_data['out']
        self.close: float = res_data['close']
       

    def value(self) -> Dict[str, str]:

        dcf_value = Dcf(current_year=self.current_year, 
                        next_year=self.next_year, 
                        sales_growth_ave=self.sales_growth_ave,
                        fcf_income=self.fcf_income,).valuation(perpetual_growth=0.02, wacc=self.wacc, out=self.outstadings, 
                                                               close=self.close)
        print(self.wacc[0])
        growth_value = GrowthValuation(growth_estimate=self.growth_estimate, 
                                       wacc=self.wacc[0]).valuation(self.eps_current_year_estimate)
        
        if isinstance(dcf_value, float) and dcf_value > 0 : dcf_value = round(dcf_value, 2)
        return {'DCF法:': f'{dcf_value}元', '成長型股票評價:': f'{round(growth_value, 2)}元'}


if __name__ == '__main__':

    res = Valuation('T', 0.01).value()

