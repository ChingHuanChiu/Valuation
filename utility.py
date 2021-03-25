import pandas as pd


def transform_to_num(raw_value):
    value = raw_value
    if '%' in raw_value:
        value = raw_value.replace('%', '')
        value = float(value) * 0.01
    elif 'B' in raw_value:
        value = raw_value.replace('B', '')
        value = float(value) * 1000
    elif 'M' in raw_value:
        value = float(raw_value)

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


def filter_extreme_case(data: pd.Series, mul=3):
    """
    如果最大值超過其餘數值平均的3倍則刪除
    """
    if data.max() >= pd.Series(sorted(data)[:-1]).mean() * mul:
        data = data.drop(data.argmax())
    return data


def row_of_net_income(soup):

    all_data: list = soup.find_all('div', {'data-test': 'fin-row'})

    for i in range(len(all_data)):

        if all_data[i].text.startswith('Net Income from Continuing Operation Net Minority Interest'):
            row = i + 1
            break
    return row
