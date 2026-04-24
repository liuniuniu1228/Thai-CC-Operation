# CRM Performance Tracker v4.0 🚀

泰国 CC 团队数据监控工具，支持**业绩排行**、**通话效率**、**综合运营**、**体验课跟进**、**转化率分析**五大模块，支持日期筛选和个人/团队维度筛选。

---

## 目录结构

```
Thai-CC-Operation/
├── crm_tool.py         # 核心脚本（perf / call / static / info / conv 五种模式）
├── crmlogin.md         # 登录原理说明
├── requirements.txt    # 依赖：requests, beautifulsoup4, lxml
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

**字段**：排名、姓名、小组、业绩(USD)

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
| 首次/末次 | 当日首尾通话时间 |
| 总次数 | 拨号总次数 |
| 有效通话 | 符合标准（≥20秒）的有效次数 |
| 有效率 | 有效通话占比率 |
| 平均/次 | 每次通话平均时长(分钟) |

**快捷词**：`today`（今天）、`yesterday`（昨天）、`month`（本月）

---

### C. 综合运营数据查询 (static)

查询各团队/个人的新付费金额、订单金额、出席数、Leads、付费率等综合运营数据。
- 不带姓名参数：显示团队维度汇总
- 带姓名参数：显示个人维度数据

| 命令 | 说明 |
|-----|------|
| `python crm_tool.py static` | 今日各团队数据 |
| `python crm_tool.py static yesterday` | 昨天各团队数据 |
| `python crm_tool.py static month` | 本月各团队数据 |
| `python crm_tool.py static 2026-04-01 2026-04-23` | 指定日期区间 |
| `python crm_tool.py static Bell` | Bell 个人本月数据 |
| `python crm_tool.py static Bell yesterday` | Bell 昨天个人数据 |

**字段说明**：

| 字段 | 说明 |
|-----|------|
| 新付费(RMB) | 新付费金额（人民币） |
| 订单(USD) | 订单金额（美元） |
| 出席数 | 体验课/活动出席人次 |
| Leads | 线索总数 |
| MKT | 市场渠道线索数 |
| 转介leads | 转介绍渠道线索数 |
| 付费人数 | 当期付费用户数 |

---

### D. 体验课跟进数据查询 (info)

查询各员工/团队的体验课跟进情况，包含课前/课后拨打跟进率。

| 命令 | 说明 |
|-----|------|
| `python crm_tool.py info` | 今日体验课跟进数据 |
| `python crm_tool.py info yesterday` | 昨天体验课跟进数据 |
| `python crm_tool.py info week` | 近7天体验课跟进 |
| `python crm_tool.py info month` | 本月体验课跟进 |
| `python crm_tool.py info Fern yesterday` | Fern 昨天体验课跟进详情 |
| `python crm_tool.py info Fern 2026-04-01 2026-04-23` | Fern 指定日期区间 |

**字段说明**：

| 字段 | 说明 |
|-----|------|
| 体验课量 | 当期体验课总数量 |
| 课前跟进（打过） | 课前主动拨打过电话的完成度/跟进数 |
| 课前跟进（打通） | 课前电话打通的完成度/跟进数 |
| 课前未跟进 | 课前未拨打的完成度/未跟进数 |
| 课后跟进（打过） | 课后主动拨打过电话的完成度/跟进数 |
| 课后跟进（打通） | 课后电话打通的完成度/跟进数 |
| 课后未跟进 | 课后未拨打的完成度/未跟进数 |
| 课后出席拨打量/拨通量 | 针对已出席用户的拨打和拨通数 |
| 课后未出席拨打量/拨通量 | 针对未出席用户的拨打和拨通数 |

**快捷词**：`today`（今天）、`yesterday`（昨天）、`week`（近7天）、`month`（本月）

---

### E. 转化率分析 (conv) ⭐ 新增

查询员工/团队的市场转化率、转介绍转化率及转介绍占比。

**三个核心指标的计算公式：**

| 指标 | 公式 | 说明 |
|-----|------|------|
| **市场转化率** | (付费人数 - 转介绍单量) / MKT leads | 去除转介绍后的市场获客效率 |
| **转介绍转化率** | 转介绍总单量 / 转介绍leads | 转介绍线索的转化能力 |
| **转介绍占比** | 转介绍订单USD / 新付费RMB | 转介绍在整体收入的贡献比例 |

| 命令 | 说明 |
|-----|------|
| `python crm_tool.py conv` | 全员本月转化率排行 |
| `python crm_tool.py conv yesterday` | 昨天全员转化率 |
| `python crm_tool.py conv Bell` | Bell 本月转化率 |
| `python crm_tool.py conv Bell yesterday` | Bell 昨天转化率 |
| `python crm_tool.py conv Bell 2026-04-01 2026-04-23` | Bell 指定日期区间 |
| `python crm_tool.py conv --team TH-CC01Team` | TH-CC01Team 本月团队转化率 |
| `python crm_tool.py conv --team TH-CC01Team yesterday` | TH-CC01Team 昨天团队转化率 |

**输出字段**：

| 字段 | 说明 |
|-----|------|
| 新付费(RMB) | 新付费总金额（人民币） |
| 付费人数 | 当期付费用户数 |
| 转介单 | 转介绍渠道订单数 |
| MKT | 市场渠道线索数 |
| 转介leads | 转介绍渠道线索数 |
| 市场转化率 | (付费人数 - 转介单) / MKT |
| 转介转化率 | 转介单 / 转介leads |
| 转介占比 | 转介订单USD / 新付费RMB |

---

## 注意事项

1. **日期格式**：必须为 `YYYY-MM-DD`（如 `2026-04-24`）
2. **VPN**：访问 `crm.51talk.com` 需确保网络畅通
3. **快捷查询**：`call`、`info`、`static`、`conv` 模式均支持 `today` / `yesterday` / `month` 快捷词；`info` 额外支持 `week`
4. **长跨度查询**：查询超过 30 天的数据时，响应可能较慢
5. **团队 vs 个人**：
   - `static` 不带姓名 → 团队维度；带姓名 → 个人维度
   - `conv` 不带姓名/团队 → 全员；带姓名 → 个人；带 `--team` → 团队
6. **安全提醒**：请勿将包含明文密码的脚本推送至公开仓库

---

## 快速参考

```bash
# 业绩排行
python crm_tool.py perf                          # 前5名
python crm_tool.py perf Fern                     # Fern 业绩

# 通话效率
python crm_tool.py call                          # 今日通话 TOP 20
python crm_tool.py call yesterday                # 昨天全员通话
python crm_tool.py call Fern yesterday           # Fern 昨天通话

# 综合运营
python crm_tool.py static                        # 今日各团队数据
python crm_tool.py static yesterday              # 昨天各团队数据
python crm_tool.py static Bell                  # Bell 个人本月数据

# 体验课跟进
python crm_tool.py info                          # 今日体验课跟进
python crm_tool.py info week                    # 近7天
python crm_tool.py info Bell yesterday           # Bell 昨天体验课跟进详情

# 转化率分析（新增）
python crm_tool.py conv                          # 全员本月转化率排行
python crm_tool.py conv yesterday                # 昨天全员转化率
python crm_tool.py conv Bell                     # Bell 本月转化率
python crm_tool.py conv Bell yesterday           # Bell 昨天转化率
python crm_tool.py conv --team TH-CC01Team       # TH-CC01Team 本月团队转化率
```
