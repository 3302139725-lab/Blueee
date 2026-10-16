---
name: jev
description: Use when a task needs a fast, typed DECISION instead of free-form generation — classification, routing, scoring, or yes/no gating. Trigger keywords include Jev, 判别, 判断, 分类, 归类, 路由, 打分, 评分, 是否, 概率, 置信度. The LLM generates/reasons (brain); Jev decides (fast, structured, low-hallucination). Do NOT use for writing/chat/coding — that is the LLM's job.
---

# Jev — 快速类型化判断（System One 模型）

Jev 是 TypeSafe AI 的 System One 模型：**不做聊天/生成**，只对一段「状态」做结构化判断。

三类输出：
- `choice`：从固定选项里选一个（分类 / 路由）
- `score`：按标准打分（有序数值）
- `noul`：某个命题为真的**校准概率**（0~1，用于是/否闸门）

**分工**：需要**生成/推理/写作/写代码** → LLM（我自己）；需要**快速、可靠、带置信度的判断** → Jev。

## 何时用
- 对一段文本/JSON 做**分类、路由、意图识别**
- 给内容**打分/排优先级**（如紧急度、风险、质量）
- 需要**是/否 + 概率**来做分支（如"要不要升级/拦截/继续"）
- 需要**快**（几十~几百毫秒）且**尽量不幻觉**的判断

## 前置：配置 API Key
按顺序任一即可：
1. 环境变量 `JEVMODEL_API_KEY`
2. 文件 `%USERPROFILE%\.config\opencode\jev_api_key.txt`（只放 key 一行）

> 获取 key：登录 https://jevmodel.org → Dashboard → 新建 key。

## ⚠️ 地区限制（重要）
Jev API 在大陆返回 **HTTP 451「TypeSafe is not available in your region」**。
必须先挂代理再调用。脚本支持代理，按顺序读取：
- 环境变量 `JEVMODEL_PROXY`（如 `http://127.0.0.1:7897`）
- 或 `HTTPS_PROXY` / `HTTP_PROXY`

即调用前先启动代理（如 Clash Verge），并设置：
```powershell
$env:JEVMODEL_PROXY="http://127.0.0.1:<你的代理端口>"
```
否则会 451 失败。

## 各类型 criteria 格式（关键）
- `choice`：`criteria` 是**对象** `{值:说明}`
- `score`：`criteria` 是**有序数组** `[低, ..., 高]`（2~10 个等级，从低到高）
- `noul`：无需 criteria，只要 `instructions`

## 如何调用
1. 写一个请求 JSON 文件（建议放临时目录，如 `%TEMP%\jev_req.json`）：
```json
{
  "state": "被判断的内容（文本或 JSON 字符串）",
  "questions": {
    "category": {
      "type": "choice",
      "instructions": "这条工单属于哪类？",
      "criteria": {"billing": "费用/退款问题", "technical": "产品故障", "other": "其它"}
    },
    "urgency": {
      "type": "score",
      "instructions": "紧急程度如何？",
      "criteria": ["完全不急", "不太急", "比较急", "非常急"]
    },
    "escalate": {
      "type": "noul",
      "instructions": "需要立即升级给人工吗？"
    }
  }
}
```
2. 运行脚本（用技能目录下的 `jev.py`）：
```powershell
python "<项目根>\.opencode\skills\jev\jev.py" "%TEMP%\jev_req.json"
```
脚本会打印 Jev 返回的**结构化 JSON**（含概率与置信度）。

## 规则
- 每个问题要**原子、具体**——不要问「评价这段」这种大问题，拆成多个小问题（Jev 会并行、独立评估，加问题几乎不加时间）
- 一次 1~8 个问题
- **一定要设置信度阈值**：低于阈值的判断别硬信，可以退回给我（LLM）或走人工
- 命名用**代码要分支的字段名**（如 `route`、`is_spam`），别用模糊主题词
- Jev 只给"判断"；**解释、文案、后续生成**由我来做

## 典型组合用法
1. 我用 LLM 把用户的模糊需求**拆成结构化问题**
2. 调 Jev 拿到**带置信度的类型化判断**
3. 我根据阈值**分支**，需要时再生成文本/代码
4. 低置信度的结果，我兜底或提示你复核
