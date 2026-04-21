import json
import sys
from datetime import datetime, date
from pathlib import Path
from core.data_models import GuaXiang


class LiuYaoEngine:
    def __init__(self):
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent.parent))
        data_path = base / "assets" / "gua_data.json"
        with open(data_path, encoding="utf-8") as f:
            self._data = json.load(f)

    def qigua(self, stock_code: str = "") -> GuaXiang:
        now = datetime.now()
        year, month, day, hour = now.year, now.month, now.day, now.hour
        shichen = self._get_shichen(hour)

        # 提取股票代码中的纯数字之和，作为个股区分因子
        code_sum = sum(int(c) for c in stock_code if c.isdigit())

        upper_idx = (year + month + day + code_sum) % 8 or 8
        lower_idx = (year + month + day + shichen + code_sum) % 8 or 8
        dong_yao = (year + month + day + shichen + code_sum) % 6 or 6

        upper_yaos = self._data["bagua"][str(upper_idx)]["yaos"]
        lower_yaos = self._data["bagua"][str(lower_idx)]["yaos"]
        yao_list = lower_yaos + upper_yaos  # 初爻在下，上爻在上

        upper_name = self._data["bagua"][str(upper_idx)]["name"]
        lower_name = self._data["bagua"][str(lower_idx)]["name"]
        gua_name = f"{upper_name}{lower_name}"

        return GuaXiang(
            upper_gua=upper_idx,
            lower_gua=lower_idx,
            dong_yao=dong_yao,
            yao_list=yao_list,
            gua_name=gua_name,
        )

    def _get_shichen(self, hour: int) -> int:
        shichen_map = {23: 1, 0: 1, 1: 2, 2: 2, 3: 3, 4: 3, 5: 4, 6: 4,
                       7: 5, 8: 5, 9: 6, 10: 6, 11: 7, 12: 7, 13: 8, 14: 8,
                       15: 9, 16: 9, 17: 10, 18: 10, 19: 11, 20: 11, 21: 12, 22: 12}
        return shichen_map[hour]

    def _get_rigan(self, d: date) -> str:
        base = date(2000, 1, 1)
        delta = (d - base).days
        tiangan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        return tiangan[delta % 10]

    def get_rigan_wuxing(self) -> str:
        today = datetime.now().date()
        rigan = self._get_rigan(today)
        return self._data["tiangan_wuxing"][rigan]
