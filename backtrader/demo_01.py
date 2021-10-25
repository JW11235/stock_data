"""
backtrader 案例

@ author: Jeffrey.Wang
@ date: 2021.10.4
"""

import os
import datetime
import pandas as pd
import numpy as np
import backtrader as bt
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']


class Platform(bt.Indicator):
    lines = ('uplimit', 'downlimit')

    def __init__(self):
        self.addminperiod(6)

    def next(self):
        self.uplimit[0] = max(self.data.high.get(ago=-1, size=5))
        self.downlimit[0] = min(self.data.low.get(ago=-1, size=5))


class MyStrategy(bt.Strategy):
    params = (
        ('maperiod_3', 3),
        ('maperiod_5', 5)
    )

    def log(self):
        pass

    def __init__(self):
        print(f'init___{self.datas[0].datetime.date(0)}')
        self.limits = Platform(self.data)
        self.buysignals = bt.indicators.CrossOver(self.datas[0].close, self.limits.uplimit)
        self.sellsignals = bt.indicators.CrossDown(self.data.close, self.limits.downlimit)
        # self.order = None
        self.buysignals.plotinfo.plot = False
        self.sellsignals.plotinfo.plot = False
        self.limits.plotinfo.plotmaster = self.data  # 类似通达信的 是否在主图显示
        # self.卖出信号.plotinfo.plot = False

    def start(self):
        print(f"start!___{self.datas[0].datetime.date(0)}")

    def prenext(self):
        print(f"prenext___{self.datas[0].datetime.date(0)}")

    def nextstart(self):
        print(f'nextstart___{self.datas[0].datetime.date(0)}')

    # def notify_order(self):
    #     pass
    #
    # def notify_trade(self):
    #     pass

    def next(self):
        # if self.order:
        #     return
        if not self.position:
            if self.buysignals[0] == 1:
                self.order = self.buy(size=1000)
                print(f"{self.datas[0].datetime.date(0)},买入！价格为{self.data.close[0]}")
        else:
            if self.sellsignals[0] == 1:
                self.order = self.sell(size=1000)
                print(f"{self.datas[0].datetime.date(0)},卖出！价格为{self.data.close[0]}")
        pass

    def stop(self):
        print(f"stop___{self.datas[0].datetime.date(0)}")
        if self.position:
            self.order = self.sell(size=1000)
            print(f"{self.datas[0].datetime.date(0)},卖出！价格为{self.data.close[0]}")


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.00)    # 设置初始资金金额
    init_cash = cerebro.broker.getvalue()
    print('初始资金:{}'.format(init_cash))

    #####################
    path = os.path.join('..\\db', '600000sh.csv')
    data = pd.read_csv(path, index_col='date', parse_dates=True)
    prices = bt.feeds.PandasData(dataname=data,
                                 fromdate=datetime.datetime(2020, 1, 1),
                                 todate=datetime.datetime(2020, 10, 18)
                                 )

    cerebro.adddata(prices)
    cerebro.addstrategy(MyStrategy)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.02, annualize=True, _name='SP')
    cerebro.addanalyzer(bt.analyzers.DrawDown,  _name='DD')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='TA')
    #####################

    results = cerebro.run()
    strat = results[0]
    anzs = strat.analyzers
    spratio = anzs.SP.get_analysis()['sharperatio']
    dd = anzs.DD.get_analysis()

    end_cash = cerebro.broker.getvalue()
    print('期末资金: {}'.format(end_cash))
    print('夏普率： {}'.format(spratio))
    print('最大回撤： {}'.format(dd['drawdown']))
    cerebro.plot()

    # for alyzer in strat.analyzers:
    #     alyzer.print()