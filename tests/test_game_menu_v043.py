from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MENU_PATH = ROOT / "scripts" / "game_menu.py"


def load_menu():
    spec = importlib.util.spec_from_file_location("game_menu_v043", MENU_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class ChineseGameMenuTests(unittest.TestCase):
    def test_title_and_tutorial_are_player_facing_chinese(self) -> None:
        menu = load_menu()
        title = menu.render_title()
        self.assertIn("SALES ROLEPLAY SOLO", title)
        self.assertIn("销售实战模拟训练系统", title)
        self.assertIn("版本 0.4.3", title)
        self.assertIn("你扮演招生老师", menu.TUTORIAL)
        self.assertIn("最多 20 个有效回合", menu.TUTORIAL)
        for leaked in ("TTS", "MP3", "JSON", "manifest", "动态回退", "内部思考"):
            self.assertNotIn(leaked, title + menu.TUTORIAL)

    def test_numbered_dlc_and_stage_menus_use_chinese_status(self) -> None:
        menu = load_menu()
        config = menu.load_config()
        dlcs = menu.render_dlc_menu(config)
        stages = menu.render_stage_menu(config, menu.default_progress(), "DLC02")
        self.assertIn("【1】制造业", dlcs)
        self.assertIn("【2】商学院", dlcs)
        self.assertNotIn("AVAILABLE", dlcs)
        self.assertIn("【1】潜在学员需求诊断　【已解锁】", stages)
        self.assertIn("【2】报名政策与价格谈判　【未解锁】", stages)
        self.assertIn("默认难度：正常", stages)
        self.assertIn("1 简单", stages)
        self.assertIn("【输入方式】直接输入文字，或点击麦克风说话", stages)
        self.assertIn("【语音指令】输入 /voice 可启用本机录音", stages)

    def test_numeric_choices_resolve_and_stage_choice_carries_difficulty(self) -> None:
        menu = load_menu()
        config = menu.load_config()
        self.assertEqual(menu.resolve_dlc_choice(config, "2"), "DLC02")
        self.assertEqual(menu.parse_stage_choice(config, "DLC02", "1"), ("L01", "正常"))
        self.assertEqual(menu.parse_stage_choice(config, "DLC02", "1 简单"), ("L01", "简单"))
        self.assertEqual(menu.parse_stage_choice(config, "DLC02", "L01 困难"), ("L01", "困难"))
        with self.assertRaises(ValueError):
            menu.parse_stage_choice(config, "DLC02", "1 地狱")

    def test_selecting_an_unlocked_stage_immediately_returns_loading_card(self) -> None:
        menu = load_menu()
        output = menu.render_loading_card("DLC02", "L01", "简单")
        self.assertIn("关卡数据载入中", output)
        self.assertIn("教练分析数据载入中", output)
        self.assertIn("潜在学员需求诊断", output)
        self.assertIn("难度：简单", output)
        self.assertNotIn("请再输入开始", output)


if __name__ == "__main__":
    unittest.main()
