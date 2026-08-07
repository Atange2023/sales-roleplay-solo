from __future__ import annotations

import importlib.util
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEECH_PATH = ROOT / "scripts" / "speech_input.py"


def load_speech():
    spec = importlib.util.spec_from_file_location("speech_input_v043", SPEECH_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class SpeechInputUxTests(unittest.TestCase):
    def test_voice_transcript_is_returned_with_friendly_chinese_status(self) -> None:
        speech = load_speech()
        output = io.StringIO()
        with patch.object(speech, "capture_windows_speech", return_value="我想了解学习安排"), redirect_stdout(output):
            self.assertEqual(speech.read_turn("voice"), "我想了解学习安排")
        self.assertIn("【语音】请开始说话", output.getvalue())
        self.assertIn("【识别结果】我想了解学习安排", output.getvalue())

    def test_voice_failure_switches_to_text_without_technical_language(self) -> None:
        speech = load_speech()
        output = io.StringIO()
        with patch.object(speech, "capture_windows_speech", return_value=None), patch("builtins.input", return_value="文字回答"), redirect_stdout(output):
            self.assertEqual(speech.read_turn("voice"), "文字回答")
        message = output.getvalue()
        self.assertIn("本轮语音暂不可用，已自动切换为文字，不影响关卡进度", message)
        self.assertNotIn("回退", message)


if __name__ == "__main__":
    unittest.main()
