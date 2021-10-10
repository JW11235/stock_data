"""
baostock 数据提取工具

@author: Jeffrey.Wang
@date: 2021.10.1
"""

import numpy
import pandas as pd
import baostock as bs
import datetime as dt


lg = bs.login()
print('login respond error_msg:' + lg.error_msg)


def get_stk_market_daily(stock_code, begin_date, end_date):
    """
    备注：存储前添加后复权因子。
    """
    bs_code = stock_code[-2:] + '.' + stock_code[0:6]
    bs_begin = begin_date.strftime(format='%Y-%m-%d')
    bs_end = end_date.strftime(format='%Y-%m-%d')
    fields = ['date', 'code', 'open', 'high', 'low', 'close', 'preclose',
              'volume', 'amount', 'adjustflag', 'turn', 'tradestatus',
              'pctChg', 'peTTM', 'pbMRQ', 'psTTM', 'pcfNcfTTM', 'isST']

    rs = bs.query_history_k_data_plus(bs_code,
                                      ','.join(fields),
                                      start_date=bs_begin,
                                      end_date=bs_end,
                                      frequency='d',
                                      adjustflag='3')

    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())

    result = pd.DataFrame(data_list, columns=rs.fields)
    result.iloc[:, 2:-1] = result.iloc[:, 2:-1].applymap(lambda x: float(x))
    result['code'] = result['code'].apply(lambda x: x[3:] + '.' + x[0:2])

    # 修改fields名称
    result.rename(columns={'pctChg': 'pct_chg',
                           'peTTM': 'pe_ttm',
                           'pbMRQ': 'pb_mrq',
                           'psTTM': 'ps_ttm',
                           'pcfNcfTTM': 'pcf_ttm',
                           'isST': 'is_st'}, inplace=True)

    return result


def get_index_market_daily(index_code, begin_date, end_date):
    bs_code = index_code[-2:] + '.' + index_code[0:6]
    bs_begin = begin_date.strftime(format='%Y-%m-%d')
    bs_end = end_date.strftime(format='%Y-%m-%d')
    fields = ['date', 'code', 'open', 'high', 'low', 'close', 'preclose',
              'volume', 'amount', 'pctChg']

    rs = bs.query_history_k_data_plus(bs_code,
                                      ','.join(fields),
                                      start_date=bs_begin,
                                      end_date=bs_end,
                                      frequency='d')

    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())

    result = pd.DataFrame(data_list, columns=rs.fields)
    result.iloc[:, 2:-1] = result.iloc[:, 2:-1].applymap(lambda x: float(x))
    result['code'] = result['code'].apply(lambda x: x[3:] + '.' + x[0:2])

    # 修改fields名称
    result.rename(columns={'pctChg': 'pct_chg'}, inplace=True)

    return result


def get_adj_factor(stock_code, begin_date, end_date):
    """
    获取复权因子，涨跌幅复权算法。
    """
    bs_code = stock_code[-2:] + '.' + stock_code[0:6]
    bs_begin = begin_date.strftime(format='%Y-%m-%d')
    bs_end = end_date.strftime(format='%Y-%m-%d')

    # 查询复权因子
    rs_list = []
    rs_factor = bs.query_adjust_factor(code=bs_code,
                                       start_date=bs_begin,
                                       end_date=bs_end)

    while (rs_factor.error_code == '0') & rs_factor.next():
        rs_list.append(rs_factor.get_row_data())

    result = pd.DataFrame(rs_list, columns=rs_factor.fields)
    result.iloc[:, 2:-1] = result.iloc[:, 2:-1].applymap(lambda x: float(x))
    result['code'] = result['code'].apply(lambda x: x[3:] + '.' + x[0:2])

    return result


def get_stk_industry(stock_code=None, begin_date=None):

    if isinstance(stock_code, str):
        bs_code = stock_code[-2:] + '.' + stock_code[0:6]
    else:
        bs_code = stock_code

    if isinstance(begin_date, dt.datetime):
        bs_date = begin_date.strftime(format='%Y-%m-%d')
    else:
        bs_date = begin_date

    rs = bs.query_stock_industry(bs_code, bs_date)

    industry_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        industry_list.append(rs.get_row_data())

    result = pd.DataFrame(industry_list, columns=rs.fields)
    result['code'] = result['code'].apply(lambda x: x[3:] + '.' + x[0:2])

    return result


if __name__ == '__main__':
    import os
    scode = '600000.sh'
    bdate = dt.datetime(2019, 1, 1)
    edate = dt.datetime(2021, 9, 1)
    # df = get_stk_market_daily(scode, bdate, edate)
    # df = get_index_market_daily('000001.sh', bdate, edate)
    # df = get_adj_factor(scode, bdate, edate)
    # df = get_stk_industry(scode, bdate)
    df = get_stk_market_daily(scode, bdate, edate)
    df['openinterest'] = 0.0
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
    df = df.loc[:, ['open', 'high', 'low', 'close', 'volume', 'openinterest']]
    print(df.head())
    df.to_csv(os.path.join('..\\db', scode[0:6]+scode[-2:]+'.csv'), encoding='gbk', index=True)
