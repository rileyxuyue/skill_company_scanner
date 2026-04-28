---
name: company-scanner
description: "公司深度扫描报告生成器。当用户输入一个公司名称并要求生成扫描报告、深度分析、公司调研时，使用此skill。自动完成信息搜集、HTML报告生成（含精美视觉设计）、以及每个模块的截图输出（桌面版+手机版两套）。"
---

# 公司深度扫描报告生成器

## 概述

此skill用于当用户提供一个公司名称时，自动完成以下全流程：
1. 搜集该公司的公开信息（商业模式、融资、团队、竞争格局等）
2. 生成一份精美的单页HTML深度分析报告
3. 对报告的每个模块进行截图，输出桌面版和手机版两套图片

## 触发条件

当用户输入一个公司名称并期望获得扫描报告、深度分析、公司调研时触发。常见表达：
- "帮我扫描一下 XX 公司"
- "生成 XX 的深度报告"
- "分析一下 XX 这家公司"
- 直接输入公司名称

## 工作流程

### Phase 1: 信息搜集

使用 web_search 搜集目标公司的以下信息维度，每个维度至少搜索2-3次确保信息充分：

| 维度 | 搜索关键词示例 | 必须搜集的数据点 |
|------|------------|--------------|
| 基本信息 | "XX公司 简介 融资" | 全称、城市、行业、员工数、估值 |
| 商业模式 | "XX公司 做什么 客户 商业模式" | 核心产品、目标客户、盈利模式、竞争优势 |
| 竞争格局 | "XX公司 竞争对手 行业格局" | 主要竞品（至少5家）、各自优劣势 |
| 融资历程 | "XX公司 融资 投资方 估值" | 每轮融资时间、轮次、领投方、金额 |
| 管理团队 | "XX公司 创始人 CEO CTO 背景" | 核心创始人姓名、教育背景、职业经历、学术贡献 |
| 财务状况 | "XX公司 营收 盈利 财务" | 收入规模、盈利状态、烧钱速度 |
| 招聘信息 | "XX公司 招聘 岗位 薪资 BOSS直聘" | 在招岗位类别、代表岗位、薪资范围 |
| 公司文化 | "XX公司 工作体验 加班 文化" | 管理风格、工作强度、员工评价 |

### Phase 2: 生成 HTML 报告

参考 `references/template-report.html` 的完整结构和视觉设计，生成报告。

#### 报告结构（12个Section）

每个section使用 `<div class="sec"><div class="ac ac-{type}">` 包裹，type根据内容判断：
- `ac-g`（绿色/优势）：该维度对公司有利
- `ac-r`（红色/劣势）：该维度对公司不利
- `ac-n`（蓝色/中性）：综合评估或信息展示

| # | Section | 类型判断 | 内容要求 |
|---|---------|---------|---------|
| 0 | 综合评估摘要 | ac-n | 10维度评分表 + 综合建议（值得入职？财务自由？风险？） |
| 1 | 商业理解 | 按内容判断 | 一句话解释 + 解决什么问题 + 谁付钱 + 为什么选它 |
| 2 | 竞争格局 | 按内容判断 | 竞品对比表（至少5家）+ 优势/劣势对比框 |
| 3 | 上限分析 | 按内容判断 | 市场规模 + 有利/不利趋势 + 天花板估算 |
| 4 | 下限分析 | 按内容判断 | 核心风险清单（至少5条）+ 最坏情况 |
| 5 | 收入分解 | 按内容判断 | 收入来源表格 + 关键问题分析 |
| 6 | 财务质量 | 按内容判断 | 行业对照 + 资金储备/烧钱速度/跑道分析 |
| 7 | 管理团队 | 按内容判断 | 每位核心创始人独立卡片（教育标签+学术贡献区块） |
| 8 | 投资方和估值 | 按内容判断 | 融资时间轴 + 投资方高亮列表 + IPO分析 |
| 9 | 公司规模 | 按内容判断 | 3格统计面板 + 扩张/技术密度/办公布局 |
| 10 | 氛围文化 | 按内容判断 | 积极面 vs 需留意（双列对比卡片） |
| 11 | 在招岗位 | ac-n | 5类岗位网格（每类最多3个代表岗位）+ 福利标签 |

#### 视觉设计规范

