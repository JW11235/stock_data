import backtrader as bt


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


###############################################
