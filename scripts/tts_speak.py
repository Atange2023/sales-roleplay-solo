# -*- coding: utf-8 -*-
"""数字人语音模块：edge-tts 合成 + ffplay 播放

用法（在 Git Bash 或 PowerShell 中）：
  py 03_tts_播放.py "文本内容"                      # 默认张总男声，合成并播放
  py 03_tts_播放.py "文本" --voice zh-CN-XiaoxiaoNeural --rate -5%
  py 03_tts_播放.py --batch                         # 从 02_台词数据库.json 批量合成到 audio/
  py 03_tts_播放.py --play B3_loss                  # 播放台词库中某条（按 id）

依赖：pip install edge-tts；播放器 ffplay（FFmpeg 自带）。
"""
import sys, os, subprocess, json, asyncio, tempfile

sys.stdout.reconfigure(encoding='utf-8')
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)                     # 仓库根目录
AUDIO_DIR = os.path.join(ROOT, 'audio')
AUDIO3_DIR = os.path.join(ROOT, 'audio3')
AUDIO4_DIR = os.path.join(ROOT, 'audio4')
SINGLE_DB = os.path.join(ROOT, 'scenarios', 'zhang_dialogue.json')
THREE_DB = os.path.join(ROOT, 'scenarios', 'three_party_dialogue.json')
BIZ_DB = os.path.join(ROOT, 'scenarios', 'business_school_dialogue.json')

DEFAULT_VOICE = 'zh-CN-YunyangNeural'   # 沉稳男声（张总）
DEFAULT_RATE = '-8%'                    # 语速稍慢，像 50+ 老板


def speak(text, voice=DEFAULT_VOICE, rate=DEFAULT_RATE, play=True, out=None, quiet=False, retries=3):
    """合成一段文本为 mp3（edge-tts Python API，规避命令行中文编码问题），可选播放（ffplay）。
    内置重试：edge-tts 偶发 NoAudioReceived（网络限流），最多重试 retries 次。"""
    import asyncio, edge_tts, time
    out = out or os.path.join(tempfile.gettempdir(), 'tts_tmp.mp3')

    async def _gen():
        comm = edge_tts.Communicate(text, voice, rate=rate)
        await comm.save(out)

    for attempt in range(1, retries + 1):
        try:
            asyncio.run(_gen())
            break
        except Exception:
            if attempt >= retries:
                raise
            time.sleep(2 * attempt)

    if play:
        subprocess.run(['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', out])
    if not quiet:
        print('OK ->', out)
    return out


def batch_synth():
    """从单人台词库 JSON 批量合成全部台词到 audio/（不播放）。"""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    with open(SINGLE_DB, encoding='utf-8') as f:
        db = json.load(f)
    voice = db['persona']['voice']
    rate = db['persona']['rate']
    items = [(o['id'], [o['text']]) for o in db['openings']]
    items += [(b['id'], b['replies']) for b in db['branches']]
    n = 0
    for key, texts in items:
        for i, text in enumerate(texts):
            name = f"{key}_{i+1}.mp3"
            speak(text, voice=voice, rate=rate, play=False,
                  out=os.path.join(AUDIO_DIR, name), quiet=True)
            n += 1
    print(f'批量合成完成：{n} 条 -> {AUDIO_DIR}')


def batch_synth4():
    """商学院台词库批量合成（三类学员按角色 voice）到 audio4/。"""
    os.makedirs(AUDIO4_DIR, exist_ok=True)
    with open(BIZ_DB, encoding='utf-8') as f:
        db = json.load(f)
    chars = db['characters']
    n = 0
    for b in db['branches']:
        ch = chars[b['char']]
        for i, text in enumerate(b['replies']):
            speak(text, voice=ch['voice'], rate=ch['rate'], play=False,
                  out=os.path.join(AUDIO4_DIR, f"{b['char']}_{b['id']}_{i+1}.mp3"), quiet=True)
            n += 1
    print(f'商学院台词合成完成：{n} 条 -> {AUDIO4_DIR}')


def batch_synth3():
    """从三人台词库批量合成（按角色 voice/rate）到 audio3/（不播放）。"""
    os.makedirs(AUDIO3_DIR, exist_ok=True)
    with open(THREE_DB, encoding='utf-8') as f:
        db = json.load(f)
    chars = db['characters']
    n = 0
    for b in db['branches']:
        ch = chars[b['char']]
        for i, text in enumerate(b['replies']):
            name = f"{b['char']}_{b['id']}_{i+1}.mp3"
            speak(text, voice=ch['voice'], rate=ch['rate'], play=False,
                  out=os.path.join(AUDIO3_DIR, name), quiet=True)
            n += 1
    print(f'三人台词合成完成：{n} 条 -> {AUDIO3_DIR}')


def play_by_id(key):
    """播放台词库中指定 id 的第一条（--play <id>），单人/三人库都支持。"""
    for path, is_three in ((SINGLE_DB, False), (THREE_DB, True)):
        with open(path, encoding='utf-8') as f:
            db = json.load(f)
        if not is_three:
            for it in db['openings'] + db['branches']:
                if it['id'] == key:
                    speak(it['replies'][0] if 'replies' in it else it['text'],
                          voice=db['persona']['voice'], rate=db['persona']['rate'])
                    return
        else:
            for it in db['branches']:
                if it['id'] == key:
                    ch = db['characters'][it['char']]
                    speak(it['replies'][0], voice=ch['voice'], rate=ch['rate'])
                    return
    print('未找到 id:', key)


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print(__doc__)
    elif args[0] == '--batch':
        batch_synth()
    elif args[0] == '--batch3':
        batch_synth3()
    elif args[0] == '--batch4':
        batch_synth4()
    elif args[0] == '--play' and len(args) > 1:
        play_by_id(args[1])
    else:
        text = args[0]
        voice = DEFAULT_VOICE
        rate = DEFAULT_RATE
        i = 1
        while i < len(args):
            if args[i] == '--voice' and i + 1 < len(args):
                voice = args[i + 1]; i += 2
            elif args[i] == '--rate' and i + 1 < len(args):
                rate = args[i + 1]; i += 2
            else:
                i += 1
        speak(text, voice=voice, rate=rate)
