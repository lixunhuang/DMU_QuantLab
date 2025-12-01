from src.tools.data_manager import DataManager
from .strategies.small_cap_pb_big_pe import SmallCapValueStrategy
from .backtest.engine import BacktestEngine
from .backtest.analyzer import PerformanceAnalyzer
from datetime import datetime, timedelta


def run_strategy_backtest():
    """执行完整的策略回测流程"""
    print("\n" + "=" * 50)
    print("🚀 启动量化回测工作流")
    print("=" * 50)

    # 1. 数据准备
    dm = DataManager()
    # 建议定期运行 update_data，平常回测注释掉以节省时间
    # dm.update_data()

    # 2. 配置回测区间
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=365 * 3)).strftime('%Y%m%d')  # 跑最近3年

    # 3. 初始化策略
    # 这里选择了 '小盘价值策略'，你可以换成别的
    print(">>> 正在加载策略模型...")
    strategy = SmallCapValueStrategy(dm, hold_count=10)

    # 4. 运行回测引擎
    engine = BacktestEngine(dm, strategy, start_date, end_date)
    asset_curve = engine.run()

    # 5. 绩效分析
    if not asset_curve.empty:
        print(">>> 正在计算统计指标并绘图...")
        benchmark = dm.get_benchmark(start_date, end_date)
        analyzer = PerformanceAnalyzer(asset_curve, benchmark)
        analyzer.plot()
    else:
        print("❌ 回测生成了空的资产曲线，请检查策略或数据。")