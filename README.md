
### 1. README.md (更新版)
**重点：** 增加了多模式运行指令的说明。

```markdown
# CRM Performance & Call Analytics Tracker 🚀

本项目是一套用于自动化提取 CRM 系统数据的工具库，支持实时监控员工的**业绩排名**及**通话行为效率**。

## 📁 目录结构
- `main/crm_tool.py`: 核心脚本，支持 `perf` (业绩) 和 `call` (通话) 两种抓取模式。
- `requirements.txt`: 包含 `requests`, `beautifulsoup4`, `lxml` 等必要依赖。

## 🛠️ 环境配置
1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```
2. **凭证管理**:
   - 脚本默认使用内置凭证，建议通过环境变量增强安全性：
   - `export CRM_PWD="你的密码"`

## 🚀 运行指令
脚本采用参数化运行，格式为：`python main/crm_tool.py [模式] [姓名]`

### A. 业绩查询 (Performance)
- **查看前 5 名**: `python main/crm_tool.py perf`
- **查询特定员工业绩**: `python main/crm_tool.py perf Panawat`

### B. 通话效率查询 (Call Stats)
- **查看今日全部通话统计**: `python main/crm_tool.py call`
- **查询特定员工通话详情**: `python main/crm_tool.py call Panawat`

## 📊 字段解析
- **业绩数据**: 排名、姓名、小组、业绩总额。
- **通话数据**: CC 姓名、通话总时长 (0-24h)、首次通话时间 (First call)、总通话次数。

## ⚠️ 注意事项
- **VPN**: 访问 `crm.51talk.com` 需确保处于公司内网或已开启 VPN。
- **字段变更**: 若 CRM 网页改版导致数据错位，需调整脚本中的 `cells` 索引。
```

---

### 2. skill.md (更新版)
**重点：** 赋予 Agent 关联分析的能力。

```markdown
# Skill: CRM 综合运营数据助手 (Performance & Call Analysis)

## 1. 核心能力定义
通过执行 `main/crm_tool.py` 脚本，Agent 可实时获取 CRM 系统的两类核心数据：
1. **业绩表现**: 员工的实时排名与销售额。
2. **行为效率**: 员工的拨号频次、通话时长及开启工作的时间（First Call）。

## 2. 技能指令集 (CLI Reference)
| 查询目标 | 执行指令 | 参数说明 |
| :--- | :--- | :--- |
| 全局业绩/排名 | `python main/crm_tool.py perf` | 默认返回 Top 5 |
| 个人业绩查询 | `python main/crm_tool.py perf [姓名]` | 模糊匹配姓名 |
| 全局通话统计 | `python main/crm_tool.py call` | 获取当日全员通话行为 |
| 个人通话查询 | `python main/crm_tool.py call [姓名]` | 查看特定 CC 的努力程度 |

## 3. Agent 分析逻辑 (Pro-Active Insights)
当用户提出需求时，Agent 应具备以下分析思路：
- **查考勤/状态**: 检查 `call` 模式下的 `首次通话 (First call)`。如果时间较晚，暗示员工进入状态慢。
- **查工作量**: 检查 `通话总时长` 和 `通话次数`。
- **综合评估**: 关联业绩与通话数据。
  - *分析模型*: 如果“通话时长极高”但“业绩排名靠后”，可能存在无效沟通，建议关注其通话质量。

## 4. 对话回复规范
- **简洁直观**: 优先展示关键数据点，避免大段 JSON 输出。
- **语气建议**: 针对运营管理场景，回复应准确且具有洞察力。
  - *示例*: "Panawat 今天的表现很好，首通电话在 09:02 拨出，目前通话时长 180 分钟，业绩排在全组第 3 名。"

## 5. 数据源映射
- **业绩地址**: `/Performance/getSsPreformanceList?type=2`
- **通话地址**: `/admin/user/cc_call_info_new.php`
```
