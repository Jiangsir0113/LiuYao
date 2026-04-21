# tests/test_liuyao_engine.py
from unittest.mock import patch
import datetime
from core.liuyao_engine import LiuYaoEngine

def test_qigua_returns_gua_xiang():
    engine = LiuYaoEngine()
    fixed_dt = datetime.datetime(2026, 4, 21, 9, 0, 0)
    with patch("core.liuyao_engine.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_dt
        gua = engine.qigua()
    assert gua.upper_gua in range(1, 9)
    assert gua.lower_gua in range(1, 9)
    assert gua.dong_yao in range(1, 7)
    assert len(gua.yao_list) == 6
    assert all(y in ["阳", "阴"] for y in gua.yao_list)

def test_qigua_deterministic():
    engine = LiuYaoEngine()
    fixed_dt = datetime.datetime(2026, 4, 21, 9, 0, 0)
    with patch("core.liuyao_engine.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_dt
        gua1 = engine.qigua()
        gua2 = engine.qigua()
    assert gua1.upper_gua == gua2.upper_gua
    assert gua1.lower_gua == gua2.lower_gua
    assert gua1.dong_yao == gua2.dong_yao

def test_get_shichen():
    engine = LiuYaoEngine()
    assert engine._get_shichen(23) == 1
    assert engine._get_shichen(1) == 2
    assert engine._get_shichen(9) == 6

def test_get_rigan():
    engine = LiuYaoEngine()
    gan = engine._get_rigan(datetime.date(2026, 4, 21))
    assert gan in ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
