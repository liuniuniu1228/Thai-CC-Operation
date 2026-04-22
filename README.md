### 1. README.md
**用途**：面向人类开发者或你自己，记录如何配置环境、安全事项及运行脚本。

```markdown
# CRM Performance Tracker 🚀

本项目包含一套用于自动化登录 CRM 系统并提取业绩数据的工具。

## 📁 目录结构
- `main/crm_tool.py`: 核心 Python 脚本，处理登录、抓取与数据解析。
- `requirements.txt`: 项目依赖库。

## 🛠️ 环境配置
1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```
2. **设置环境变量** (推荐):
   为了安全，建议不要在脚本中明文存储密码。
   - `export CRM_PWD="你的密码"`

## 🚀 快速运行
```bash
python main/crm_tool.py
```

## 📊 输出说明
脚本将输出结构化的 JSON 数据，包含以下字段：
- `序号`: 实时业绩排名
- `姓名`: 员工姓名
- `业绩`: 当前完成业绩数值
- `小组`: 所属团队名称

## ⚠️ 安全警示
- **凭证安全**: 请勿将包含明文密码的代码提交至公开仓库。
- **SSL 警告**: 脚本目前配置为跳过 SSL 校验 (`verify=False`)，仅限内部网络使用。
```

---

### 2. skill.md
**用途**：直接喂给 AI Agent（如 GPTs, Claude, AutoGPT），作为它的“技能书”。

```markdown
# Skill: CRM 业绩数据实时查询 (CRM_Performance_Query)

## 1. 核心能力定义
通过运行 `main/crm_tool.py` 模拟管理员登录 CRM 系统，抓取 `type=2` 页面的实时业绩排行榜。能够将非结构化的网页表格转化为结构化 JSON 数据，支持对话式的数据检索与分析。

## 2. 账号与权限信息
- **账号**: `THCC-Panawat`
- **目标地址**: `https://crm.51talk.com/Performance/getSsPreformanceList?type=2`
- **执行路径**: `main/crm_tool.py`

## 3. Agent 运行逻辑 (Step-by-Step)
1. **环境初始化**: 确保安装了 `pandas`, `requests`, `beautifulsoup4`。
2. **触发条件**: 当用户询问“XX的业绩”、“现在的排名”、“前三名是谁”等问题时。
3. **执行脚本**: 运行 `python main/crm_tool.py` 获取最新的 JSON 数据。
4. **数据处理**: 
   - 搜索 `姓名` 匹配用户查询的目标。
   - 提取 `序号` 作为排名反馈。
   - 如果用户没有指定姓名，默认展示前 5 名。

## 4. 对话回复规范
- **禁止输出**: 不要输出 MD5 哈希值、登录过程日志或原始 HTML 源码。
- **推荐输出**: 以自然的语气回复。
  - *例子*: "查询到 Panawat 目前排名第 3，业绩为 15,200，属于泰国销售一组。"
- **异常处理**: 如果脚本返回登录失败，请提示用户检查 CRM 密码或 VPN 状态。

## 5. 数据字段映射
| 原始字段 | Agent 识别名 | 备注 |
| :--- | :--- | :--- |
| 序号 | 排名 | 数字越小排名越高 |
| 姓名 | 员工名 | 支持模糊匹配 |
| 业绩 | 销售额/课时 | 核心数值 |
| 小组 | 团队 | 用于归类分析 |
```
