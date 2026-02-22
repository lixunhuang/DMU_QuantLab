import os

# ================= 数据配置 =================
# 请替换为你自己的 Tushare Token
TS_TOKEN = ''

# 数据库路径 (自动定位到项目根目录下的 data 文件夹)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DB_PATH = os.path.join(DATA_DIR, 'stock_data.db')

# ================= 回测参数 =================
INITIAL_CAPITAL = 20000  # 初始资金
DOWNLOAD_YEARS = 10  # 下载数据年限

# ================= 费率设置 =================
TAX_RATE = 0.001  # 印花税 (千1)
COMMISSION_RATE = 0.0003  # 佣金 (万3)
MIN_COMMISSION = 5  # 最低佣金 (5元)
