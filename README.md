# sales-roleplay-solo v0.4.3

面向主流 Agent 的中文智能销售陪练 Skill。加载后由宿主大模型扮演客户与教练；本地 Python 只负责菜单、语音播放、规则、进度、日志、周报和离线验证，不是独立聊天软件。

## 主要能力

- 复古 DOS/MUD 字符启动界面，先选 DLC、再选关卡，选关后直接开始。
- 文字与麦克风输入随时切换，保持同一客户和证据状态。
- 每轮客户回应后提供教练分析、改良建议、参考表达和进度。
- 简单、正常、困难三档难度；最多 20 个有效回合。
- 双轴评分：八维销售能力 0–24 与客户结果独立记录。
- 本地日志与领导可读 HTML/CSV 周报。
- 145 条 v0.3 客户语音、固定系统语音、5 个 MIDI/WAV 提示音离线可用。

## 关卡

- DLC01 制造业
  - L01 第一次正式面谈
  - L02 三人方案会
- DLC02 商学院
  - L01 潜在学员需求诊断：15 项证据、八维客户画像还原、多种通关与未通关结局。
  - L02 报名政策与价格谈判：价格、退款、奖学金、助学金、特殊条件与权限边界。

## 安装

将完整 `sales-roleplay-solo/` 文件夹复制到 Agent 的 Skill 目录，然后重启或重新索引 Agent：

- Codex：`%USERPROFILE%\.codex\skills\sales-roleplay-solo`
- Reasonix：`.reasonix\skills\sales-roleplay-solo`
- OpenClaw/ArkClaw：`~/.openclaw/workspace/skills/sales-roleplay-solo`

通过 Git 安装当前 GitHub 主分支：

```powershell
git clone https://github.com/Atange2023/sales-roleplay-solo.git "$env:USERPROFILE\.codex\skills\sales-roleplay-solo"
```

安装后直接在 Agent 对话中说“启动销售陪练”。不要用 `py scripts/roleplay.py --offline` 开始练习；该脚本只做离线自检。

## 更新与自检

在 Agent 中说 `sales-roleplay update`，Agent 会调用随包更新器并保留 `data/`、`reports/` 和进度。详情见 `references/updating.md`。

```powershell
py scripts/roleplay.py --smoke --offline --no-audio
py -m unittest discover -s tests -p "test_*.py"
```

## 版权

方法框架参考《销售就是会提问》（青木毅，天津人民出版社 2021）；剧本、规则、脚本与资产为本仓库内容，代码采用 MIT License。
