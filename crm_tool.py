import os
import re
import warnings
import requests
import hashlib
from bs4 import BeautifulSoup
import sys

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
    """获取业绩数据"""
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

def fetch_call_data(session, name=None):
    """获取通话数据"""
    try:
        # 默认访问页面，获取当日数据
        resp = session.get(CALL_URL, verify=False, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', {'id': 'table_id'}) or soup.find('table') # 尝试定位通话表格
        
        if not table:
            print("❌ 未能找到通话数据表格。")
            return

        rows = table.find_all('tr')
        print(f"\n--- 通话效率统计 (Target: {name if name else '全部'}) ---")
        found = False
        
        for row in rows:
            cells = row.find_all('td')
            # 假设字段索引：CC(0), 通话总时长(1), 首次通话(2), 通话总次数(3)
            # 注意：如果 CRM 列顺序不同，请调整 cells[n] 的索引
            if len(cells) < 4: continue
            
            cc_name = cells[0].get_text(strip=True)
            if cc_name == "CC" or not cc_name: continue # 跳过表头
            
            if name and name.lower() not in cc_name.lower(): continue
            
            duration = cells[1].get_text(strip=True)
            first_call = cells[2].get_text(strip=True)
            total_calls = cells[3].get_text(strip=True)
            
            print(f"CC: {cc_name:<15} | 总时长: {duration:<10} | 首次: {first_call:<10} | 次数: {total_calls}")
            found = True
        
        if not found: print("未找到匹配的通话记录。")
    except Exception as e:
        print(f"通话数据抓取错误: {e}")

if __name__ == "__main__":
    # 使用方法：
    # python crm_tool.py perf [姓名]  -> 查业绩
    # python crm_tool.py call [姓名]  -> 查通话
    mode = sys.argv[1] if len(sys.argv) > 1 else "perf"
    target_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    sess = get_session()
    if sess:
        if mode == "perf":
            fetch_performance(sess, name=target_name)
        elif mode == "call":
            fetch_call_data(sess, name=target_name)
        else:
            print("未知模式，请使用 'perf' 或 'call'")
