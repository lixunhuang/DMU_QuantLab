# DMU_QuantLab - 模块化量化投研系统 🚀

**DMU_QuantLab** 是一个基于 Python 的轻量级、模块化量化回测与分析框架。它专为理工科背景的交易者设计，支持从数据获取、策略开发、回测执行到绩效分析的全流程自动化。

本项目采用**本地数据库 (SQLite)** 存储方案，实现了数据的增量更新与毫秒级读取，并提供了机构级的可视化回测报告。

## 📂 项目结构说明

```text
DMU_QuantLab/
├── data/                   # [数据层] 存放本地数据 (Git忽略)
│   └── stock_data.db       # SQLite数据库，存储全市场行情与财务指标
│
├── docs/                   # [知识库] 存放学习资料
│   ├── papers/             # 经典量化论文 (PDF)
│   └── notes/              # 研报与学习笔记
│
├── src/                    # [核心源码]
│   ├── config.py           # 全局配置 (Token, 费率, 回测参数)
│   ├── workflow.py         # 工作流管理器 (串联各模块)
│   │
│   ├── strategies/         # [策略库] 存放具体的交易策略
│   │   ├── base.py         # 策略基类 (所有新策略必须继承此类)
│   │   └── small_cap_value.py  # 示例：小盘价值轮动策略
│   │
│   ├── backtest/           # [回测引擎]
│   │   ├── engine.py       # 交易撮合核心逻辑
│   │   └── analyzer.py     # 绩效分析器 (绘制专业图表, 计算Alpha/Sharpe)
│   │
│   └── tools/              # [投研工具箱]
│       ├── stock_valuator.py   # 个股基本面诊断工具 (人工选股用)
│       ├── data_manager.py     # 数据管家 (负责下载、更新、清洗数据)
│
├── run_backtest.py         # [入口] 一键启动回测脚本
├── requirements.txt        # Python 依赖包列表
└── README.md               # 项目说明书
````

## 🛠️ 快速开始

### 1\. 环境准备

推荐使用 Python 3.8+。

```
# 克隆仓库
git clone https://github.com/YourUsername/DMU_QuantLab.git
cd DMU_QuantLab

# 安装依赖
pip install -r requirements.txt
```

### 2\. 配置 Token

打开 `src/config.py`，找到 `TS_TOKEN` 字段，填入你的 Tushare Token。

```python
# src/config.py
TS_TOKEN = 'PASTE_YOUR_TOKEN_HERE'
```

### 3\. 数据初始化

首次运行回测时，系统会自动检测并下载过去 10 年的全市场数据（约需 10-20 分钟）。

```
# 启动回测 (自动触发数据下载)
python run_backtest.py
```

## 🖥️ 功能使用指南

### 场景 A：运行策略回测

想要测试某个策略的历史表现？直接运行根目录下的脚本：

```
python run_backtest.py
```

  * **输出**：控制台打印详细的交易日志，结束后弹出一张包含资金曲线、回撤图、夏普比率、T检验结果的专业图表。
  * **修改策略**：去 `src/workflow.py` 中修改 `strategy = ...` 即可切换不同策略。

### 场景 B：个股基本面诊断 (人工看盘)

当你想查询某只股票（如平安银行）当前的估值水位时，不需要跑回测，直接使用工具箱：

```
python src/tools/stock_valuator.py
```

  * **交互**：输入股票代码（如 `000001.SZ`），系统会基于本地数据库，计算其 PE/PB 在全市场的百分位排名，并给出“低估/高估”的 AI 评价。

### 场景 C：开发新策略

想尝试 LSTM 或 双均线策略？

1.  在 `src/strategies/` 下新建文件（如 `my_strategy.py`）。
2.  继承 `BaseStrategy` 类。
3.  实现 `select_stocks(date)` 方法，返回当日想买的股票代码列表。

## 🤝 协作开发规范 (必读)

本项目为**私有协作仓库**，请严格遵守以下 Git 流程：

1.  **禁止直接推送到 `main` 分支**

      * `main` 分支受保护，仅用于发布稳定版本。

2.  **开发流程 (Feature Branch Workflow)**

      * **新建分支**：每次开发新功能或修改代码前，请从 `main` 切出一个新分支。
        ```bash
        git checkout main
        git pull origin main
        git checkout -b feature-你的功能名 (例如: feature-add-lstm)
        ```
      * **提交代码**：在你的分支上进行修改和 Commit。
      * **推送分支**：`git push origin feature-你的功能名`

3.  **代码合并 (Pull Request)**

      * 开发完成后，在 GitHub 页面发起 **Pull Request (PR)**。
      * **Code Review**：必须经过管理员（Repository Owner）的代码审查（Approve）后，才能合并入 `main`。

## ⚠️ 免责声明

本项目仅供计算机金融（FinTech）学习与研究使用。回测结果基于历史数据，**不代表未来表现**。代码中包含的策略不构成任何投资建议。实盘交易风险自负。
