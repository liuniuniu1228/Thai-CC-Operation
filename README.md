# CRM Performance & Call Analytics Tracker 🚀 (v2.0)

本项目是一套用于自动化提取 CRM 系统数据的工具库，支持实时监控员工的**业绩排名**及**通话行为效率**，并支持自定义日期范围筛选。

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
脚本采用参数化运行，格式为：
`python main/crm_tool.py [模式] [姓名] [开始日期] [结束日期]`

### A. 业绩查询 (Performance)
*注：业绩查询暂仅支持实时数据。*
- **查看前 5 名**: `python main/crm_tool.py perf`
- **查询特定员工业绩**: `python main/crm_tool.py perf Panawat`

### B. 通话效率查询 (Call Stats)
支持通过日期范围分析员工的努力程度。**日期格式：YYYY-MM-DD**。

- **今日全员统计**: `python main/crm_tool.py call`
- **今日个人统计**: `python main/crm_tool.py call Panawat`
- **特定日期个人统计**: 
  `python main/crm_tool.py call Panawat 2026-04-20 2026-04-20`
- **特定日期范围统计 (如本月至今)**: 
  `python main/crm_tool.py call Panawat 2026-04-01 2026-04-24`
- **特定日期范围全员统计**: 
  `python main/crm_tool.py call None 2026-04-01 2026-04-07`

## 📊 字段解析
- **业绩数据**: 排名、姓名、小组、业绩总额。
- **通话数据**: 
  - **CC**: 员工姓名。
  - **总时长 (Total duration)**: 累计通话分钟数。
  - **总次数 (Total calls)**: 拨号总次数。
  - **有效率 (Eff. rate)**: 接通且符合标准通话的占比。

## ⚠️ 注意事项
- **日期规范**: 必须使用 `YYYY-MM-DD` 格式（例如 `2026-04-24`），否则 CRM 系统可能无法识别。
- **VPN**: 访问 `crm.51talk.com` 需确保处于公司内网或已开启 VPN。
- **性能**: 查询长跨度日期（如超过 30 天）时，由于 CRM 页面渲染较慢，脚本返回可能存在延迟。
