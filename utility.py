import pandas as pd
import numpy as np


def transform_to_num(raw_value) -> float:
    value = raw_value
    if '%' in raw_value:
        value = raw_value.replace('%', '')
        value = float(value) * 0.01
    elif 'B' in raw_value:
        value = raw_value.replace('B', '')
        value = float(value) * 1000
    elif 'M' in raw_value:
        value = raw_value.replace('M', '')
        value = float(value) * 100

    elif '(' in raw_value:
        value = raw_value.replace('(', '')
        value = value.replace(')', '').replace(',', '')
        value = float(value) * -1
    elif 'nan' == str(raw_value):
        value = 'nan'
    elif ',' in raw_value:
        value = raw_value.replace(',', '')
        value = float(value)

    return value


def filter_extreme_case(data: pd.Series, std_mul=1):
    """
    remove the data if data greater than  'mean + std_mul * std' or  smaller than 'mean  std_mul * std'
    """

    MEAN = data.mean()
    STD = data.std()
    pos_threshold, neg_threshold = MEAN + std_mul * STD, MEAN - std_mul * STD
    position = np.where((pos_threshold * std_mul <= data.values) | (data.values >= neg_threshold * std_mul))[0]
    res = data[position]

    return res


def row_of_report(soup, field):
    all_data: list = soup.find_all('div', {'data-test': 'fin-row'})

    for i in range(len(all_data)):

        if all_data[i].text.startswith(field):
            row = i + 1
            break
    return row

def amount_of_column(soup):
    resp = soup.find_all('div', {'class': 'D(tbhg)'})[0].find_all('div', {'class': 'Ta(c)'})
    return len(resp) - 1