严格遵循以下设计要素，全部内联在 `<style>` 中（不依赖外部CSS）：

**1. Hero 标题区域**
- 使用城市夜景背景图 `hero-bg.png`（⚠️ 必须在生成HTML后执行 Phase 3.5 的复制命令，将 skill `assets/hero-bg.png` 复制到报告输出目录）
- 65%透明度深色遮罩 + 3px 背景模糊
- 扫描光条动画（`@keyframes scan`，5秒周期从上到下）
- 网格线背景（48px间距，3.5%透明度）
- 左上/右下角装饰线
- 标签："🌕 一颗月球表面扫描报告"（**纯白色字体 `#fff`**）
- 4个统计卡片（估值/融资轮次/公司规模/技术占比等）
- 副标题包含公司核心亮点概述

**2. 卡片设计**
- 白色背景 + 22px圆角 + 精致阴影
- 左边框彩色条（绿/红/蓝区分优劣势）
- 编号方块带渐变色 + hover旋转动效
- 底部半月暗纹装饰（760px暖黄色径向渐变月球）
- 环形山纹理（多层椭圆径向渐变）

**3. 融资时间轴**
- 左侧竖线 + 圆点标记
- 明星投资方用金色圆点 + 黄色底色卡片
- 投资方名称用黄色渐变标签高亮

**4. 管理团队卡片**
- 每人独立卡片，左侧彩色边框
- 教育背景用醒目渐变标签（🎓 XX大学 · XX博士）
- 博士级别增加"📚 学术贡献与地位"独立区块

**5. 水印**
- SVG pattern 全页斜25°重复
- 文字："@一颗月球表面"
- 透明度 8%

**6. Footer**
- 深色渐变背景
- 月相SVG装饰（9个月相等间距）
- 生成日期

**7. 响应式**
- 768px断点适配

#### CSS变量体系

```css
:root {
  --bg: #F4F5FA;
  --w: #FFF;
  --d: #111827;
  --m: #6B7280;
  --g: #059669;    /* 绿色/优势 */
  --r: #DC2626;    /* 红色/劣势 */
  --b: #4F46E5;    /* 蓝色/中性 */
  --rd: 22px;      /* 圆角 */
  --f: 'Inter','PingFang SC',-apple-system,sans-serif;
}
```

#### 字号规范（确保桌面版截图清晰可读）

| 元素 | 字号 | 说明 |
|------|------|------|
| body 基础字号 | 15px | 全局基础 |
| 正文 `.tx` | 15px | 卡片内正文 |
| 卡片标题 `.ct` | 22px | Section 标题 |
| 卡片副标题 `.cs` | 13px | Section 英文副标题 |
| 表格内容 `.st` `.ct2` | 14px | 表格单元格 |
| 表头 `.st th` `.ct2 th` | 12px | 大写字母表头 |
| 高亮盒子标题 `.hxt` | 15px | 绿/红/蓝盒子标题 |
| 高亮盒子列表 `.hx ul` | 14px | 盒子内列表项 |
| 建议框正文 `.abtx` | 15px | 黄色建议框 |
| 判定徽章 `.vd` | 13px | 优势/劣势标签 |
| Hero 副标题 `.hs` | 16px | 公司简介 |
| Hero 标题 `h1` | 46px | 公司名称 |

### Phase 3: 输出两个版本的 HTML

每次生成报告需要产出**两个 HTML 文件**：

#### 3a. Desktop 版（详实版）
- 文件名：`{company}-deep-dive.html`
- 使用 `references/template-report.html` 的桌面版 CSS
- **信息密度高**：表格完整、列表详尽、分析段落详细、竞品对比完整
- max-width 920px，适合桌面浏览器阅读
- **不截图**，改为导出 PDF（使用 Playwright `page.pdf()`）

#### 3b. Mobile 版（精简版）
- 文件名：`{company}-mobile.html`
- 使用移动端优先 CSS（参考 `references/template-report.html` 中移动端部分）
- **信息密度低**：表格改为卡片列表（`.m-list > .m-item`）、文案更精炼、列表项更少
- `max-width: 420px; margin: 0 auto` — 大屏幕也以手机宽度居中（微信公众号风格）
- `body` 背景 `#E8E8ED`，`.page-wrap` 白色带阴影
- 用 `.page-wrap` div 包裹全部内容（水印、hero、sections、footer）
- **需要截图**

