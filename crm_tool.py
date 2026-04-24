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
INFO_URL = "https://crm.51talk.com/admin/user/cc_static_new_info_new.php"
USER_NAME = "THCC-Panawat"
RAW_PWD = os.getenv("CRM_PWD", "b@2A5qt7")

# --- 核心工具函数 ---

def get_session():
    """统一登录"""
    pwd_md5 = hashlib.md5(RAW_PWD.encode()).hexdigest()
    session = requests.Session()
    try:
        resp = session.post(CRM_URL, data={
            "user_name": USER_NAME, "password": pwd_md5,
            "user_type": "admin", "login_employee_type": "sideline", "Submit": "登录"
        }, verify=False, timeout=30)
        if "admin_id" not in resp.text:
            print("❌ 登录失败，请检查账号密码或网络。")
            return None
        return session
    except Exception as e:
        print(f"⚠️ 登录异常: {e}")
        return None


def _parse_num(val):
    """把含逗号的数字字符串转成 float"""
    try:
        return float(val.replace(',', '').strip())
    except:
        return 0.0


def _pct(a, b, decimals=2):
    """计算百分比，b 为 0 时返回 '-'"""
    if b == 0:
        return "-"
    return f"{round(a/b*100, decimals)}%"


# --- 模式一：业绩排行 ---

