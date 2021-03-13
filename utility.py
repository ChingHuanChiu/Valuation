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


