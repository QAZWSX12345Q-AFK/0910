import os
import re
import smtplib
import ssl
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header

import akshare as ak
import pandas as pd

FUNDS = ["004102", "004103", "021266"]
FUND_NAME = "中信保诚稳悦债券"


def latest_holdings():
    frames = []
    current_year = datetime.now().year
    for code in FUNDS:
        # Bond holdings are disclosed by reporting period; use the newest
        # available period returned by Eastmoney/AKShare.
        for year in [current_year, current_year - 1]:
            try:
                df = ak.fund_portfolio_bond_hold_em(symbol=code, date=str(year))
                if df is not None and not df.empty:
                    df = df.copy()
                    df["基金代码"] = code
                    frames.append(df)
                    break
            except Exception:
                continue

    if not frames:
        raise RuntimeError("无法获取基金债券持仓数据")

    all_df = pd.concat(frames, ignore_index=True)
    # Prefer the newest disclosed quarter/date when available.
    if "季度" in all_df.columns:
        all_df = all_df.sort_values("季度", ascending=False)
    return all_df


def get_market_quotes():
    quotes = []

    # Exchange-traded bonds: latest price and percentage change.
    try:
        df = ak.bond_zh_hs_spot(start_page="1", end_page="20")
        if df is not None and not df.empty:
            quotes.append(df)
    except Exception:
        pass

    # Interbank cash bond deals: useful as a fallback for government/policy-bank bonds.
    try:
        df = ak.bond_spot_deal()
        if df is not None and not df.empty:
            quotes.append(df)
    except Exception:
        pass

    return quotes


def find_change(name, code, quote_frames):
    clean_name = re.sub(r"[（）()\s]", "", str(name))
    code = str(code).strip()

    # First try exchange quote table by code/name.
    for df in quote_frames:
        cols = set(df.columns)
        if "代码" in cols and "涨跌幅" in cols:
            hit = df[df["代码"].astype(str).str.contains(code, regex=False, na=False)]
            if hit.empty:
                hit = df[df["名称"].astype(str).map(
                    lambda x: clean_name in re.sub(r"[（）()\s]", "", x)
                )]
            if not hit.empty:
                row = hit.iloc[0]
                try:
                    return float(row["涨跌幅"]), "交易所行情"
                except Exception:
                    pass

    # Interbank deal data normally has no percentage change; do not fabricate it.
    for df in quote_frames:
        if "债券简称" in df.columns:
            hit = df[df["债券简称"].astype(str).map(
                lambda x: clean_name in re.sub(r"[（）()\s]", "", x)
                or re.sub(r"[（）()\s]", "", x) in clean_name
            )]
            if not hit.empty:
                return None, "银行间成交行情（无可直接换算的日涨跌幅）"

    return None, "未找到当日价格涨跌幅"


def build_report():
    holdings = latest_holdings()
    quotes = get_market_quotes()

    # Use the latest disclosure and show the top positions by NAV weight.
    if "占净值比例" in holdings.columns:
        holdings["weight"] = pd.to_numeric(holdings["占净值比例"], errors="coerce")
    else:
        holdings["weight"] = pd.to_numeric(holdings.iloc[:, 3], errors="coerce")

    holdings = holdings.dropna(subset=["weight"]).sort_values("weight", ascending=False)
    top = holdings.head(10)

    lines = []
    lines.append(f"{FUND_NAME} 下午监控")
    lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("说明：债券持仓来自最新可获得的公开披露；行情优先使用当日公开价格数据。只有拿到可直接比较的日涨跌幅才计入加权估算，缺失数据不编造。")
    lines.append("")

    weighted = 0.0
    matched_weight = 0.0
    rows = []

    for _, r in top.iterrows():
        name = str(r.get("债券名称", r.get("名称", "")))
        code = str(r.get("债券代码", r.get("代码", "")))
        weight = float(r["weight"])
        chg, source = find_change(name, code, quotes)
        contribution = None
        if chg is not None:
            contribution = weight / 100.0 * chg
            weighted += contribution
            matched_weight += weight
        rows.append((name, code, weight, chg, contribution, source))

    lines.append("主要债券持仓：")
    lines.append("债券 | 代码 | 权重 | 当日涨跌 | 收益贡献 | 数据")
    lines.append("---|---|---:|---:|---:|---")
    for name, code, weight, chg, contribution, source in rows:
        chg_s = f"{chg:+.3f}%" if chg is not None else "—"
        con_s = f"{contribution:+.4f}%" if contribution is not None else "—"
        lines.append(f"{name} | {code} | {weight:.2f}% | {chg_s} | {con_s} | {source}")

    lines.append("")
    if matched_weight > 0:
        lines.append(f"可计算权重：{matched_weight:.2f}%")
        lines.append(f"已匹配持仓的加权收益贡献：{weighted:+.4f}%")
        lines.append("注意：这不是基金官方当日净值收益率，只是基于已匹配持仓价格变动的估算。")
    else:
        lines.append("今日没有获得足够的可直接比较债券价格数据，因此不输出伪造的基金收益估算。")

    return "\n".join(lines)


def send_email(body):
    sender = os.environ.get("QQ_EMAIL")
    auth_code = os.environ.get("QQ_AUTH_CODE")
    if not sender or not auth_code:
        raise RuntimeError("缺少 GitHub Secrets：QQ_EMAIL / QQ_AUTH_CODE")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header("中信保诚稳悦债券｜下午监控", "utf-8")
    msg["From"] = sender
    msg["To"] = sender

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.qq.com", 465, context=context, timeout=30) as server:
        server.login(sender, auth_code)
        server.sendmail(sender, [sender], msg.as_string())


if __name__ == "__main__":
    report = build_report()
    print(report)
    send_email(report)
