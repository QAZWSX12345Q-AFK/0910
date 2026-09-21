import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime

import akshare as ak
import pandas as pd

FUND_CODE = "004102"
FUND_NAME = "中信保诚稳悦债券A"
TO_EMAIL = os.environ["REPORT_TO"]
FROM_EMAIL = os.environ["QQ_EMAIL"]
AUTH_CODE = os.environ["QQ_AUTH_CODE"]

# Latest disclosed Q2 2026 top holdings previously identified for this fund.
# The script attempts to refresh holdings from AKShare first; these are the fallback.
FALLBACK_HOLDINGS = [
    ("25超长特别国债02", 33.78),
    ("26超长特别国债02", 20.28),
    ("25国开15", 14.84),
    ("26附息国债02", 12.10),
    ("26超长特别国债03", 4.40),
]

def get_holdings():
    try:
        # AKShare's fund portfolio bond interface can change upstream.
        df = ak.fund_portfolio_bond_hold_em(symbol=FUND_CODE)
        if df is not None and not df.empty:
            cols = list(df.columns)
            name_col = next((c for c in cols if "债券名称" in str(c)), None)
            weight_col = next((c for c in cols if "占净值比例" in str(c)), None)
            if name_col and weight_col:
                rows = []
                for _, r in df.iterrows():
                    try:
                        name = str(r[name_col]).strip()
                        weight = float(r[weight_col])
                        if name and pd.notna(weight):
                            rows.append((name, weight))
                    except Exception:
                        pass
                if rows:
                    return rows[:10], "AKShare"
    except Exception as e:
        print("holdings refresh failed:", repr(e))
    return FALLBACK_HOLDINGS, "Q2 2026 fallback"

def get_exchange_bond_quotes():
    try:
        df = ak.bond_zh_hs_spot()
        if df is None or df.empty:
            return {}
        name_col = next((c for c in df.columns if str(c) in ("名称", "债券名称")), None)
        pct_col = next((c for c in df.columns if "涨跌幅" in str(c)), None)
        if not name_col or not pct_col:
            return {}
        out = {}
        for _, r in df.iterrows():
            try:
                name = str(r[name_col]).strip()
                pct = float(str(r[pct_col]).replace("%", ""))
                out[name] = pct
            except Exception:
                pass
        return out
    except Exception as e:
        print("bond quote refresh failed:", repr(e))
        return {}

def build_report():
    holdings, source = get_holdings()
    quotes = get_exchange_bond_quotes()

    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines.append(f"<h2>中信保诚稳悦债券｜每日监控</h2>")
    lines.append(f"<p>生成时间：{now}</p>")
    lines.append(f"<p>持仓来源：{source}；本报告为<strong>估算</strong>，不是官方基金净值。</p>")
    lines.append("<table border='1' cellpadding='6' cellspacing='0'><tr><th>主要持仓</th><th>权重</th><th>当日涨跌</th><th>估算贡献</th></tr>")

    estimated = 0.0
    for name, weight in holdings:
        pct = quotes.get(name)
        if pct is None:
            change = "暂无可靠行情"
            contrib = "—"
        else:
            change = f"{pct:+.4f}%"
            c = weight / 100.0 * pct
            estimated += c
            contrib = f"{c:+.4f}%"
        lines.append(f"<tr><td>{name}</td><td>{weight:.2f}%</td><td>{change}</td><td>{contrib}</td></tr>")

    lines.append("</table>")
    lines.append(f"<h3>主要持仓加权估算：{estimated:+.4f}%</h3>")
    lines.append("<p>注意：债券基金还包含未列出的债券、现金/存款、应计利息、申赎及费用等因素，因此该数字只能作为盘中/收盘前的方向性估算。若行情接口没有可靠价格，不会用猜测数据填充。</p>")
    return "\n".join(lines), estimated

def send_email(html, estimated):
    subject = f"【稳悦债券监控】{datetime.now():%m-%d} 预计收益 {estimated:+.2f}%"
    msg = MIMEText(html, "html", "utf-8")
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL
    msg["Subject"] = Header(subject, "utf-8")
    with smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=30) as server:
        server.login(FROM_EMAIL, AUTH_CODE)
        server.sendmail(FROM_EMAIL, [TO_EMAIL], msg.as_string())

if __name__ == "__main__":
    html, estimated = build_report()
    send_email(html, estimated)
    print("report sent to", TO_EMAIL)
