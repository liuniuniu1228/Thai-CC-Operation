import os
import re
import warnings
import requests
import hashlib
from bs4 import BeautifulSoup

warnings.filterwarnings('ignore')

# --- 配置区 ---
CRM_URL = "https://crm.51talk.com/admin/login.php"
DATA_URL = "https://crm.51talk.com/Performance/getSsPreformanceList?type=2"
USER_NAME = "THCC-Panawat"
RAW_PWD = os.getenv("CRM_PWD", "b@2A5qt7")  # 优先从环境变量读取，兜底用默认值


def get_performance(name=None, top_n=5):
    """
    获取 CRM 业绩数据
    name   : 模糊搜索姓名，默认 None（返回前 N 名）
    top_n  : 不指定姓名时返回前几名，默认 5
    """
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
        data_resp = session.get(DATA_URL, verify=False, timeout=15)

        # 6. 解析网页内容
        soup = BeautifulSoup(data_resp.text, 'html.parser')
        tables = soup.find_all('table')

        if len(tables) < 2:
            print("❌ 未能在页面中找到业绩表格。")
            return

        data_table = tables[1]

        # 7. 用 BeautifulSoup 直接提取每个 <tr> 的数据行
        rows = data_table.find_all('tr')
        results = []

        for row in rows:
            cells = row.find_all('td')
            if not cells or len(cells) < 13:
                continue

            # 提取序号（第0格）、姓名（第1格）、小组（第2格）、业绩（第12格）
            # 序号格子里可能是 <img> 也可能是纯数字，需要兼容
            seq_cell = cells[0].get_text(strip=True)
            if not seq_cell:  # 前三名是图片排名
                img = cells[0].find('img')
                seq_cell = img['src'].split('/')[-1].replace('.png', '') if img else ''

            name_cell = cells[1].get_text(strip=True)
            group_cell = cells[2].get_text(strip=True)
            perf_cell = cells[12].get_text(strip=True).replace(',', '')

            if not seq_cell or not name_cell:
                continue

            results.append({
                "序号": seq_cell,
                "姓名": name_cell,
                "小组": group_cell,
                "业绩": perf_cell
            })

        # 8. 根据条件过滤
        if name:
            name_lower = name.lower()
            matched = [r for r in results if name_lower in r["姓名"].lower()]
            output = matched
        else:
            output = results[:top_n]

        # 9. 格式化输出
        if not output:
            print("未找到匹配的业绩数据。")
            return

        for r in output:
            print(f"排名 {r['序号']:>3} | {r['姓名']:<25} | {r['小组']:<15} | 业绩: {r['业绩']}")

        print(f"\n共找到 {len(output)} 条记录")
        return output

    except requests.exceptions.Timeout:
        print("⚠️ 网络超时，请检查网络或 VPN 连接。")
    except requests.exceptions.ConnectionError:
        print("⚠️ 无法连接 CRM，请确认网络或 VPN 状态。")
    except Exception as e:
        print(f"⚠️ 发生错误: {e}")


if __name__ == "__main__":
    import sys
    # 支持命令行参数：python crm_tool.py [姓名]
    target = sys.argv[1] if len(sys.argv) > 1 else None
    get_performance(name=target, top_n=5)
