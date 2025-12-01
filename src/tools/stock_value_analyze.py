import sys
import os
import pandas as pd

# 将项目根目录加入路径，以便导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from src.tools.data_manager import DataManager


class StockValuator:
    def __init__(self):
        self.dm = DataManager()
        # 预加载最新一天的数据用于全市场对比
        print(">>> [Valuator] 正在加载全市场数据以进行估值对比...")
        dates = self.dm.get_trade_dates('20230101', '20991231')
        if not dates:
            print("错误：数据库无数据，请先运行回测流程下载数据。")
            self.latest_df = pd.DataFrame()
        else:
            self.latest_date = dates[-1]
            self.latest_df = self.dm.get_daily_cross_section(self.latest_date)
            print(f">>> 数据基准日: {self.latest_date}")

    def analyze(self, ts_code):
        """分析单只股票"""
        if self.latest_df.empty: return

        # 查找目标股票
        target = self.latest_df[self.latest_df['ts_code'] == ts_code]

        if target.empty:
            print(f"❌ 未找到代码 {ts_code} 的数据（可能已退市或代码错误）。")
            return

        # 提取指标
        name = target['name'].values[0]
        industry = target['industry'].values[0]
        close = target['close'].values[0]
        pe = target['pe_ttm'].values[0]
        pb = target['pb'].values[0]
        mv = target['total_mv'].values[0]

        # 计算全市场排名 (百分位)
        # mean() * 100 得到的是 "打败了百分之多少的人"
        # 我们这里计算 "排在百分之多少的位置" (数值越小越便宜/规模越小)
        pe_rank = (self.latest_df['pe_ttm'] < pe).mean() * 100
        pb_rank = (self.latest_df['pb'] < pb).mean() * 100
        mv_rank = (self.latest_df['total_mv'] > mv).mean() * 100  # 市值越大，rank越靠前(数值小)

        print("\n" + "=" * 40)
        print(f"🔍 个股基本面诊断报告: {name} ({ts_code})")
        print("=" * 40)
        print(f"【基础信息】")
        print(f"  所属行业 : {industry}")
        print(f"  当前价格 : {close} 元")
        print(f"  总市值   : {mv / 10000:.2f} 亿 (全市场排名 Top {mv_rank:.1f}%)")
        print("-" * 40)
        print(f"【估值水位】")
        print(f"  PE (TTM) : {pe:.2f}")
        print(f"  -> 状态  : 比全市场 {pe_rank:.1f}% 的股票更贵")
        print(f"  PB (MRQ) : {pb:.2f}")
        print(f"  -> 状态  : 比全市场 {pb_rank:.1f}% 的股票更贵")
        print("-" * 40)

        # 简易评级逻辑
        print(f"【AI 综合评价】")
        if pe_rank < 20 and pb_rank < 20:
            print("  🟢 [极具价值] 双低估值，安全边际极高（捡烟蒂策略）。")
        elif pe_rank > 80 and pb_rank > 80:
            print("  🔴 [高估风险] 估值处于市场高位，需确认是否有高成长支撑。")
        elif mv_rank < 10 and pe_rank < 50:
            print("  🔵 [核心资产] 大市值且估值合理，适合作为底仓。")
        else:
            print("  ⚪ [中性] 估值在合理区间，建议结合技术面分析。")
        print("=" * 40 + "\n")


if __name__ == "__main__":
    tool = StockValuator()

    while True:
        code = input("请输入股票代码 (例如 600519.SH) 或输入 q 退出: ").strip()
        if code.lower() == 'q':
            break
        tool.analyze(code)