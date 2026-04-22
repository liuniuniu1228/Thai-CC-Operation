# Skill: CRM 业绩对话式查询助手

## 1. 技能描述
此技能允许 Agent 登录 CRM 系统，抓取并解析 `type=2` 的业绩列表，并将数据转化为结构化 JSON。Agent 接收到数据后，可以针对“姓名”、“排名”、“业绩”等关键词与用户进行自然语言交互。

## 2. 核心指令 (Agent Action)
当用户询问业绩相关问题时，Agent 应执行以下步骤：
1. **认证**: 执行登录并获取 Session。
2. **抓取**: 访问业绩页面。
3. **解析**: 将 HTML 转换为结构化文本/JSON。
4. **回答**: 根据 JSON 内容回答用户的具体问题。

---

## 3. 执行脚本 (Shell + Python 混合版)
此脚本执行后会直接在控制台（stdout）输出 JSON，方便 Agent 直接读取进入内存。

```bash
#!/bin/bash
# 1. 环境准备
CRM_USER="THCC-Panawat"
CRM_PWD_MD5="7297a2d7765265fb64d7cd46efa2f77d"
COOKIE_FILE="/tmp/crm_cookie.txt"

# 2. 登录流程
curl -s -c $COOKIE_FILE -b $COOKIE_FILE -k -X POST \
  "https://crm.51talk.com/admin/login.php" \
  -d "user_name=$CRM_USER&password=$CRM_PWD_MD5&user_type=admin&login_employee_type=sideline&Submit=%E7%99%BB%E5%BD%95" -L > /dev/null

# 3. 抓取数据并使用 Python 实时解析成 JSON 输出
curl -s -b $COOKIE_FILE -k "https://crm.51talk.com/Performance/getSsPreformanceList?type=2" | python3 - <<EOF
import pandas as pd
import sys
import json

try:
    # 自动识别页面中的表格
    dfs = pd.read_html(sys.stdin.read())
    # 假设业绩在第一个表格，提取关键列
    df = dfs[0][['序号', '姓名', '业绩', '小组']]
    # 转换为字典格式输出，方便 Agent 识别
    print(json.dumps(df.to_dict(orient='records'), ensure_ascii=False))
except Exception as e:
    print(json.dumps({"error": str(e)}))
EOF
```

---

## 4. Agent 对话逻辑配置 (Prompting Guide)

为了让 Agent 能够自然对话，请在 Agent 的 **System Instructions** 中加入以下逻辑：

> **数据处理规范：**
> * 当你通过该 Skill 获取到数据后，你会得到一个包含多个对象的列表，例如：`[{"序号": 1, "姓名": "张三", "业绩": 5000, "小组": "A组"}, ...]`。
> * **排名查询**: “序号”即为该员工的实时排名。
> * **逻辑推理**: 
>   * 如果用户问“谁是第一名？”，请查找 `序号 == 1` 的姓名。
>   * 如果用户问“XX 的业绩怎么样？”，请根据姓名匹配对应的业绩和小组。
>   * 如果用户问“我们组谁最厉害？”，请先筛选“小组”，再对比“业绩”。
>
> **回复风格示例：**
> * *用户*：“查询一下 Panawat 的排名。”
> * *Agent*：“好的，为您查询到 Panawat 目前在 `type=2` 类别中排名第 **5**，当前业绩为 **12,800**，所属小组为 **Thai-Sales-01**。”

---

## 5. 交互示例

**场景 A：查具体人**
* **User**: "帮我看看王小明的业绩。"
* **Agent**: (运行 Skill -> 检索数据) "王小明目前的业绩是 8,500，排名第 12 位，属于飞虎队小组。"

**场景 B：查前三名**
* **User**: "现在排名前三的都是谁？"
* **Agent**: (运行 Skill -> 排序) "目前的前三名分别是：1. 李华（业绩 20,000）、2. 陈静（业绩 18,500）、3. 周强（业绩 17,000）。"

---

### 💡 开发建议
* **实时性**: 因为业绩是动态的，建议 Agent 每次处理此类问题时都静默运行一次抓取脚本，确保数据是最新的。
* **容错**: 如果 `type=2` 页面字段名有微调（比如“业绩”变成了“销售额”），记得更新 Python 脚本中的 `df[['...']]` 部分。
