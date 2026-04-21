import json
from pathlib import Path
from core.data_models import GuaXiang, GuaAnalysis

# 五行相生：金生水、水生木、木生火、火生土、土生金
_SHENG = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}
# 五行相克：金克木、木克土、土克水、水克火、火克金
_KE = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}

_BAGUA_WUXING = {"1": "金", "2": "金", "3": "火", "4": "木",
                  "5": "木", "6": "水", "7": "土", "8": "土"}

_LIUSHEN = ["青龙", "朱雀", "勾陈", "腾蛇", "白虎", "玄武"]


class GuaAnalyzer:
    def __init__(self):
        data_path = Path(__file__).parent.parent / "assets" / "gua_data.json"
        with open(data_path, encoding="utf-8") as f:
            self._data = json.load(f)

    def analyze(self, gua: GuaXiang, rigan_wuxing: str) -> GuaAnalysis:
        yao_wuxing = self._get_yao_wuxing(gua)
        liu_qin = self._get_liu_qin(yao_wuxing, rigan_wuxing)
        liu_shen = self._get_liu_shen()

        caicai_positions = [i for i, q in enumerate(liu_qin) if q == "妻财"]
        if caicai_positions:
            yong_pos = caicai_positions[0]
            yong_shen = f"{yong_pos + 1}爻（妻财）"
            yong_wuxing = yao_wuxing[yong_pos]
        else:
            yong_pos = 0
            yong_shen = "1爻（无妻财，取初爻）"
            yong_wuxing = yao_wuxing[0]

        state, reasons = self._judge_wangshuai(
            yong_wuxing, yong_pos, gua.dong_yao - 1, yao_wuxing, liu_qin, rigan_wuxing
        )
        conclusion = self._get_conclusion(state)

        return GuaAnalysis(
            liu_qin=liu_qin,
            liu_shen=liu_shen,
            yong_shen=yong_shen,
            yong_shen_state=state,
            reasons=reasons,
            conclusion=conclusion,
        )

    def _get_yao_wuxing(self, gua: GuaXiang) -> list[str]:
        lower_wx = _BAGUA_WUXING[str(gua.lower_gua)]
        upper_wx = _BAGUA_WUXING[str(gua.upper_gua)]
        return [lower_wx] * 3 + [upper_wx] * 3

    def _get_liu_qin(self, yao_wuxing: list[str], rigan_wuxing: str) -> list[str]:
        table = self._data["liuqin_wuxing"][rigan_wuxing]
        return [table[wx] for wx in yao_wuxing]

    def _get_liu_shen(self) -> list[str]:
        return _LIUSHEN.copy()

    def _judge_wangshuai(
        self, yong_wuxing: str, yong_pos: int, dong_idx: int,
        yao_wuxing: list[str], liu_qin: list[str], rigan_wuxing: str
    ) -> tuple[str, list[str]]:
        reasons = []
        score = 0

        if _SHENG[rigan_wuxing] == yong_wuxing or rigan_wuxing == yong_wuxing:
            score += 2
            reasons.append(f"日干（{rigan_wuxing}）生扶用神（{yong_wuxing}），用神旺相")

        if _KE[rigan_wuxing] == yong_wuxing:
            score -= 2
            reasons.append(f"日干（{rigan_wuxing}）克用神（{yong_wuxing}），用神受克")

        dong_wx = yao_wuxing[dong_idx]
        if _SHENG[dong_wx] == yong_wuxing:
            score += 1
            reasons.append(f"动爻（{dong_wx}）生用神，有利")
        elif _KE[dong_wx] == yong_wuxing:
            score -= 1
            reasons.append(f"动爻（{dong_wx}）克用神，不利")

        if liu_qin[dong_idx] == "官鬼":
            score -= 1
            reasons.append("官鬼爻动，忌神发动，不利财爻")

        if not reasons:
            reasons.append("用神无明显生克，卦象平和")

        if score >= 2:
            return "旺", reasons
        elif score <= -1:
            return "衰", reasons
        else:
            return "平", reasons

    def _get_conclusion(self, state: str) -> str:
        if state == "旺":
            return "宜买"
        elif state == "衰":
            return "不宜"
        else:
            return "观望"
