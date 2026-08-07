# -*- coding: utf-8 -*-
"""Optional Windows offline speech input with graceful text fallback."""

from __future__ import annotations

import subprocess


def capture_windows_speech(timeout_seconds: int = 10) -> str | None:
    command = rf"""
Add-Type -AssemblyName System.Speech
$culture=[System.Globalization.CultureInfo]::GetCultureInfo('zh-CN')
$recognizer=New-Object System.Speech.Recognition.SpeechRecognitionEngine($culture)
$recognizer.SetInputToDefaultAudioDevice()
$recognizer.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar))
$result=$recognizer.Recognize([TimeSpan]::FromSeconds({int(timeout_seconds)}))
if($null -ne $result){{[Console]::OutputEncoding=[Text.Encoding]::UTF8; $result.Text}}
"""
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=timeout_seconds + 5,
    )
    value = completed.stdout.strip()
    return value or None


def read_turn(mode: str) -> str:
    if mode == "voice":
        print("【语音】请开始说话……")
        spoken = capture_windows_speech()
        if spoken:
            print(f"【识别结果】{spoken}")
            return spoken
        print("【提示】本轮语音暂不可用，已自动切换为文字，不影响关卡进度。")
    return input("【文字输入】> ").strip()