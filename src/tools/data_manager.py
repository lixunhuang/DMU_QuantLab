import tushare as pro
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
import sys
from src.config import TS_TOKEN, DB_PATH, DOWNLOAD_YEARS


class DataManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.pro = pro.pro_api(TS_TOKEN)
            self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.init_db()
            self.initialized = True

    def init_db(self):
        """初始化数据库表结构"""
        cursor = self.conn.cursor()
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS daily (ts_code TEXT, trade_date TEXT, close REAL, open REAL, high REAL, low REAL, vol REAL, PRIMARY KEY (ts_code, trade_date))''')
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS daily_basic (ts_code TEXT, trade_date TEXT, pe_ttm REAL, pb REAL, total_mv REAL, turnover_rate REAL, PRIMARY KEY (ts_code, trade_date))''')
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS stock_basic (ts_code TEXT PRIMARY KEY, name TEXT, industry TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS index_daily (trade_date TEXT PRIMARY KEY, close REAL)''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date_price ON daily (trade_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date_basic ON daily_basic (trade_date)')
        self.conn.commit()

    def update_data(self):
        """全量数据下载/更新"""
        print(f">>> [DataManager] 正在检查数据完整性 (DB: {DB_PATH})...")
        end_date = datetime.now().strftime('%Y%m%d')

        cursor = self.conn.cursor()
        cursor.execute('SELECT MAX(trade_date) FROM index_daily')
        last_date = cursor.fetchone()[0]

        if last_date and last_date >= (datetime.now() - timedelta(days=1)).strftime('%Y%m%d'):
            print(">>> 数据已是最新，跳过下载。")
            return

        start_date = (datetime.now() - timedelta(days=DOWNLOAD_YEARS * 365)).strftime('%Y%m%d')
        if last_date:
            start_date = (datetime.strptime(last_date, "%Y%m%d") + timedelta(days=1)).strftime("%Y%m%d")

        print(f">>> 开始下载数据: {start_date} -> {end_date}")

        # 1. 股票列表
        df_info = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,name,industry')
        df_info.to_sql('stock_basic', self.conn, if_exists='replace', index=False)

        # 2. 交易日历
        dates = self.pro.trade_cal(exchange='', start_date=start_date, end_date=end_date, is_open='1')[
            'cal_date'].tolist()

        for i, date in enumerate(dates):
            sys.stdout.write(f"\r下载进度: {i + 1}/{len(dates)} ({date})")
            sys.stdout.flush()
            try:
                # 指数
                df_index = self.pro.index_daily(ts_code='000300.SH', trade_date=date, fields='trade_date,close')
                if not df_index.empty: df_index.to_sql('index_daily', self.conn, if_exists='append', index=False)

                # 行情
                df_daily = self.pro.daily(trade_date=date, fields='ts_code,trade_date,close,open,high,low,vol')
                if not df_daily.empty: df_daily.to_sql('daily', self.conn, if_exists='append', index=False)

                # 指标
                df_basic = self.pro.daily_basic(trade_date=date,
                                                fields='ts_code,trade_date,pe_ttm,pb,total_mv,turnover_rate')
                if not df_basic.empty: df_basic.to_sql('daily_basic', self.conn, if_exists='append', index=False)
            except Exception as e:
                print(f" Err: {e}")
                continue
        print("\n>>> 数据同步完成！")
        self.conn.commit()

    def get_daily_cross_section(self, date):
        """获取某日选股所需的全量数据 (Price + Valuation + Info)"""
        query = f'''
            SELECT a.ts_code, a.close, b.pe_ttm, b.pb, b.total_mv, b.turnover_rate, c.name, c.industry
            FROM daily a
            JOIN daily_basic b ON a.ts_code = b.ts_code AND a.trade_date = b.trade_date
            JOIN stock_basic c ON a.ts_code = c.ts_code
            WHERE a.trade_date = '{date}'
        '''
        return pd.read_sql(query, self.conn)

    def get_price(self, code, date):
        """获取单只股票特定日期的价格"""
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT close FROM daily WHERE ts_code='{code}' AND trade_date='{date}'")
        res = cursor.fetchone()
        return res[0] if res else None

    def get_trade_dates(self, start_date, end_date):
        """获取区间内的交易日列表"""
        query = f"SELECT trade_date FROM index_daily WHERE trade_date BETWEEN '{start_date}' AND '{end_date}' ORDER BY trade_date"
        df = pd.read_sql(query, self.conn)
        return df['trade_date'].tolist()

    def get_benchmark(self, start_date, end_date):
        """获取基准指数数据"""
        query = f"SELECT trade_date, close FROM index_daily WHERE trade_date BETWEEN '{start_date}' AND '{end_date}' ORDER BY trade_date"
        df = pd.read_sql(query, self.conn)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        return df.set_index('trade_date')['close']