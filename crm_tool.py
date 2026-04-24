import os
import re
import warnings
import requests
import hashlib
from bs4 import BeautifulSoup
import sys
from datetime import datetime

warnings.filterwarnings('ignore')

# --- 配置区 ---
CRM_URL = "https://crm.51talk.com/admin/login.php"
PERF_URL = "https://crm.51talk.com/Performance/getSsPreformanceList?type=2"
CALL_URL = "https://crm.51talk.com/admin/user/cc_call_info_new.php"
USER_NAME = "THCC-Panawat"
RAW_PWD = os.getenv("CRM_PWD", "b@2A5qt7")

def get_session():
    """统一登录逻辑"""
    pwd_md5 = hashlib.md5(RAW_PWD.encode()).hexdigest()
    session = requests.Session()
    login_data = {
        "user_name": USER_NAME,
        "password": pwd_md5,
        "user_type": "admin",
        "login_employee_type": "sideline",
        "Submit": "登录"
    }
    try:
        response = session.post(CRM_URL, data=login_data, verify=False, timeout=15)
        if "admin_id" not in response.text:
            print("❌ 登录失败，请检查账号密码或网络。")
            return None
        return session
    except Exception as e:
        print(f"⚠️ 登录异常: {e}")
        return None

def fetch_performance(session, name=None, top_n=5):
    """获取业绩数据 (保持不变)"""
    try:
        resp = session.get(PERF_URL, verify=False, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        tables = soup.find_all('table')
        if len(tables) < 2: return
        
        rows = tables[1].find_all('tr')
        results = []
        for row in rows:
            cells = row.find_all('td')
            if not cells or len(cells) < 13: continue
            
            seq = cells[0].get_text(strip=True)
            if not seq:
                img = cells[0].find('img')
                seq = img['src'].split('/')[-1].replace('.png', '') if img else ''
            
            name_val = cells[1].get_text(strip=True)
            group = cells[2].get_text(strip=True)
            perf = cells[12].get_text(strip=True).replace(',', '')
            
            if name and name.lower() not in name_val.lower(): continue
            results.append({"rank": seq, "name": name_val, "group": group, "value": perf})

        output = results if name else results[:top_n]
        print(f"\n--- 业绩排行榜 (Target: {name if name else 'Top '+str(top_n)}) ---")
        for r in output:
            print(f"排名 {r['rank']:>3} | {r['name']:<20} | {r['group']:<15} | 业绩: {r['value']}")
    except Exception as e:
        print(f"业绩抓取错误: {e}")

def fetch_call_data(session, name=None, start_date=None, end_date=None, top_n=20):
    """获取通话数据，支持日期筛选"""
    # 如果没传日期，默认当天
    today = datetime.now().strftime('%Y-%m-%d')
    start_date = start_date or today
    end_date = end_date or today

    # 构造表单数据，模拟点击 submit
    post_data = {
        "start_time": start_date,
        "end_time": end_date,
        "submit": "submit" # 对应截图中的 submit 按钮
    }

    try:
        # 使用 POST 请求提交日期筛选
        resp = session.post(CALL_URL, data=post_data, verify=False, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', {'id': 'salary'})
        
        if not table:
            print(f"❌ 未能找到 {start_date} 至 {end_date} 的通话数据表格。")
            return

        rows = table.find_all('tr')
        results = []
        
        # 解析逻辑
        for row in rows[2:]:  # 跳过表头和合计
            cells = row.find_all('td')
            if not cells or len(cells) < 12:
                continue
            cc_name = cells[1].get_text(strip=True)
            if not cc_name:
                continue
            results.append({
                "cc": cc_name,
                "total_duration": cells[2].get_text(strip=True),
                "total_calls": cells[5].get_text(strip=True),
                "eff_rate": cells[7].get_text(strip=True),
            })

        if name:
            output = [r for r in results if name.lower() in r["cc"].lower()]
        else:
            output = results[:top_n]

        print(f"\n--- 通话效率统计 ({start_date} 至 {end_date}) ---")
        for r in output:
            print(f"CC: {r['cc']:<20} | 总时长: {r['total_duration']:>7}min | 总次数: {r['total_calls']:>3} | 有效率: {r['eff_rate']}")

        if not output:
            print("未找到匹配的通话记录。")
        return output
    except Exception as e:
        print(f"通话数据抓取错误: {e}")

if __name__ == "__main__":
    # 使用方法更新：
    # python crm_tool.py perf [姓名]
    # python crm_tool.py call [姓名] [开始日期] [结束日期]
    # 示例：python crm_tool.py call "Panawat" 2026-04-01 2026-04-24
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "perf"
    target_name = sys.argv[2] if (len(sys.argv) > 2 and sys.argv[2] != "None") else None
    s_date = sys.argv[3] if len(sys.argv) > 3 else None
    e_date = sys.argv[4] if len(sys.argv) > 4 else None
    
    sess = get_session()
    if sess:
        if mode == "perf":
            fetch_performance(sess, name=target_name)
        elif mode == "call":
            fetch_call_data(sess, name=target_name, start_date=s_date, end_date=e_date)
        else:
            print("未知模式，请使用 'perf' 或 'call'")
