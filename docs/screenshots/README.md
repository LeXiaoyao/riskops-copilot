# Screenshots

本目录用于存放 README 视觉导览所需的截图。

> 公开 demo 边界：synthetic data only / 不接真实客户数据 / 不做真实风控决策。截图只用于展示当前 demo 输出，不代表生产系统。

---

## Recommended Screenshots

下面是建议补充的 4 张截图。每一张都给出：用途、来源命令或文件、推荐文件名、人工截图要点。

当前仓库尚未提交真实 PNG（避免引入大文件 / 平台特定渲染差异），下列文件名是约定占位。补图后保持文件名不变，README 入口无需改动。

### 1. `cli-summary.png` — CLI summary

- **用途**：展示项目当前阶段、异常数量、数据边界。
- **生成命令**：
  ```bash
  python scripts/riskops_cli.py summary
  ```
- **截图要点**：
  - 至少完整露出顶部 4 行（"当前阶段：M6/M7 ... model lab + state recovery feasibility guard"，"当前 demo 数据边界：synthetic data ..."，"anomaly 总数"，"attribution target metric"）。
  - 终端字体清晰；窗口宽度 80–100 列即可。
  - 不要遮挡 "synthetic data" 与 "D7 回收率（recovery_rate_d7）" 这两行——它们是 demo 边界的关键证据。

### 2. `model-lab-cli.png` — Model Lab overview

- **用途**：展示 M6 Model Lab + demo boundary。
- **生成命令**：
  ```bash
  python scripts/riskops_cli.py model-lab
  ```
- **截图要点**：
  - 必须包含 "scenario count：5" / "target metric：recovery_rate_d7" / "top recommended scenario" 三行。
  - 必须包含底部 "demo boundary" 块（synthetic data only / no real customer data / no real collection action / no SMS / no LLM decisioning）。
  - 不要单独截 "top recommended scenario" 而省略 demo boundary——避免给访客留下 "production decisioning" 印象。

### 3. `dashboard-preview.png` — Static Dashboard

- **用途**：展示本地静态 Dashboard。
- **来源文件**：`outputs/dashboard/dashboard.html`
- **生成方式**：
  ```bash
  # 如果 outputs/dashboard/dashboard.html 已存在，可直接用浏览器打开：
  open outputs/dashboard/dashboard.html
  # 若需要重新渲染（会覆盖 outputs/dashboard/dashboard.html）：
  python scripts/riskops_cli.py render-dashboard
  ```
- **截图要点**：
  - 截取首屏即可，目标是让访客一眼看到 dashboard 风格，而不是替代完整 HTML。
  - 浏览器宽度建议 1280–1440px；过宽会让图过大。
  - 单张控制在 1 MB 以内（PNG 8-bit 或 WebP 优先）。

### 4. `model-lab-summary.png` — Strategy / ROI summary（可选）

- **用途**：展示 M6 strategy evaluation / ROI 摘要的可读性。
- **来源文件**：
  - `outputs/model_lab/strategy_eval_summary.md`
  - `outputs/model_lab/roi_summary.md`
- **生成方式**：用任意 Markdown 预览器（VS Code、Typora、GitHub blob 页）打开后截图首屏。
- **截图要点**：
  - 截取 baseline / scenario / delta 表头一段即可。
  - 必须包含明示 "demo cost assumptions" 或 "synthetic" 字样的段落，避免被误读为真实财务结果。

---

## Architecture diagram

`docs/architecture.md` 内已用 Mermaid 描述层级关系。**GitHub 会在 Markdown 页面上原生渲染 Mermaid**，所以无需再额外截图或导出 PNG。如未来需要导出静态图，建议命名 `architecture-overview.png`，分辨率 ≤ 1600px 宽。

---

## What NOT to screenshot

为保持公开 demo 可信度，以下内容**不要**截图、不要展示：

- `synthetic_data/raw_secure/` 下的任何原始合成数据（即便是合成的，也保留与生产同样的处理纪律）。
- `outputs/model_lab/ml_baseline/` 下的 feature_importance 完整列表——可以引用，但不要把 38+ 字段全部截图作为"模型完整能力"展示，避免暗示 production model。
- 任何包含 "production"、"real customer"、"cure baseline ready" 字样的拼贴图。

---

## Update workflow

1. 在本地跑 smoke 命令（`summary` / `model-lab` 等）并截图。
2. 把图片放到 `docs/screenshots/<name>.png`，文件名与本文件 §Recommended Screenshots 中一致。
3. 如新增图片在 README 中需要直接展示，再回到 [README.md](../../README.md) / [README.en.md](../../README.en.md) 的 Preview 入口里追加引用；否则保留入口指向本文件即可。
4. 单图 ≤ 1 MB；总目录大小不要超过 5 MB（公开仓库克隆速度优先）。
5. 不要把 `outputs/` 下的渲染产物直接复制到 `docs/screenshots/`——截图是给访客的导览图，不是产物镜像。

---

## See Also

- [README.md](../../README.md)
- [README.en.md](../../README.en.md)
- [docs/architecture.md](../architecture.md)
