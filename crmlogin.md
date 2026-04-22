# Skill: CRM 系统自动化登录与 API 调用

## 1. 技能描述
通过模拟 HTTP POST 请求实现 CRM 系统的自动化登录。该技能不依赖特定 SDK，使用原生的 `curl` 命令处理身份验证、Session 保持（Cookie 管理）及后续数据查询。

## 2. 环境要求
* **工具**: `curl`, `md5sum` (或 Python 脚本处理 MD5)
* **网络**: 可访问 `crm.51talk.com` 的网络环境
* **权限**: 有效的 CRM 账号及密码

## 3. 配置参数 (Environment Variables)
在运行脚本前，请替换以下变量：
* `CRM_USER`: 员工账号 (如 `THCC-Panawat`)
* `CRM_PWD`: 原始明文密码
* `COOKIE_FILE`: 本地 Cookie 存储路径 (如 `./crm_cookie.txt`)

---

## 4. 执行逻辑 (Core Logic)

### Step 1: 密码哈希处理
将明文密码转换为 MD5 格式。
```bash
# 使用 Python 生成 MD5 示例
CRM_PWD_MD5=$(python3 -c "import hashlib; print(hashlib.md5('$CRM_PWD'.encode()).hexdigest())")
```

### Step 2: 环境清理
删除旧的凭证，防止会话冲突。
```bash
rm -f $COOKIE_FILE
```

### Step 3: 发送登录请求
模拟表单提交，自动捕获 Session 并存入 Cookie 文件。
```bash
curl -s -c "$COOKIE_FILE" -b "$COOKIE_FILE" -k -X POST \
  "https://crm.51talk.com/admin/login.php" \
  -d "user_name=$CRM_USER" \
  -d "password=$CRM_PWD_MD5" \
  -d "user_type=admin" \
  -d "redirect_uri=" \
  -d "login_employee_type=sideline" \
  -d "Submit=%E7%99%BB%E5%BD%95" \
  -L --max-redirs 3 --max-time 15 > login_response.html
```

### Step 4: 登录状态校验
通过检查响应体中是否包含关键字段 `admin_id` 来判定成功。
```bash
if grep -q "admin_id" login_response.html; then
    echo "Login Success"
else
    echo "Login Failed"
    exit 1
fi
```

### Step 5: 后续数据请求 (模版)
使用已保存的 Cookie 进行鉴权查询。
```bash
curl -s -b "$COOKIE_FILE" -k "https://crm.51talk.com/admin/api/target_data"
```

---

## 5. 注意事项
* **安全性**: 密码以 MD5 形式传输，但在本地处理时请注意日志脱敏。
* **SSL 校验**: 使用了 `-k` 跳过证书检查，在生产环境建议确保服务器证书有效并移除该参数。
* **重定向**: `-L` 参数至关重要，因为 CRM 登录后通常会跳转至首页。
* **超时**: 设置了 `--max-time 15` 防止在网络波动时脚本死锁。

---

## 6. 输入输出定义
* **Input**: 用户名、明文密码、目标 API URL。
* **Output**: 成功标志或 API 返回的结构化数据（JSON/HTML）。
