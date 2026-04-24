# Skill: CRM 综合运营数据助手 (perf / call / static / info / conv)

## 1. 技能描述

此技能允许 Agent 登录 CRM 系统，抓取并关联五类核心数据：

| 模块 | 功能 | 数据来源 | 快捷词 |
|:---|:---|:---|:---|
| **业绩排行** (perf) | 实时个人业绩排名 | `getSsPreformanceList?type=2` | - |
| **通话效率** (call) | 每日通话时长、次数、有效率 | `cc_call_info_new.php` | today / yesterday / month |
| **综合运营** (static) | 各团队/个人新付费、订单、出席、Leads | `custom_static_cc.php` | today / yesterday / month |
| **体验课跟进** (info) | 课前/课后拨打跟进率 | `cc_static_new_info_new.php` | today / yesterday / week / month |
| **转化率分析** (conv) | 市场转化率、转介转化率、转介占比 | `custom_static_cc.php` | today / yesterday / month |

---

## 2. Agent 运行逻辑

### Step 1：判断模式

```
问业绩/排名/谁最高         → perf
问通话/打电话/时长/次数     → call
问团队/出席/Leads/付费率    → static
问课前/课后/体验课/拨打率   → info
问转化率/市场转化/转介占比   → conv
问个人综合表现             → 组合 perf / call / static / info / conv
```

### Step 2：判断筛选维度

```
查某人          → 传 name 参数（模糊匹配）
查某团队        → conv 模式传 --team 参数
查全员/全团队   → 不传筛选参数
```

### Step 3：判断日期

```
今天的数据    → today 或不传
昨天的数据    → yesterday
本月数据      → month
近7天         → week（仅 info 模式支持）
指定日期区间  → 传入 start_date 和 end_date（YYYY-MM-DD）
```

### Step 4：执行并解读

运行 `crm_tool.py`，提取关键数字，用自然语言回复用户。

---

## 3. 对话示例

**场景 A：问团队转化率**
- *用户*：TH-CC01Team 本月市场转化率多少？
- *Agent*：运行 `python crm_tool.py conv --team TH-CC01Team month` → "TH-CC01Team 本月付费人数67，转介绍单28，MKT leads 1936，市场转化率 = (67-28)/1936 = 2.01%，转介转化率 = 28/94 = 29.79%..."

**场景 B：问某人转化率**
- *用户*：Bell 这个月转化率怎么样？
- *Agent*：运行 `python crm_tool.py conv Bell` → "Bell 本月付费人数10，转介单6，MKT 215，市场转化率 = (10-6)/215 = 1.86%，转介转化率 = 6/13 = 46.15%，转介占比 = 6061.57/9267.31 = 65.4%..."

**场景 C：问业绩排名**
- *用户*：现在业绩前三是谁？
- *Agent*：运行 `python crm_tool.py perf` → "🥇 phakkhaphon 22790 USD，🥈 THCC-A 19237 USD，🥉 bird 17790 USD"

**场景 D：问某人通话效率**
- *用户*：phakkhaphon 昨天打了多久电话？
- *Agent*：运行 `python crm_tool.py call phakkhaphon yesterday` → "phakkhaphon 昨天总通话 177.8 分钟，打了 96 次，有效率 30.2%..."

**场景 E：问某人体验课跟进**
- *用户*：Bell 昨天体验课课前跟进情况？
- *Agent*：运行 `python crm_tool.py info Bell yesterday` → 显示 Bell 昨天的体验课量、课前打过/打通、未跟进等全部字段

---

## 4. 字段说明

### perf（业绩）
| 字段 | 说明 |
|:---|:---|
| 排名 | 数字越小排名越高，前三名显示🥇🥈🥉 |
| 姓名 | 支持模糊匹配 |
| 小组 | 所属团队 |
| 业绩(USD) | 订单金额（美元） |

### call（通话）
| 字段 | 说明 |
|:---|:---|
| 总时长 | 累计通话分钟数 |
| 首次/末次 | 当日首尾通话时间 |
| 总次数 | 拨号总次数 |
| 有效通话 | 符合标准（≥20秒）的有效次数 |
| 有效率 | 有效通话占比率 |

### static（综合运营）
| 字段 | 说明 |
|:---|:---|
| 新付费(RMB) | 新付费金额（人民币） |
| 订单(USD) | 订单金额（美元） |
| 出席数 | 体验课/活动出席人次 |
| Leads | 线索总数 |
| MKT | 市场渠道线索数 |
| 转介leads | 转介绍渠道线索数 |
| 付费人数 | 当期付费用户数 |

### info（体验课跟进）
| 字段 | 说明 |
|:---|:---|
| 体验课量 | 当期体验课总数量 |
| 课前跟进（打过） | 完成度% / 跟进数 |
| 课前跟进（打通） | 完成度% / 打通数 |
| 课前未跟进 | 未完成度% / 未跟进数 |
| 课后跟进（打过） | 完成度% / 跟进数 |
| 课后跟进（打通） | 完成度% / 打通数 |
| 课后未跟进 | 未完成度% / 未跟进数 |
| 课后出席拨打量/拨通量 | 针对已出席用户的拨打和拨通数 |
| 课后未出席拨打量/拨通量 | 针对未出席用户的拨打和拨通数 |

### conv（转化率分析）⭐
| 字段 | 说明 |
|:---|:---|
| 新付费(RMB) | 新付费总金额（人民币） |
| 付费人数 | 当期付费用户数 |
| 转介单 | 转介绍渠道订单数 |
| MKT | 市场渠道线索数 |
| 转介leads | 转介绍渠道线索数 |
| **市场转化率** | (付费人数 - 转介单) / MKT |
| **转介转化率** | 转介单 / 转介leads |
| **转介占比** | 转介订单USD / 新付费RMB |

---

## 5. conv 模式详解

### 三个核心公式

```python
市场转化率 = (付费人数 - 转介绍总单量) / MKT leads
转介绍转化率 = 转介绍总单量 / 转介绍leads
转介绍占比 = 转介绍订单付款金额(USD) / 新付费金额(RMB)
```

### 筛选参数优先级

```
1. name 参数  → 个人维度（is_show_group='n', all_user=姓名）
2. --team 参数 → 团队维度（group_list=团队名）
3. 两者皆无   → 全员数据（is_show_group='n'）
```

### 日期参数

| 快捷词 | 含义 | 支持模式 |
|:---|:---|:---|
| today | 今天 | call / static / info / conv |
| yesterday | 昨天 | call / static / info / conv |
| week | 近7天 | info |
| month | 本月 | call / static / info / conv |
| YYYY-MM-DD YYYY-MM-DD | 自定义日期区间 | call / static / info / conv |

---

## 6. 维护说明

- **字段索引**：如果 CRM 页面结构调整，优先修改 Python 脚本中的 `cells[n]` 索引
- **安全规范**：严禁在对话中输出 MD5 哈希、Cookie、密码等敏感信息
- **时效性**：所有数据均为实时查询，每次提问时重新执行脚本获取最新数据
- **日期格式**：必须为 `YYYY-MM-DD`（如 `2026-04-24`）
- **模糊匹配**：name 参数支持大小写不敏感的部分匹配（如 "Bell" 可匹配 "thcc-Bell"）
```

三份都给你了，可以直接复制粘贴。