#### Mobile 版与 Desktop 版的信息密度差异

| 元素 | Desktop（详实） | Mobile（精简） |
|------|----------------|---------------|
| 综合评估 | 3列表格（维度/评估/判断） | 卡片列表（`.m-list`），每张卡片一个维度 |
| 竞品对比 | 5列表格（企业/估值/路线/出货量/优势） | 卡片列表，每张一行公司+简短描述 |
| 收入来源 | 4列表格 | 卡片列表，每张一个来源+占比 |
| 正文段落 | 完整分析（3-4段，每段3-5行） | 精炼（2-3段，每段1-3行） |
| 高亮盒子列表 | 4-6条 | 3-4条 |
| 管理团队 | 完整学术贡献区块 + 详细经历 | 精简学术贡献 + 1句经历 |
| 岗位 | 5类×3个 | 3类×2个 |
| 福利 | 7个标签 | 5个标签 |

### ⚠️ Phase 3.5: 复制 Hero 背景图（必须执行！）

**HTML 生成后、截图/PDF 之前，必须先将背景图复制到报告目录，否则 Hero 区域将无法显示背景图！**

```bash
cp {skill_base_dir}/assets/hero-bg.png {report_output_dir}/hero-bg.png
```

其中：
- `{skill_base_dir}` 是本 skill 的安装目录（包含 `SKILL.md` 的目录）
- `{report_output_dir}` 是报告 HTML 所在目录（即 `post/reports/{company-slug}/`）

**验证**：确认报告目录下存在 `hero-bg.png` 文件后，再继续后续步骤。

### Phase 4: Mobile 截图

运行移动端截图脚本：

```bash
python3 {skill_base_dir}/scripts/screenshot_mobile.py <mobile_html_path> <output_dir>
```

脚本依赖：`playwright`、`Pillow`（PIL）。若未安装：
```bash
pip3 install playwright Pillow
python3 -m playwright install chromium
```

输出：
```
output_dir/
├── 00_hero.png
├── 00_hero_animated.gif   # 扫描光条动画 GIF
├── 01_summary.png
├── 02_business.png
├── ...
└── 13_footer.png
```

### Phase 5: Desktop PDF

Desktop HTML 生成后，使用 Playwright 导出 PDF：

```python
async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    await page.goto(f"file://{html_path}", wait_until="networkidle")
    await page.wait_for_timeout(2000)
    await page.pdf(path=output_pdf_path, format="A4", print_background=True, margin={"top":"10mm","bottom":"10mm","left":"8mm","right":"8mm"})
    await browser.close()
```

### Phase 6: 交付

1. 使用 `preview_url` 预览 Mobile HTML
2. 使用 `open_result_view` 展示截图文件夹中的代表截图
3. 所有文件存放在 `post/reports/{company-slug}/` 目录下
4. 告知用户文件位置和使用建议

最终交付物清单：
```
post/reports/{company-slug}/
├── hero-bg.png                    # Hero背景图
├── {company}-deep-dive.html       # 桌面详实版 HTML
├── {company}-deep-dive.pdf        # 桌面详实版 PDF
├── {company}-mobile.html          # 移动精简版 HTML
└── screenshots/                   # 移动版截图
    ├── 00_hero.png
    ├── 00_hero_animated.gif
    ├── 01_summary.png ~ 13_footer.png
    └── ...
```

## 重要注意事项

- 每次生成**两个 HTML**：desktop 详实版 + mobile 精简版
- Desktop 版不截图，导出 **PDF**
- Mobile 版需截图，使用 `scripts/screenshot_mobile.py`
- 所有 CSS 必须内联（不依赖外部CSS）
- 字体使用 Google Fonts Inter（CDN加载）
- Hero 背景图 `hero-bg.png` 从 skill assets 复制到报告目录
- Mobile 版必须加 `.page-wrap`（max-width:420px, margin:0 auto）确保大屏幕也是手机宽度
- Mobile 版表格用 `.m-list > .m-item` 卡片列表替代，不要用 `<table>`
- 信息搜集要充分，每个维度搜 2-3 次
- 不放投递渠道
- 报告语言为中文
- 截图脚本需要 playwright 和 Pillow
- 所有产出文件存放在 `post/reports/{company-slug}/` 目录下，不放桌面
