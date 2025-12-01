from src.workflow import run_strategy_backtest

if __name__ == "__main__":
    try:
        run_strategy_backtest()
    except KeyboardInterrupt:
        print("\n\n用户终止了程序。")
    except Exception as e:
        print(f"\n❌ 程序发生错误: {e}")