def fetch_performance(session, name=None, top_n=5):
    try:
        resp = session.get(PERF_URL, verify=False, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        tables = soup.find_all('table')
        if len(tables) < 2:
            print("❌ 未找到业绩表格")
            return
        results = []
        for row in tables[1].find_all('tr'):
            cells = row.find_all('td')
            if not cells or len(cells) < 13:
                continue
            seq = cells[0].get_text(strip=True)
            if not seq:
                img = cells[0].find('img')
                seq = img['src'].split('/')[-1].replace('.png', '') if img else ''
            name_val = cells[1].get_text(strip=True)
            if name and name.lower() not in name_val.lower():
                continue
            results.append({
                "rank": seq,
                "name": name_val,
                "group": cells[2].get_text(strip=True),
                "value": cells[12].get_text(strip=True).replace(',', '')
            })
        output = results if name else results[:top_n]
        print(f"\n--- 业绩排行榜 ---")
        for r in output:
            print(f"排名 {r['rank']:>3} | {r['name']:<20} | {r['group']:<15} | 业绩: {r['value']}")
    except Exception as e:
        print(f"业绩抓取错误: {e}")


# --- 模式二：通话效率 ---

def fetch_call_data(session, name=None, start_date=None, end_date=None, date_mode=None, top_n=20):
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    if date_mode == 'today':
        post_data, date_label = {"ben_day": "Today"}, today
    elif date_mode == 'yesterday':
        post_data, date_label = {"yesterday": "Yesterday"}, yesterday
    elif date_mode == 'month':
        post_data, date_label = {"ben_month": "本月"}, f"{today[:7]}-01 至 {today}"
    else:
        s, e = start_date or today, end_date or today
        post_data = {"start_date": s, "end_date": e, "group_name": "", "group_list": "", "is_show_group": "y", "": "submit"}
        date_label = f"{s} 至 {e}"

    try:
        resp = session.post(CALL_URL, data=post_data, verify=False, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', {'id': 'salary'})
        if not table:
            print(f"❌ 未找到 {date_label} 的通话数据")
            return
        results = []
        for row in table.find_all('tr')[2:]:
            cells = row.find_all('td')
            if not cells or len(cells) < 12:
                continue
            cc = cells[1].get_text(strip=True)
            if not cc or not re.sub(r'[^a-zA-Z]', '', cc):
                continue
            results.append({
                "cc": cc,
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
            output = sorted(results, key=lambda x: -_parse_num(x['total_duration']))[:top_n]
        print(f"\n--- 通话效率统计 ({date_label}) ---")
        for r in output:
            print(f"CC: {r['cc']:<20} | 时长: {r['total_duration']:>7}min | 首次: {r['first_call']:<8} | "
                  f"次数: {r['total_calls']:>3} | 有效率: {r['eff_rate']}")
        if not output:
            print("未找到匹配的通话记录")
    except Exception as e:
        print(f"通话数据抓取错误: {e}")


# --- 模式三：综合运营（含团队/个人总计）---

def fetch_static(session, name=None, team=None, start_date=None, end_date=None, date_mode=None):
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    if date_mode == 'today':
        post_data, date_label = {"ben_day": "今天"}, today
    elif date_mode == 'yesterday':
        post_data, date_label = {"yesterday": "昨天"}, yesterday
    elif date_mode == 'month':
        post_data, date_label = {"ben_month": "本月"}, f"{today[:7]}-01 至 {today}"
    else:
        s, e = start_date or '2026-04-01', end_date or today
        post_data = {"start_date": s, "end_date": e, "all_user": "", "group_name": "",
                    "group_list": "", "is_show_group": "y", "xk": "en", "": "搜索"}
        date_label = f"{s} 至 {e}"

    # 个人筛选时关掉团队聚合
    show_group = 'n' if name else 'y'
    post_data['is_show_group'] = show_group
    if name:
        post_data['all_user'] = name

    try:
        resp = session.post(STATIC_URL, data=post_data, verify=False, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', {'id': 'salary'})
        if not table:
            print(f"❌ 未找到 {date_label} 的数据")
            return

        results = []
        for row in table.find_all('tr')[2:]:
            cells = row.find_all('td')
            if not cells or len(cells) < 20:
                continue
            cc = cells[1].get_text(strip=True)
            if not cc or cc in ('总计',):
                continue
            results.append({
                "cc": cc,
                "new_pay": cells[5].get_text(strip=True),        # 新付费金额(RMB)
                "order_usd": cells[6].get_text(strip=True),        # 订单金额(USD)
                "referral_pay": cells[7].get_text(strip=True),     # 新付费金额(转介绍)
                "referral_orders": cells[8].get_text(strip=True),  # 转介绍总单量
                "referral_order_usd": cells[9].get_text(strip=True),  # 转介绍订单付款金额(USD)
                "attend": cells[12].get_text(strip=True),         # 出席数
                "leads": cells[13].get_text(strip=True),           # Leads总数
                "mkt_leads": cells[14].get_text(strip=True),       # MKT leads
                "referral_leads": cells[15].get_text(strip=True),  # 转介绍leads
                "paid_num": cells[17].get_text(strip=True),        # 付费人数
                "paid_usd": cells[19].get_text(strip=True),        # 付费人数(USD门槛)
            })

        if not results:
            print(f"❌ 未找到 {date_label} 的数据")
            return

        print(f"\n--- 综合运营数据 ({date_label}) ---")
        print(f"{'排名':<4} {'CC/团队':<22} {'新付费(RMB)':>12} {'订单(USD)':>10} "
              f"{'出席数':>6} {'Leads':>6} {'MKT':>5} {'转介leads':>7} {'付费人数':>6}")
        print("-" * 90)
        for i, r in enumerate(results, 1):
            print(f"{i:<4} {r['cc']:<22} {r['new_pay']:>12} {r['order_usd']:>10} "
                  f"{r['attend']:>6} {r['leads']:>6} {r['mkt_leads']:>5} "
                  f"{r['referral_leads']:>7} {r['paid_num']:>6}")
    except Exception as e:
        print(f"综合数据抓取错误: {e}")


# --- 模式四：体验课跟进 ---

def fetch_info(session, name=None, start_date=None, end_date=None, date_mode=None, top_n=30):
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    if date_mode == 'today':
        post_data, date_label = {"ben_day": "今天"}, today
    elif date_mode == 'yesterday':
        post_data, date_label = {"yesterday": "昨天"}, yesterday
    elif date_mode == 'week':
        post_data, date_label = {"ben_week": "7天"}, f"{today[:7]}-01 至 {today}"
    elif date_mode == 'month':
        post_data, date_label = {"ben_month": "本月"}, f"{today[:7]}-01 至 {today}"
    else:
        s, e = start_date or today, end_date or today
        post_data = {"start_date": s, "end_date": e, "group_name": "", "group_list": "", "is_show_group": "y", "": "搜索"}
        date_label = f"{s} 至 {e}"

    try:
        resp = session.post(INFO_URL, data=post_data, verify=False, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        tables = soup.find_all('table')
        table = tables[2] if len(tables) > 2 else None
        if not table:
            print(f"❌ 未找到 {date_label} 的体验课跟进数据")
            return

        results = []
        for row in table.find_all('tr')[2:]:
            cells = row.find_all('td')
            if not cells or len(cells) < 13:
                continue
            cc = cells[1].get_text(strip=True)
            if not cc:
                continue
            pre_called = cells[3].get_text(strip=True).replace('\xa0', ' ')
            results.append({
                "cc": cc,
                "exp_class": cells[2].get_text(strip=True),
                "pre_called": pre_called,
                "pre_answered": cells[4].get_text(strip=True),
                "pre_not_called": cells[5].get_text(strip=True),
                "post_called": cells[6].get_text(strip=True).replace('\xa0', ' '),
                "post_answered": cells[7].get_text(strip=True),
                "post_not_called": cells[8].get_text(strip=True),
                "post_attend_calls": cells[9].get_text(strip=True),
                "post_no_attend_calls": cells[10].get_text(strip=True),
                "post_attend_answered": cells[11].get_text(strip=True),
                "post_no_attend_answered": cells[12].get_text(strip=True),
            })

        if name:
            output = [r for r in results if name.lower() in r["cc"].lower()]
        else:
            output = results[:top_n]

        print(f"\n--- 体验课跟进数据 ({date_label}) ---")
        if name and len(output) == 1:
            r = output[0]
            print(f"  CC: {r['cc']}")
            print(f"  体验课量: {r['exp_class']}")
            print(f"  课前跟进（打过）: {r['pre_called']}")
            print(f"  课前跟进（打通）: {r['pre_answered']}")
            print(f"  课前未跟进: {r['pre_not_called']}")
            print(f"  课后跟进（打过）: {r['post_called']}")
            print(f"  课后跟进（打通）: {r['post_answered']}")
            print(f"  课后未跟进: {r['post_not_called']}")
            print(f"  课后出席拨打量: {r['post_attend_calls']} / 拨通量: {r['post_attend_answered']}")
            print(f"  课后未出席拨打量: {r['post_no_attend_calls']} / 拨通量: {r['post_no_attend_answered']}")
        else:
            print(f"{'排名':<4} {'CC':<22} {'体验课':>5} {'课前跟进(打过)':>16} {'课前打通':>10} "
                  f"{'课后跟进(打过)':>16} {'课后打通':>10}")
            print("-" * 90)
            for i, r in enumerate(output, 1):
                pc = re.search(r'/(\d+)', r['pre_called'])
                pc = pc.group(1) if pc else '-'
                poc = re.search(r'/(\d+)', r['post_called'])
                poc = poc.group(1) if poc else '-'
                pr = re.sub(r'/[\d]+', '', r['pre_called']).strip()
                por = re.sub(r'/[\d]+', '', r['post_called']).strip()
                print(f"{i:<4} {r['cc']:<22} {r['exp_class']:>5} "
                      f"{pr:>10} /{pc:<4} {r['pre_answered']:>10} "
                      f"{por:>10} /{poc:<4} {r['post_answered']:>10}")
        if not output:
            print("未找到匹配的记录")
    except Exception as e:
        print(f"体验课跟进数据抓取错误: {e}")


# --- 模式五（新增）：转化率分析 ---

def fetch_conversion(session, name=None, team=None, start_date=None, end_date=None, date_mode=None, top_n=30):
    """
    转化率分析（custom_static_cc.php 个人粒度）

    计算公式：
      市场转化率 = (付费人数 - 转介绍总单量) / MKT leads
      转介绍转化率 = 转介绍总单量 / 转介绍leads
      转介绍占比 = 转介绍订单付款金额(USD) / 新付费金额(RMB)

    支持：
      - 查询某人：python crm_tool.py conv Bell
      - 查询某团队：python crm_tool.py conv --team TH-CC01Team
      - 日期筛选：today / yesterday / month / 自定义日期
    """
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    if date_mode == 'today':
        post_data, date_label = {"ben_day": "今天"}, today
    elif date_mode == 'yesterday':
        post_data, date_label = {"yesterday": "昨天"}, yesterday
    elif date_mode == 'month':
        post_data, date_label = {"ben_month": "本月"}, f"{today[:7]}-01 至 {today}"
    else:
        s, e = start_date or '2026-04-01', end_date or today
        post_data = {"start_date": s, "end_date": e, "all_user": "", "group_name": "",
                    "group_list": "", "is_show_group": "y", "xk": "en", "": "搜索"}
        date_label = f"{s} 至 {e}"

    # 个人筛选
    if name:
        post_data['is_show_group'] = 'n'
        post_data['all_user'] = name
    elif team:
        post_data['is_show_group'] = 'y'
        post_data['group_list'] = team
    else:
        post_data['is_show_group'] = 'n'

    try:
        resp = session.post(STATIC_URL, data=post_data, verify=False, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', {'id': 'salary'})
        if not table:
            print(f"❌ 未找到 {date_label} 的数据")
            return

        results = []
        for row in table.find_all('tr')[2:]:
            cells = row.find_all('td')
            if not cells or len(cells) < 20:
                continue
            cc = cells[1].get_text(strip=True)
            if not cc or cc in ('总计',):
                continue

            paid_num   = _parse_num(cells[17].get_text(strip=True))  # 付费人数
            ref_orders = _parse_num(cells[8].get_text(strip=True))   # 转介绍总单量
            mkt        = _parse_num(cells[14].get_text(strip=True))   # MKT leads
            ref_leads  = _parse_num(cells[15].get_text(strip=True))   # 转介绍leads
            new_pay    = _parse_num(cells[5].get_text(strip=True))    # 新付费金额(RMB)
            ref_usd    = _parse_num(cells[9].get_text(strip=True))   # 转介绍订单付款金额(USD)

            # 计算转化率
            mkt_conv   = _pct(paid_num - ref_orders, mkt)
            ref_conv   = _pct(ref_orders, ref_leads)
            ref_ratio  = _pct(ref_usd, new_pay)

            results.append({
                "cc": cc,
                "new_pay": cells[5].get_text(strip=True),
                "paid_num": cells[17].get_text(strip=True),
                "paid_num_raw": paid_num,
                "ref_orders": cells[8].get_text(strip=True),
                "ref_orders_raw": ref_orders,
                "mkt": cells[14].get_text(strip=True),
                "mkt_raw": mkt,
                "ref_leads": cells[15].get_text(strip=True),
                "ref_leads_raw": ref_leads,
                "ref_usd": cells[9].get_text(strip=True),
                "mkt_conv": mkt_conv,
                "ref_conv": ref_conv,
                "ref_ratio": ref_ratio,
            })

        if not results:
            print(f"❌ 未找到 {date_label} 的数据")
            return

        print(f"\n{'='*100}")
        print(f"  转化率分析 ({date_label})")
        print(f"{'='*100}")
        print(f"{'排名':<4} {'CC/团队':<22} {'新付费(RMB)':>12} {'付费人数':>6} "
              f"{'转介单':>5} {'MKT':>5} {'转介leads':>7} "
              f"{'市场转化率':>10} {'转介转化率':>10} {'转介占比':>9}")
        print("-" * 100)
        for i, r in enumerate(results, 1):
            print(f"{i:<4} {r['cc']:<22} {r['new_pay']:>12} {r['paid_num']:>6} "
                  f"{r['ref_orders']:>5} {r['mkt']:>5} {r['ref_leads']:>7} "
                  f"{r['mkt_conv']:>10} {r['ref_conv']:>10} {r['ref_ratio']:>9}")

        # 单人详情模式
        if name and len(results) == 1:
            r = results[0]
            print(f"\n  公式说明：")
            print(f"  市场转化率 = (付费人数 - 转介单量) / MKT leads = ({r['paid_num']} - {r['ref_orders']}) / {r['mkt']} = {r['mkt_conv']}")
            print(f"  转介转化率 = 转介单量 / 转介leads = {r['ref_orders']} / {r['ref_leads']} = {r['ref_conv']}")
            print(f"  转介占比  = 转介订单USD / 新付费RMB = {r['ref_usd']} / {r['new_pay']} ≈ {r['ref_ratio']}")

    except Exception as e:
        print(f"转化率数据抓取错误: {e}")


# --- 命令行入口 ---

QUICK = ['today', 'yesterday', 'week', 'month']

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "perf"
    arg2 = sys.argv[2] if len(sys.argv) > 2 else None
    arg3 = sys.argv[3] if len(sys.argv) > 3 else None
    arg4 = sys.argv[4] if len(sys.argv) > 4 else None

    sess = get_session()
    if not sess:
        exit(1)

    if mode == "perf":
        fetch_performance(sess, name=arg2)
    elif mode == "call":
        if arg2 in QUICK:
            fetch_call_data(sess, date_mode=arg2)
        else:
            name = arg2
            if arg3 in QUICK:
                fetch_call_data(sess, name=name, date_mode=arg3)
            elif arg3 and arg4:
                fetch_call_data(sess, name=name, start_date=arg3, end_date=arg4)
            elif arg3:
                fetch_call_data(sess, name=name, start_date=arg3)
            else:
                fetch_call_data(sess, name=name)
    elif mode == "static":
        if arg2 in QUICK:
            fetch_static(sess, date_mode=arg2)
        elif arg2 and arg3:
            fetch_static(sess, start_date=arg2, end_date=arg3)
        else:
            fetch_static(sess, name=arg2)
    elif mode == "info":
        if arg2 in QUICK:
            fetch_info(sess, date_mode=arg2)
        else:
            name = arg2
            if arg3 in QUICK:
                fetch_info(sess, name=name, date_mode=arg3)
            elif arg3 and arg4:
                fetch_info(sess, name=name, start_date=arg3, end_date=arg4)
            elif arg3:
                fetch_info(sess, name=name, start_date=arg3)
            else:
                fetch_info(sess, name=name)
    elif mode == "conv":
        # conv [姓名] [日期快捷词/开始日期 结束日期]
        # conv --team TH-CC01Team [日期]
        if arg2 == '--team':
            team_name = arg3
            date_arg = arg4 if arg4 in QUICK else None
            if date_arg:
                fetch_conversion(sess, team=team_name, date_mode=date_arg)
            elif arg4 and arg5:
                fetch_conversion(sess, team=team_name, start_date=arg4, end_date=arg5)
            else:
                fetch_conversion(sess, team=team_name)
        else:
            name = arg2 if arg2 and arg2 not in QUICK else None
            if arg2 in QUICK:
                fetch_conversion(sess, date_mode=arg2)
            elif arg3 in QUICK:
                fetch_conversion(sess, name=name, date_mode=arg3)
            elif arg3 and arg4:
                fetch_conversion(sess, name=name, start_date=arg3, end_date=arg4)
            else:
                fetch_conversion(sess, name=name)
    else:
        print("未知模式: perf / call / static / info / conv")
        print("输入 'python crm_tool.py' 查看帮助")
