import os
import akshare as ak
import pandas as pd
from core.data_models import StockInfo

for _k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
    os.environ.pop(_k, None)


class StockFilter:
    def fetch_and_filter(
        self,
        min_volume: float = 5000.0,
        min_change: float = -3.0,
        max_change: float = 7.0,
    ) -> list[StockInfo]:
        # 使用新浪财经接口，在 WSL/Linux 环境下可用
        df = ak.stock_zh_a_spot()
        df = df.rename(columns={
            "代码": "code", "名称": "name",
            "成交量": "volume", "涨跌幅": "change_pct"
        })
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0) / 10000
        df["change_pct"] = pd.to_numeric(df["change_pct"], errors="coerce").fillna(0)

        mask = (
            (df["volume"] >= min_volume) &
            (df["change_pct"] >= min_change) &
            (df["change_pct"] <= max_change) &
            (~df["name"].str.contains("ST", na=False))
        )
        filtered = df[mask].head(100)

        return [
            StockInfo(
                code=str(row["code"]),
                name=str(row["name"]),
                volume=float(row["volume"]),
                change_pct=float(row["change_pct"]),
            )
            for _, row in filtered.iterrows()
        ]
