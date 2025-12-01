from .base import BaseStrategy
import pandas as pd


class SmallCapValueStrategy(BaseStrategy):
    """
    策略：小市值 + 低PB/PE + 高盈利 (改进版)
    """

    def __init__(self, data_manager, hold_count=5):
        super().__init__(data_manager)
        self.hold_count = hold_count

    def select_stocks(self, date):
        df = self.dm.get_daily_cross_section(date)
        if df.empty: return []

        # 1. 基础过滤
        df = df[~df['name'].str.contains('ST')]
        df = df[df['pe_ttm'] > 0]
        # 过滤高价股，确保小资金能买得起
        df = df[df['close'] < 35]

        # 2. 因子计算 (Ranking)
        # 市值越小越好 (Rank 1 = Smallest)
        rank_size = df['total_mv'].rank(ascending=True)
        # PB越低越好 (Rank 1 = Lowest PB)
        rank_pb = df['pb'].rank(ascending=True)
        # PE越高越好 (Rank 1 = Highest PE)
        rank_pe = df['pe_ttm'].rank(ascending=True)

        # 综合打分：40%看盈利，30%看便宜，30%看市值
        # 这种组合比纯粹买微盘股要稳健
        df['score'] = 0.3 * rank_size + 0.3 * rank_pb + 0.4 * rank_pe

        # 3. 选出得分最低(排名最靠前)的N只
        picks = df.sort_values('score').head(self.hold_count)
        return picks['ts_code'].tolist()