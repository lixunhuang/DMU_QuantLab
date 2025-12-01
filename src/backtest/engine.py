import pandas as pd
from datetime import datetime
import sys
from ..config import INITIAL_CAPITAL, COMMISSION_RATE, MIN_COMMISSION, TAX_RATE


class BacktestEngine:
    def __init__(self, data_manager, strategy, start_date, end_date):
        self.dm = data_manager
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date

        # 账户状态
        self.cash = INITIAL_CAPITAL
        self.holdings = {}  # {code: shares}
        self.history_assets = []
        self.dates = []
        self.last_prices = {}  # 价格缓存，防止停牌导致资产归零

    def calculate_cost(self, amount, is_sell=False):
        comm = max(MIN_COMMISSION, amount * COMMISSION_RATE)
        tax = amount * TAX_RATE if is_sell else 0
        return comm + tax

    def run(self):
        print(f"\n>>> 启动回测引擎: {self.strategy.__class__.__name__}")
        trade_dates = self.dm.get_trade_dates(self.start_date, self.end_date)
        if not trade_dates:
            print("错误：回测区间无数据，请检查日期或数据库。")
            return pd.Series()

        last_rebalance_idx = -999

        for i, date in enumerate(trade_dates):
            # 进度条
            sys.stdout.write(f"\r处理进度: {i + 1}/{len(trade_dates)} ({date})")
            sys.stdout.flush()

            # --- 策略调仓 (每20个交易日) ---
            if i == 0 or (i - last_rebalance_idx) >= 20:
                target_codes = self.strategy.select_stocks(date)
                if target_codes:
                    last_rebalance_idx = i
                    self._rebalance(date, target_codes)

            # --- 每日结算 ---
            self._settle(date)

        print("\n>>> 回测完成")

        # 返回资产曲线
        return pd.Series(self.history_assets, index=pd.to_datetime(self.dates))

    def _rebalance(self, date, target_codes):
        # 1. 卖出
        for code in list(self.holdings.keys()):
            price = self.dm.get_price(code, date)
            # 兜底逻辑：如果今天没价格，用缓存价格卖出(模拟)
            if not price: price = self.last_prices.get(code)

            if price:
                amt = self.holdings[code] * price
                cost = self.calculate_cost(amt, True)
                self.cash += amt - cost
                del self.holdings[code]

        # 2. 买入
        if not target_codes: return
        # 预留2%现金做缓冲
        per_cash = self.cash * 0.98 / len(target_codes)

        for code in target_codes:
            price = self.dm.get_price(code, date)
            if price:
                self.last_prices[code] = price
                # 向下取整到100股
                shares = int(per_cash / price / 100) * 100
                if shares >= 100:
                    cost = shares * price
                    fee = self.calculate_cost(cost, False)
                    if self.cash >= cost + fee:
                        self.cash -= (cost + fee)
                        self.holdings[code] = shares

    def _settle(self, date):
        holding_val = 0
        for code, shares in self.holdings.items():
            price = self.dm.get_price(code, date)
            if price:
                self.last_prices[code] = price
            else:
                price = self.last_prices.get(code, 0)
            holding_val += shares * price

        total_asset = self.cash + holding_val
        self.history_assets.append(total_asset)
        self.dates.append(date)