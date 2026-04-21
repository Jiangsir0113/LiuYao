# tests/test_gua_analyzer.py
from core.gua_analyzer import GuaAnalyzer
from core.data_models import GuaXiang

def _make_gua():
    # 上坎(6)下离(3)：水火既济，动爻第3爻
    return GuaXiang(
        upper_gua=6, lower_gua=3, dong_yao=3,
        yao_list=["阳","阴","阳","阴","阳","阴"],
        gua_name="水火既济"
    )

def test_analyze_returns_gua_analysis():
    analyzer = GuaAnalyzer()
    gua = _make_gua()
    result = analyzer.analyze(gua, rigan_wuxing="木")
    assert len(result.liu_qin) == 6
    assert len(result.liu_shen) == 6
    assert result.conclusion in ["宜买", "观望", "不宜"]

def test_liu_qin_all_valid():
    analyzer = GuaAnalyzer()
    gua = _make_gua()
    result = analyzer.analyze(gua, rigan_wuxing="木")
    valid = {"父母", "兄弟", "子孙", "妻财", "官鬼"}
    for qin in result.liu_qin:
        assert qin in valid

def test_liu_shen_all_valid():
    analyzer = GuaAnalyzer()
    gua = _make_gua()
    result = analyzer.analyze(gua, rigan_wuxing="木")
    valid = {"青龙", "朱雀", "勾陈", "腾蛇", "白虎", "玄武"}
    for shen in result.liu_shen:
        assert shen in valid

def test_yong_shen_is_caicai():
    analyzer = GuaAnalyzer()
    gua = _make_gua()
    result = analyzer.analyze(gua, rigan_wuxing="木")
    assert "妻财" in result.yong_shen

def test_reasons_not_empty():
    analyzer = GuaAnalyzer()
    gua = _make_gua()
    result = analyzer.analyze(gua, rigan_wuxing="木")
    assert len(result.reasons) > 0
