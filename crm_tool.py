import os
import re
import warnings
import requests
import hashlib
from bs4 import BeautifulSoup
import sys
from datetime import datetime, timedelta

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
        response = session.post(CRM_URL, data=login_data, verify=False, timeout=30)
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
        resp = session.get(PERF_URL, verify=False, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        tables = soup.find_all('table')
        if len(tables) < 2:
            print("❌ 未找到业绩表格")
            return

        rows = tables[1].find_all('tr')
        results = []
        for row in rows:
            cells = row.find_all('td')
            if not cells or len(cells) < 13:
                continue
            seq = cells[0].get_text(strip=True)
            if not seq:
                img = cells[0].find('img')
                seq = img['src'].split('/')[-1].replace('.png', '') if img else ''
            name_val = cells[1].get_text(strip=True)
            group = cells[2].get_text(strip=True)
            perf = cells[12].get_text(strip=True).replace(',', '')
            if name and name.lower() not in name_val.lower():
                continue
            results.append({"rank": seq, "name": name_val, "group": group, "value": perf})

        output = results if name else results[:top_n]
        print(f"\n--- 业绩排行榜 (Target: {name if name else 'Top ' + str(top_n)}) ---")
        for r in output:
            print(f"排名 {r['rank']:>3} | {r['name']:<20} | {r['group']:<15} | 业绩: {r['value']}")
    except Exception as e:
        print(f"业绩抓取错误: {e}")


def fetch_call_data(session, name=None, start_date=None, end_date=None, top_n=20):
    """
    获取通话数据，支持日期筛选
    注意事项：
      - 该页面使用 JavaScript 动态加载数据
      - Python 直接 POST 日期筛选可能无法正确返回历史数据
      - 建议优先使用 'today' / 'yesterday' 快捷查询
    """
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    # 判断查询类型
    if start_date == 'today':
        post_data = {"ben_day": "Today"}
        date_label = today
    elif start_date == 'yesterday':
        post_data = {"yesterday": "Yesterday"}
        date_label = yesterday
    else:
        # 自定义日期
        s = start_date or today
        e = end_date or today
        # 完整表单参数（参考页面源码中的字段名）
        post_data = {
            "start_date": s,
            "end_date": e,
            "group_name": "",
            "group_list": "",
            "is_show_group": "y",
            "": "submit"
        }
        date_label = f"{s} 至 {e}"

    try:
        resp = session.post(CALL_URL, data=post_data, verify=False, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', {'id': 'salary'})

        if not table:
            print(f"❌ 未找到 {date_label} 的通话数据表格")
            return

        rows = table.find_all('tr')
        results = []

        # 解析数据行（跳过表头行0 和 合计行1）
        for row in rows[2:]:
            cells = row.find_all('td')
            if not cells or len(cells) < 12:
                continue
            cc_name = cells[1].get_text(strip=True)
            if not cc_name or not re.sub(r'[^a-zA-Z]', '', cc_name):
                # 跳过纯数字或空行
                continue
            results.append({
                "cc": cc_name,
                "total_duration": cells[2].get_text(strip=True),
                "first_call": cells[3].get_text(strip=True),
                "last_call": cells[4].get_text(strip=True),
                "total_calls": cells[5].get_text(strip=True),
                "valid_calls": cells[6].get_text(strip=True),
                "eff_rate": cells[7].get_text(strip=True),
                "avg_call": cells[8].get_text(strip=True),
            })

        if name:
            output = [r for r in results if name.lower() in r["cc"].lower()]
        else:
            # 默认按通话时长降序
            sorted_results = []
            for r in results:
                try:
                    dur = float(r['total_duration']) if r['total_duration'] else 0
                except:
                    dur = 0
                sorted_results.append((dur, r))
            sorted_results.sort(key=lambda x: -x[0])
            output = [r for _, r in sorted_results[:top_n]]

        print(f"\n--- 通话效率统计 ({date_label}) ---")
        for r in output:
            print(f"CC: {r['cc']:<20} | 时长: {r['total_duration']:>7}min | 首次: {r['first_call']:<8} | "
                  f"次数: {r['total_calls']:>3} | 有效率: {r['eff_rate']}")

        if not output:
            print("未找到匹配的通话记录")

        return output

    except Exception as e:
        print(f"通话数据抓取错误: {e}")


if __name__ == "__main__":
    # 使用方法：
    # python crm_tool.py perf                    -> 业绩前5名
    # python crm_tool.py perf Fern               -> Fern 的业绩
    # python crm_tool.py call                    -> 今天通话前20名
    # python crm_tool.py call Fern               -> Fern 的今天通话
    # python crm_tool.py call Fern yesterday     -> Fern 的昨天通话
    # python crm_tool.py call Fern 2026-04-01 2026-04-22  -> Fern 某段日期
    # python crm_tool.py call yesterday           -> 昨天通话前20名
    # python crm_tool.py call today              -> 今天通话前20名

    mode = sys.argv[1] if len(sys.argv) > 1 else "perf"
    target_name = sys.argv[2] if len(sys.argv) > 2 else None
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
