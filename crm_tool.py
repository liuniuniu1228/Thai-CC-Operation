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
STATIC_URL = "https://crm.51talk.com/admin/user/custom_static_cc.php"
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
    快捷词：'today' / 'yesterday' / 'month'（本月）
    """
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    if start_date == 'today':
        post_data = {"ben_day": "Today"}
        date_label = today
    elif start_date == 'yesterday':
        post_data = {"yesterday": "Yesterday"}
        date_label = yesterday
    elif start_date == 'month':
        post_data = {"ben_month": "本月"}
        date_label = f"{today[:7]}-01 至 {today}"
    else:
        s = start_date or today
        e = end_date or today
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

        for row in rows[2:]:
            cells = row.find_all('td')
            if not cells or len(cells) < 12:
                continue
            cc_name = cells[1].get_text(strip=True)
            if not cc_name or not re.sub(r'[^a-zA-Z]', '', cc_name):
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


def fetch_static(session, start_date=None, end_date=None, date_mode=None):
    """
    获取综合运营数据（custom_static_cc.php）
    date_mode: 'today' / 'yesterday' / 'month' / 'all'（全量，默认）
    也可以直接传 start_date + end_date
    """
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    if date_mode == 'today':
        post_data = {"ben_day": "今天"}
        date_label = today
    elif date_mode == 'yesterday':
        post_data = {"yesterday": "昨天"}
        date_label = yesterday
    elif date_mode == 'month':
        post_data = {"ben_month": "本月"}
        date_label = f"{today[:7]}-01 至 {today}"
    else:
        s = start_date or '2026-04-01'
        e = end_date or today
        post_data = {
            "start_date": s,
            "end_date": e,
            "all_user": "",
            "group_name": "",
            "group_list": "",
            "is_show_group": "y",
            "xk": "en",
            "": "搜索"
        }
        date_label = f"{s} 至 {e}"

    try:
        resp = session.post(STATIC_URL, data=post_data, verify=False, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', {'id': 'salary'})

        if not table:
            print(f"❌ 未找到 {date_label} 的数据")
            return

        rows = table.find_all('tr')
        results = []

        for row in rows[2:]:
            cells = row.find_all('td')
            if not cells or len(cells) < 20:
                continue
            cc_name = cells[1].get_text(strip=True)
            if not cc_name or cc_name in ['总计']:
                continue
            results.append({
                "team": cc_name,
                "emp_id": cells[2].get_text(strip=True),
                "tenure": cells[3].get_text(strip=True),
                "new_pay_rmb": cells[5].get_text(strip=True),
                "order_usd": cells[6].get_text(strip=True),
                "referral_pay": cells[7].get_text(strip=True),
                "referral_orders": cells[8].get_text(strip=True),
                "attend_rate": cells[11].get_text(strip=True),
                "attend": cells[12].get_text(strip=True),
                "leads": cells[13].get_text(strip=True),
                "mkt_leads": cells[14].get_text(strip=True),
                "referral_leads": cells[15].get_text(strip=True),
                "narrow_leads": cells[16].get_text(strip=True),
                "paid_num": cells[17].get_text(strip=True),
                "paid_rate": cells[18].get_text(strip=True),
                "paid_usd": cells[19].get_text(strip=True),
            })

        # 默认按时长降序（order_usd）
        sorted_results = []
        for r in results:
            try:
                v = float(r['order_usd'].replace(',', '')) if r['order_usd'] else 0
            except:
                v = 0
            sorted_results.append((v, r))
        sorted_results.sort(key=lambda x: -x[0])
        results = [r for _, r in sorted_results]

        print(f"\n--- 综合运营数据 ({date_label}) ---")
        print(f"{'排名':<4} {'团队':<20} {'新付费(RMB)':>12} {'订单(USD)':>10} {'出席数':>6} {'Leads':>6} {'付费人数':>6}")
        print("-" * 75)
        for i, r in enumerate(results, 1):
            print(f"{i:<4} {r['team']:<20} {r['new_pay_rmb']:>12} {r['order_usd']:>10} "
                  f"{r['attend']:>6} {r['leads']:>6} {r['paid_num']:>6}")

        if not results:
            print("未找到数据")

        return results

    except Exception as e:
        print(f"综合数据抓取错误: {e}")


if __name__ == "__main__":
    # 使用方法：
    # python crm_tool.py perf                     -> 业绩前5名
    # python crm_tool.py perf Fern                 -> Fern 的业绩
    #
    # python crm_tool.py call                     -> 今天通话前20名
    # python crm_tool.py call Fern                 -> Fern 今天通话
    # python crm_tool.py call Fern yesterday       -> Fern 昨天通话
    # python crm_tool.py call yesterday           -> 昨天通话前20名
    # python crm_tool.py call today               -> 今天通话
    # python crm_tool.py call month               -> 本月通话
    #
    # python crm_tool.py static                   -> 今天综合数据
    # python crm_tool.py static yesterday         -> 昨天综合数据
    # python crm_tool.py static month             -> 本月综合数据
    # python crm_tool.py static 2026-04-01 2026-04-23 -> 指定日期区间

    mode = sys.argv[1] if len(sys.argv) > 1 else "perf"
    arg2 = sys.argv[2] if len(sys.argv) > 2 else None
    arg3 = sys.argv[3] if len(sys.argv) > 3 else None
    arg4 = sys.argv[4] if len(sys.argv) > 4 else None

    sess = get_session()
    if sess:
        if mode == "perf":
            fetch_performance(sess, name=arg2)
        elif mode == "call":
            # 支持: call [姓名] [today/yesterday/month/日期]
            name = arg2 if arg2 and arg2 not in ['today', 'yesterday', 'month'] else None
            s = arg2 if arg2 in ['today', 'yesterday', 'month'] else arg2
            e = arg3 if arg2 in ['today', 'yesterday', 'month'] else arg3
            fetch_call_data(sess, name=name, start_date=s, end_date=e)
        elif mode == "static":
            # 支持: static [today/yesterday/month/日期1 日期2]
            if arg2 in ['today', 'yesterday', 'month']:
                fetch_static(sess, date_mode=arg2)
            else:
                s = arg2 or None
                e = arg3 or None
                fetch_static(sess, start_date=s, end_date=e)
        else:
            print("未知模式，请使用 'perf' / 'call' / 'static'")
