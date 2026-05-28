# RiskOps Copilot · 5 分钟 Demo 脚本

> 目标：5 分钟内跑一遍「数据底座 → 异常 → 归因 → 策略 ROI → 报告导出」闭环。
> 前置：本机已执行 `bash scripts/run_all.sh`，`outputs/` 目录完整。

---

## ① 开场 · 30s

- **演示动作**：终端启动 TUI。
- **命令**：`python -m riskops.tui`
- **屏幕重点**：聊天面板亮起，底栏显示 `agent · model · /help 帮助`。
- **台词**：「RiskOps Copilot 是一个本地化贷后策略分析工作台——合成数据、本地 LLM、命令行、零云依赖。5 分钟跑完核心能力。」

## ② 数据底座 · 60s

- **演示动作**：先看已加载的数据摘要，再看经营总览。
- **命令**：`/context` → `/summary`
- **屏幕重点**：`/summary` 来自 `outputs/m3/m3_summary.md`，含 15 个核心指标卡片。
- **台词**：「五层数据底座 DIM / ODS / DWD / DWS / ADS，43 张表、26 个指标全部合成；隐私分级 P0–P4，明文 PII 永不出库。」

## ③ 异常 + 归因 · 90s

- **演示动作**：先看异常清单，再追主因。
- **命令**：`/anomaly` → `/drivers`
- **屏幕重点**：
  - `/anomaly` 来自 `outputs/anomalies/anomaly_results.md`——**7 条 anomaly**，主线是 M1 D7 回收率 18.6% → 15.2%。
  - `/drivers` 来自 `outputs/attribution/attribution_summary.md`——主因 Top3 + 贡献度。
- **台词**：「7 个埋点异常覆盖结果 / 过程 / 合规 / ROI 四类。M1 D7 为什么掉 3.4pct？归因引擎给的答案：高余额客群结构变化 + 华东产能不足 + 供应商 B 接通率下降——主次因 + 贡献度一目了然。」

## ④ 策略 ROI + 话术 · 60s

- **演示动作**：看 ROI 沙盘，再看话术草稿。
- **命令**：`/roi` → `/script`
- **屏幕重点**：
  - `/roi` 来自 `outputs/model_lab/roi_summary.md`，含减免 / 外呼 / 分案三类策略 ROI。
  - `/script` 来自 `outputs/script/script_summary.md`，含合规过审话术 + Mock 审批留痕。
- **台词**：「策略不是凭感觉调，每条都附 ROI 测算；话术不是凭运气写，11 维合规评分 + 关键词兜底，违禁词直接拦截。」

## ⑤ 报告导出 · 60s

- **演示动作**：触发周报全量导出。
- **命令**：`/report`
- **屏幕重点**：完成后列出 `outputs/reports/` 产物——HTML / Markdown / 飞书友好 MD (`weekly_report.feishu.md`) / Excel（6 sheet 含透视） / PPT（9 页含讲稿） / Word 草稿，配合 `outputs/visualization/` 的 11 张 Plotly 图。
- **台词**：「一条命令、6 种格式，周一直接发飞书。咨询级图表 + 讲稿备注，演示和写报告不用分两套工。Demo 完。」

---

> 备用命令：`/qc`（质检结果）、`/vendor`（供应商绩效快查）、`/briefing`（即时经营简报）、`/help`（13 条命令完整列表）。
