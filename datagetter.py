from bs4 import BeautifulSoup
from utility import transform_to_num, amount_of_column, row_of_report
import pandas as pd
import numpy as np
import requests
import re
import random
import yahoo_fin.stock_info as si



headers = [{'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/65.0.3325.181 Safari/537.36'},
           {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/39.0.2171.95 Safari/537.36'}]


class Crawler:
    def __init__(self, symbol):
        self.symbol = symbol

    def wacc(self, wacc_adj):
        """
        crawl the wacc, besides you can adjust the wacc by wacc_adjust
        """
        url = f'https://www.gurufocus.com/term/wacc/{self.symbol}/WACC'
        resp = requests.get(url, headers=random.choice(headers))
        resp.encoding = 'utf-8'
        raw_html = resp.text
        soup = BeautifulSoup(raw_html, 'html.parser')
        wacc = soup.find('font', {'style': 'font-size: 24px; font-weight: 700; color: #337ab7'}).text[1:5]
        if '%' in wacc:
            wacc = re.findall(r"\d+\.?\d*", wacc)
            wacc = (float(wacc[0]) * 0.01) + wacc_adj
        else:
            wacc = (float(wacc) * 0.01) + wacc_adj

        # 算出不同年數的wacc
        wacc_list = [wacc + 1]
        wacc_new = (1 + wacc)
        for _ in range(3):
            wacc_new = wacc_new * (1 + wacc)
            wacc_list.append(wacc_new)
        return np.array(wacc_list)

    def predict_revenue_growth_eps(self):
        """
        從Yahoo抓分析師預期營收以及預期營收成長的資料，並將單位Billion轉成Million， 將 % 轉成數值
        """
        url = f'https://finance.yahoo.com/quote/{self.symbol}/analysis'
        soup = self._suop(url=url)

        current_year = soup.select(
            '#Col1-0-AnalystLeafPage-Proxy > section > table:nth-of-type(2) > tbody > tr:nth-of-type(3) > td:nth-of-type(4) > span')[
            0].text
        next_year = soup.select(
            '#Col1-0-AnalystLeafPage-Proxy > section > table:nth-of-type(2) > tbody > tr:nth-of-type(3) > td:nth-of-type(5) > span')[
            0].text
        current_sales_growth = soup.select(
            '#Col1-0-AnalystLeafPage-Proxy > section > table:nth-of-type(2) > tbody > tr:nth-of-type(6) > td:nth-of-type(4) > span')[
            0].text
        next_sales_growth = soup.select(
            '#Col1-0-AnalystLeafPage-Proxy > section > table:nth-of-type(2) > tbody > tr:nth-of-type(6) > td:nth-of-type(5) > span')[
            0].text

        growth_estimate = soup.select(
            '#Col1-0-AnalystLeafPage-Proxy > section > table:nth-of-type(6) > tbody > tr:nth-of-type(5) > td:nth-of-type(2)')[0].text
        eps_current_year_estimate = soup.select('#Col1-0-AnalystLeafPage-Proxy > section > table:nth-of-type(4) > '
                                                'tbody > tr:nth-of-type(1) > td:nth-of-type(4) > span'

        )[0].text

        growth_estimate = transform_to_num(growth_estimate)

        current_year = transform_to_num(current_year)
        next_year = transform_to_num(next_year)
        sales_growth_current = transform_to_num(current_sales_growth)
        sales_growth_next = transform_to_num(next_sales_growth)
        sales_growth_ave = (sales_growth_current + sales_growth_next) * 0.5
        return current_year, next_year, sales_growth_ave, growth_estimate, eps_current_year_estimate

    def fcf_ni_rev(self):
        """
        Crawl the data from yahoo
        """
        income_url = f'https://finance.yahoo.com/quote/{self.symbol}/financials'
        cash_url = f'https://finance.yahoo.com/quote/{self.symbol}/cash-flow'

        income_soup = self._suop(url=income_url)
        cash_flow_soup = self._suop(url=cash_url)
        columns = amount_of_column(income_soup)
        revenue = [transform_to_num(self._income_selector(soup=income_soup, column=c, row=1)) * 0.001 for c in range(3, 3 + columns)]
        ni_row = row_of_report(income_soup, 'Net Income from Continuing Operation Net Minority Interest')
        fcf_row = row_of_report(cash_flow_soup, 'Free Cash Flow')
        ni = [transform_to_num(self._income_selector(soup=income_soup, column=c, row=ni_row)) * 0.001 for c in range(3, 3 + columns)]
        fcf = [transform_to_num(self._cashflow_selector(soup=cash_flow_soup, column=c, row=fcf_row)) * 0.001 for c in range(3, 3 + columns)]
        data = {'NI': ni, 'Sales/Revenue': revenue, 'FCF': fcf}
        return pd.DataFrame(data)

    def outstanding_close_name(self):
        """
        get the price and outstandings from yahoo API the unit of outstanding is 'M'
        """

        out = si.get_quote_data(self.symbol)['sharesOutstanding']
        out = out / 1000000
        close = si.get_quote_table(self.symbol)['Previous Close']
        name = self.symbol

        return round(out), close, name

    def _suop(self, url):
        resp = requests.get(url, headers=random.choice(headers))
        resp.encoding = 'utf-8'
        raw_html = resp.text
        soup = BeautifulSoup(raw_html, 'html.parser')
        return soup

    def _income_selector(self, soup, column, row):
        value = soup.select(f'#Col1-1-Financials-Proxy > section > div.Pos\(r\) >\
         div.W\(100\%\).Whs\(nw\).Ovx\(a\).BdT.Bdtc\(\$seperatorColor\) > div > div.D\(tbrg\) >\
          div:nth-of-type({row}) > div.D\(tbr\).fi-row.Bgc\(\$hoverBgColor\)\:h > div:nth-of-type({column}) > span')
        return value[0].text

    def _cashflow_selector(self, soup, column, row):
        value = soup.select(f'#Col1-1-Financials-Proxy > section > div.Pos\(r\) >\
               div.W\(100\%\).Whs\(nw\).Ovx\(a\).BdT.Bdtc\(\$seperatorColor\) > div > div.D\(tbrg\) >\
               div:nth-of-type({row}) > div.D\(tbr\).fi-row.Bgc\(\$hoverBgColor\)\:h > div:nth-of-type({column}) > span')

        return value[0].text


class Data(Crawler):
    def __init__(self, symbol):
        super().__init__(symbol)

    def get_wacc(self, wacc_adj):
        return self.wacc(wacc_adj=wacc_adj)

    def get_predict_revenue_growth_eps(self):
        return self.predict_revenue_growth_eps()

    def get_out_close_name(self):
        return self.outstanding_close_name()

    def get_fcf_income(self) -> pd.DataFrame:

        return self.fcf_ni_rev()
