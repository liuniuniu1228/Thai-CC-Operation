# CRM Performance Tracker v3.0 🚀

泰国 CC 团队数据监控工具，支持**业绩排名**、**通话效率**、**综合运营数据**三大模块，支持日期筛选。

---

## 目录结构

```
Thai-CC-Operation/
├── crm_tool.py         # 核心脚本（perf / call / static 三种模式）
├── crmlogin.md         # 登录原理说明
├── requirements.txt     # 依赖：requests, beautifulsoup4, lxml
└── README.md           # 本文档
```

---

## 环境配置

```bash
pip install -r requirements.txt
```

**凭证管理**：
- 脚本内置默认账号，可通过环境变量覆盖：
  ```bash
  export CRM_PWD="你的密码"
  ```

---

## 运行指令

```
python crm_tool.py [模式] [参数...]
```

---

### A. 业绩查询 (perf)

查询员工实时业绩排行榜。

| 命令 | 说明 |
|-----|------|
| `python crm_tool.py perf` | 前 5 名业绩排行 |
| `python crm_tool.py perf Fern` | Fern 的业绩及排名 |

**字段说明**：排名、姓名、小组、业绩(USD)

---

### B. 通话效率查询 (call)

查询员工每日通话数据，支持日期筛选。

| 命令 | 说明 |
|-----|------|
| `python crm_tool.py call` | 今日全员通话 TOP 20 |
| `python crm_tool.py call yesterday` | 昨天全员通话 |
| `python crm_tool.py call month` | 本月累计通话 |
| `python crm_tool.py call Fern` | Fern 今日通话 |
| `python crm_tool.py call Fern yesterday` | Fern 昨天通话 |
| `python crm_tool.py call Fern 2026-04-01 2026-04-22` | Fern 指定日期区间 |

**字段说明**：

| 字段 | 说明 |
|-----|------|
| 总时长 | 累计通话分钟数 |
| 首次通话 | 当日第一通电话时间 |
| 末次通话 | 当日最后一通电话时间 |
| 总次数 | 拨号总次数 |
| 有效通话 | 符合标准的有效通话次数 |
| 有效率 | 有效通话占比率 |
| 平均/次 | 每次通话平均时长(分钟) |

**快捷词**：`today`（今天）、`yesterday`（昨天）、`month`（本月）

---

### C. 综合运营数据查询 (static)

查询各团队的新付费金额、订单金额、出席数、Leads、付费率等综合运营数据。

| 命令 | 说明 |
|-----|------|
| `python crm_tool.py static` | 今日各团队数据 |
| `python crm_tool.py static yesterday` | 昨天各团队数据 |
| `python crm_tool.py static month` | 本月各团队数据 |
| `python crm_tool.py static 2026-04-01 2026-04-23` | 指定日期区间 |

**字段说明**：

| 字段 | 说明 |
|-----|------|
| 新付费(RMB) | 新付费金额（人民币） |
| 订单(USD) | 订单金额（美元） |
| 出席数 | 体验课/活动出席人次 |
| Leads | 线索总数 |
| MKT Leads | 市场线索数 |
| 转介绍Leads | 转介绍线索数 |
| 付费人数 | 当期付费用户数 |
| 付费率 | 付费人数/出席人数（含目标） |

---

## 注意事项

1. **日期格式**：必须为 `YYYY-MM-DD`（如 `2026-04-24`）
2. **VPN**：访问 `crm.51talk.com` 需确保网络畅通
3. **快捷查询**：`call` 和 `static` 模式均支持 `today` / `yesterday` / `month` 快捷词
4. **长跨度查询**：查询超过 30 天的数据时，响应可能较慢
5. **安全提醒**：请勿将包含明文密码的脚本推送至公开仓库

---

## 快速参考

```bash
# 今日业绩前5
python crm_tool.py perf

# Fern 业绩
python crm_tool.py perf Fern

# 今日通话 TOP 20
python crm_tool.py call

# 昨天全员通话
python crm_tool.py call yesterday

# Fern 昨天通话
python crm_tool.py call Fern yesterday

# 今日各团队综合数据
python crm_tool.py static

# 昨天各团队综合数据
python crm_tool.py static yesterday

# 指定日期区间综合数据
python crm_tool.py static 2026-04-01 2026-04-23
