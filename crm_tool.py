import requests
import hashlib
import pandas as pd
from bs4 import BeautifulSoup
import sys

# --- 配置区 ---
CRM_URL = "https://crm.51talk.com/admin/login.php"
DATA_URL = "https://crm.51talk.com/Performance/getSsPreformanceList?type=2"
USER_NAME = "THCC-Panawat"
RAW_PWD = "b@2A5qt7"

def get_performance():
    # 1. 密码 MD5 加密
    pwd_md5 = hashlib.md5(RAW_PWD.encode()).hexdigest()
    
    # 2. 建立 Session（自动处理 Cookie）
    session = requests.Session()
    
    # 3. 登录请求
    login_data = {
        "user_name": USER_NAME,
        "password": pwd_md5,
        "user_type": "admin",
        "login_employee_type": "sideline",
        "Submit": "登录"
    }
    
    try:
        response = session.post(CRM_URL, data=login_data, verify=False, timeout=15)
        
        # 4. 校验登录状态
        if "admin_id" not in response.text:
            print("❌ 登录失败，请检查账号密码或网络。")
            return
        
        # 5. 访问业绩页面
        data_resp = session.get(DATA_URL, verify=False)
        
        # 6. 解析网页内容
        # 使用 pandas 直接提取表格，或者使用 BeautifulSoup 精确提取
        soup = BeautifulSoup(data_resp.text, 'html.parser')
        table = soup.find('table') # 假设业绩在页面第一个表格
        
        if not table:
            print("❌ 未能在页面中找到业绩表格。")
            return

        df = pd.read_html(str(table))[0]
        
        # 7. 提取你需要的字段
        # 注意：这里的列名必须和网页上显示的中文完全一致
        target_columns = ["序号", "姓名", "业绩", "小组"]
        final_df = df[target_columns]
        
        # 输出 JSON 格式，方便 Agent 读取
        print(final_df.to_json(orient='records', force_ascii=False, indent=2))

    except Exception as e:
        print(f"⚠️ 发生错误: {e}")

if __name__ == "__main__":
    get_performance()
