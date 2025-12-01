import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
from ..config import INITIAL_CAPITAL

# 设置中文字体 (尝试适配 Windows/Mac/Linux)
plt.rcParams['axes.unicode_minus'] = False
font_list = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei', 'Heiti TC', 'sans-serif']
plt.rcParams['font.sans-serif'] = font_list


class PerformanceAnalyzer:
    def __init__(self, asset_series, benchmark_series):
        self.assets = asset_series
        self.benchmark = benchmark_series
        self._align_data()

    def _align_data(self):
        """对齐策略和基准的日期"""
        # 确保索引为 datetime 类型
        self.assets.index = pd.to_datetime(self.assets.index)
        self.benchmark.index = pd.to_datetime(self.benchmark.index)

        common_idx = self.assets.index.intersection(self.benchmark.index)
        self.assets = self.assets.loc[common_idx]
        self.benchmark = self.benchmark.loc[common_idx]

        # 归一化基准 (从初始资金开始画)
        if not self.benchmark.empty:
            self.benchmark = self.benchmark / self.benchmark.iloc[0] * INITIAL_CAPITAL

    def calculate_metrics(self):
        """计算核心指标与统计检验"""
        if self.assets.empty: return {}

        # --- 1. 基础收益指标 ---
        total_ret = (self.assets.iloc[-1] - INITIAL_CAPITAL) / INITIAL_CAPITAL
        days = len(self.assets)
        # 年化收益 (假设一年252个交易日)
        annual_ret = (1 + total_ret) ** (252 / days) - 1

        # --- 2. 风险指标 (回撤) ---
        cum_max = self.assets.cummax()
        drawdown = (self.assets - cum_max) / cum_max
        max_dd = drawdown.min()

        # --- 3. 统计指标 (Alpha/Beta/Sharpe) ---
        strat_ret = self.assets.pct_change().dropna()
        bench_ret = self.benchmark.pct_change().dropna()

        # 对齐收益率
        common_ret_idx = strat_ret.index.intersection(bench_ret.index)
        strat_ret = strat_ret.loc[common_ret_idx]
        bench_ret = bench_ret.loc[common_ret_idx]

        if len(strat_ret) > 10:
            # 线性回归计算 Alpha 和 Beta
            beta, alpha, r_val, p_val, std_err = stats.linregress(bench_ret, strat_ret)
            alpha_annual = alpha * 252

            # 夏普比率 (无风险利率设为 3%)
            rf = 0.03
            excess_ret = strat_ret - rf / 252
            sharpe = np.sqrt(252) * excess_ret.mean() / excess_ret.std()

            # --- 4. T检验 (统计显著性) ---
            # 检验超额收益 (Active Return) 是否显著大于 0
            active_ret = strat_ret - bench_ret
            t_stat, p_value_ttest = stats.ttest_1samp(active_ret, 0)
        else:
            beta, alpha_annual, sharpe = 0, 0, 0
            t_stat, p_value_ttest = 0, 1.0

        # Calmar 比率
        calmar = annual_ret / abs(max_dd) if max_dd != 0 else 0

        return {
            'final_asset': self.assets.iloc[-1],
            'total_ret': total_ret,
            'annual_ret': annual_ret,
            'max_dd': max_dd,
            'sharpe': sharpe,
            'calmar': calmar,
            'alpha': alpha_annual,
            'beta': beta,
            't_stat': t_stat,
            'p_value': p_value_ttest,
            'drawdown_series': drawdown
        }

    def plot(self):
        """绘制专业量化报告图表"""
        metrics = self.calculate_metrics()
        if not metrics: return

        # 创建画布布局 (3行: 指标卡片, 资金曲线, 回撤图)
        fig = plt.figure(figsize=(14, 10), constrained_layout=True)
        gs = gridspec.GridSpec(3, 1, height_ratios=[0.8, 3, 1], figure=fig)

        # === 区域 1: 核心指标仪表盘 ===
        ax_kpi = fig.add_subplot(gs[0])
        ax_kpi.axis('off')

        # 辅助函数：根据数值正负获取颜色
        def color(val, inverse=False):
            if inverse: return 'green' if val < 0 else 'red'
            return 'red' if val > 0 else 'green'

        # 定义指标展示内容
        kpi_data = [
            [
                ("初始本金", f"{INITIAL_CAPITAL}", 'black'),
                ("期末资产", f"{metrics['final_asset']:.0f}", 'red'),
                ("总收益率", f"{metrics['total_ret'] * 100:.2f}%", color(metrics['total_ret'])),
                ("年化收益", f"{metrics['annual_ret'] * 100:.2f}%", color(metrics['annual_ret'])),
            ],
            [
                ("最大回撤", f"{metrics['max_dd'] * 100:.2f}%", 'green'),  # 回撤通常绿色代表风险
                ("夏普比率", f"{metrics['sharpe']:.2f}", color(metrics['sharpe'] - 1)),  # >1 为红
                ("Calmar比", f"{metrics['calmar']:.2f}", 'black'),
                ("Beta系数", f"{metrics['beta']:.2f}", 'black'),
            ],
            [
                ("年化Alpha", f"{metrics['alpha'] * 100:.2f}%", color(metrics['alpha'])),
                ("T-统计量", f"{metrics['t_stat']:.2f}", 'black'),
                ("P-Value", f"{metrics['p_value']:.4f}", 'red' if metrics['p_value'] < 0.05 else 'gray'),
                ("统计结论", "显著" if metrics['p_value'] < 0.05 else "不显著",
                 'red' if metrics['p_value'] < 0.05 else 'gray'),
            ]
        ]

        # 绘制指标文本
        for row_idx, row_data in enumerate(kpi_data):
            y_pos = 0.8 - row_idx * 0.35
            for col_idx, (label, val, c) in enumerate(row_data):
                x_pos = 0.1 + col_idx * 0.25
                ax_kpi.text(x_pos, y_pos, label, fontsize=11, color='gray', ha='center', va='bottom')
                ax_kpi.text(x_pos, y_pos - 0.05, val, fontsize=15, fontweight='bold', color=c, ha='center', va='top')

        # === 区域 2: 资金曲线 ===
        ax_main = fig.add_subplot(gs[1])
        ax_main.plot(self.assets.index, self.assets, color='#d62728', lw=2, label='策略净值 (Strategy)')
        ax_main.plot(self.benchmark.index, self.benchmark, color='gray', ls='--', alpha=0.8,
                     label='基准净值 (Benchmark)')

        # 填充超额收益区域
        ax_main.fill_between(self.assets.index, self.assets, self.benchmark,
                             where=(self.assets >= self.benchmark), facecolor='red', alpha=0.1)
        ax_main.fill_between(self.assets.index, self.assets, self.benchmark,
                             where=(self.assets < self.benchmark), facecolor='green', alpha=0.1)

        ax_main.set_ylabel("资产净值 (元)", fontsize=12)
        ax_main.set_title("策略累计收益表现", fontsize=14, fontweight='bold')
        ax_main.legend(loc='upper left', frameon=True)
        ax_main.grid(True, linestyle='--', alpha=0.3)

        # === 区域 3: 动态回撤 ===
        ax_dd = fig.add_subplot(gs[2], sharex=ax_main)
        dd = metrics['drawdown_series']
        ax_dd.fill_between(dd.index, dd, 0, color='green', alpha=0.3)
        ax_dd.plot(dd.index, dd, color='green', lw=1)
        ax_dd.set_ylabel("回撤幅度", fontsize=12)
        ax_dd.set_title("水下回撤曲线 (Drawdown)", fontsize=10, loc='left')
        ax_dd.grid(True, linestyle='--', alpha=0.3)

        plt.show()