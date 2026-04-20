# Thai\-CC Operation Performance Skill

Streamable HTTP
transport

这是一个 AI Skill——安装后，你的 AI 助手就能自动完成 51Talk 泰国区域业绩数据的查询与分析：登录CRM系统、筛选有效业绩数据、美元转泰铢换算、全员排名统计，还能单独查询指定人员的业绩及排名，适配日常运营数据统计需求。

专为51Talk泰国区域运营场景设计，自动化完成每日业绩统计工作，无需手动操作CRM系统、换算汇率及筛选数据。

## 关于本Skill

适配51Talk CRM系统，用于泰国区域员工业绩数据的自动化查询、筛选、换算与排名展示，解决每日手动统计业绩的繁琐问题。

|项目|内容|
|---|---|
|Skill名称|Thai\-CC Operation Performance Skill|
|适配系统|51Talk CRM 兼职员工系统|
|核心用途|业绩排名统计、单人业绩查询、USD→THB自动换算|
|汇率标准|固定1 USD = 34 THB|

## 这个 Skill 能做什么

51Talk泰国区域业绩查询官方AI服务，包含 2 项核心能力 \+ 多项自动化辅助能力，全程无需手动操作CRM系统：

|能力|你可以问|说明|
|---|---|---|
|全员业绩排名|\&\#34;Full Rank\&\#34;\&\#34;导出全员业绩排名\&\#34;\&\#34;展示所有有效业绩排名\&\#34;|自动筛选有效数据、换算泰铢、按业绩降序展示完整排名|
|单人业绩查询|\&\#34;Query THCC\-Sara\&\#34;\&\#34;查询某人业绩\&\#34;\&\#34;某人的排名是多少\&\#34;|输入人名，直接返回该人员的全球排名及泰铢业绩|
|自动登录CRM|\&\#34;登录51Talk CRM\&\#34;\&\#34;获取业绩数据\&\#34;|内置固定账号密码，自动登录目标CRM页面，无需手动输入|
|数据筛选过滤|\&\#34;筛选有效业绩\&\#34;\&\#34;排除无效人员\&\#34;|自动排除指定黑名单人员，仅保留付款金额\&gt;200USD的有效数据|
|汇率自动换算|\&\#34;美元转泰铢\&\#34;\&\#34;业绩换算成泰铢\&\#34;|按固定汇率1:34，自动将美元业绩转换为泰铢，仅展示泰铢结果|

## 核心功能详情

### 1\. 全员业绩排名（Full Rank）

触发指令：**Full Rank**

功能说明：AI助手自动完成CRM登录、数据抓取、黑名单过滤、汇率换算，按泰铢业绩降序排列，生成完整的全员排名表，无人员遗漏，纯英文Markdown表格输出，仅展示Rank、Name、Performance \(THB\)三列。

### 2\. 单人业绩查询（Query \[Name\]）

触发格式：**Query \[姓名\]**（示例：Query THCC\-Sara）

功能说明：输入目标人员姓名，AI助手自动查询其对应的业绩数据，完成汇率换算后，返回该人员的全球排名、完整姓名及泰铢业绩，纯英文输出，无多余冗余信息。

### 3\. 自动化辅助规则

- 内置固定CRM登录账号密码，无需手动输入，自动跳转目标业绩页面

- 永久黑名单自动过滤，无需手动排除指定人员

- 仅统计付款金额\&gt;200USD的业绩数据，无效数据自动剔除

- 固定汇率1 USD = 34 THB，换算过程自动完成，不展示汇率及美元数据

## 使用流程

1. 安装本Skill（具体安装方法见下方）

2. 向AI助手发送触发指令，两种指令可选：
        

    - 需要全员排名：发送**Full Rank**，AI自动完成全流程，返回排名表格

    - 需要单人查询：发送 **Query 人名**（如Query THCC\-Sara），AI返回该人员详情

3. 首次使用无需额外配置，后续使用直接发送指令即可，无需重复登录CRM

注意：业绩数据来源于51Talk CRM系统，若系统页面解析失败，AI会提示异常，可稍后重试。

## 目录结构

Thai\-CC\-Operation/

     ├── README\.md                \# 说明文档（本文档）

     ├── skill\.md                 \# 核心文件：元数据 \+ Agent 指令

     ├── scripts/                 \# 预留目录（用于后续功能扩展）

     └── references/              \# 参考文档目录

## 安装

最简单的方式：告诉你的 AI 助手

直接拷贝下面这句话发给你的 AI 助手：

帮我安装 Thai\-CC Operation Performance Skill，仓库地址：https://github\.com/liuniuniu1228/Thai\-CC\-Operation/tree/main

Agent 会自动克隆仓库并安装到对应的 Skill 目录。

### 其他安装方式

手动克隆到 Skill 目录：将本仓库克隆到你项目下的 Skill 目录，不同 IDE 对应的路径：

|IDE|Skill 目录|
|---|---|
|Qoder|\.qoder/skills/Thai\-CC\-Operation/|
|Cursor|\.cursor/skills/Thai\-CC\-Operation/|
|Trae|\.trae/skills/Thai\-CC\-Operation/|
|Windsurf|\.windsurf/skills/Thai\-CC\-Operation/|
|Claude Code|\.claude/skills/Thai\-CC\-Operation/|
|通用|\.agents/skills/Thai\-CC\-Operation/|

示例：安装到 Qoder

```bash
git clone https://github.com/liuniuniu1228/Thai-CC-Operation/tree/main \ 
  .qoder/skills/Thai-CC-Operation
```

只要目录下有 `skill\.md`，Agent 下次启动就会自动加载这个 Skill。

## 发布平台

- GitHub：https://github\.com/liuniuniu1228/Thai\-CC\-Operation/tree/main

## 技术协议

|项目|说明|
|---|---|
|协议|MCP \(Model Context Protocol\)|
|传输|Streamable HTTP|

## 版本

当前版本：1\.0\.0

说明：本Skill版本独立演进，后续可根据需求扩展更多业绩统计功能。

## License

MIT

> （注：文档部分内容可能由 AI 生成）
