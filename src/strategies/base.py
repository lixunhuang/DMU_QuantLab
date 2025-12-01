from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """策略抽象基类"""
    def __init__(self, data_manager):
        self.dm = data_manager

    @abstractmethod
    def select_stocks(self, date):
        """
        核心选股逻辑
        :param date: 交易日期 (YYYYMMDD)
        :return: 目标持仓股票代码列表 [code1, code2, ...]
        """
        pass