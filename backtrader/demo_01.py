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


class MyStrategy(bt.Strategy):
    params = (
        ('ma_short', 5),
        ('ma_long', 20),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):

        self.dataclose = self.datas[0].close
        self.zf = self.datas[0].high - self.datas[0].low

        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0].close, period=self.params.ma_short)
        self.lma = bt.indicators.SimpleMovingAverage(
            self.datas[0].close, period=self.params.ma_long)


    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if not self.position:
            if self.lma[0] > self.sma[0]: #  and self.zf[0] > self.dataclose[0] * 0.02
                self.log('Buy Create, %.2f' % self.dataclose[0])
                self.buy(size=10000)
        else:
            if self.lma[0] < self.sma[0]:
                self.log('Sell Create: %.2f' % self.dataclose[0])
                self.sell(size=10000)


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
    cerebro.plot(style="candle")

    # for alyzer in strat.analyzers:
    #     alyzer.print()