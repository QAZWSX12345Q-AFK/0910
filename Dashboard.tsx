"use client";

import { useEffect, useMemo, useState } from "react";
import { Plus, RefreshCw, TrendingUp, Wallet, Settings, BarChart3 } from "lucide-react";
import { calcPlan, formatMoney, type FundPlan } from "../../lib/calculator";

const demo: FundPlan[] = [
  {
    id: "demo-1",
    code: "000001",
    name: "华夏成长混合",
    amount: 100,
    frequency: "daily",
    startDate: "2026-01-02",
    enabled: true,
    nav: 1.23,
    shares: 0,
    invested: 0
  }
];

export default function Dashboard() {
  const [plans, setPlans] = useState<FundPlan[]>([]);
  const [showAdd, setShowAdd] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("fund-dca-plans");
    setPlans(saved ? JSON.parse(saved) : demo);
  }, []);

  useEffect(() => {
    if (plans.length) localStorage.setItem("fund-dca-plans", JSON.stringify(plans));
  }, [plans]);

  const summary = useMemo(() => {
    return plans.reduce((s, p) => {
      const x = calcPlan(p);
      s.invested += x.invested;
      s.value += x.value;
      return s;
    }, { invested: 0, value: 0 });
  }, [plans]);

  const profit = summary.value - summary.invested;
  const rate = summary.invested ? profit / summary.invested : 0;

  function addPlan(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const p: FundPlan = {
      id: crypto.randomUUID(),
      code: String(f.get("code") || ""),
      name: String(f.get("name") || "未命名基金"),
      amount: Number(f.get("amount") || 100),
      frequency: String(f.get("frequency") || "daily") as FundPlan["frequency"],
      startDate: String(f.get("startDate") || new Date().toISOString().slice(0, 10)),
      enabled: true,
      nav: Number(f.get("nav") || 1),
      shares: 0,
      invested: 0
    };
    setPlans(x => [...x, p]);
    setShowAdd(false);
    e.currentTarget.reset();
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <div className="eyebrow">FUND DCA</div>
          <h1>基金定投助手</h1>
        </div>
        <button className="iconBtn" title="刷新基金数据"><RefreshCw size={18}/></button>
      </header>

      <section className="heroGrid">
        <div className="heroCard">
          <div className="label">总资产</div>
          <div className="heroNumber">{formatMoney(summary.value)}</div>
          <div className="positive"><TrendingUp size={16}/> {profit >= 0 ? "+" : ""}{formatMoney(profit)} ({(rate*100).toFixed(2)}%)</div>
        </div>
        <div className="metric"><span>累计投入</span><b>{formatMoney(summary.invested)}</b></div>
        <div className="metric"><span>累计收益</span><b className={profit >= 0 ? "positiveText" : "negativeText"}>{profit >= 0 ? "+" : ""}{formatMoney(profit)}</b></div>
        <div className="metric"><span>收益率</span><b>{(rate*100).toFixed(2)}%</b></div>
      </section>

      <section className="sectionHead">
        <div><h2>我的定投</h2><p>每笔投入独立累计，收益自动滚存。</p></div>
        <button className="primary" onClick={() => setShowAdd(true)}><Plus size={17}/> 新增定投</button>
      </section>

      <section className="cards">
        {plans.map(p => {
          const x = calcPlan(p);
          return <article className="planCard" key={p.id}>
            <div className="planTop">
              <div>
                <strong>{p.name}</strong>
                <small>{p.code} · {p.frequency === "daily" ? "每日" : p.frequency === "weekly" ? "每周" : "每月"} ¥{p.amount}</small>
              </div>
              <span className="pill">运行中</span>
            </div>
            <div className="planStats">
              <div><span>累计投入</span><b>{formatMoney(x.invested)}</b></div>
              <div><span>当前估值</span><b>{formatMoney(x.value)}</b></div>
              <div><span>收益</span><b className={x.profit >= 0 ? "positiveText" : "negativeText"}>{x.profit >= 0 ? "+" : ""}{formatMoney(x.profit)}</b></div>
              <div><span>收益率</span><b>{(x.rate*100).toFixed(2)}%</b></div>
            </div>
          </article>
        ))}
      </section>

      <section className="bottomGrid">
        <div className="panel">
          <div className="panelTitle"><BarChart3 size={18}/> 收益分析</div>
          <div className="emptyChart">
            <div>资产曲线</div>
            <p>下一阶段接入历史净值后，这里会显示每日资产、收益和回撤曲线。</p>
          </div>
        </div>
        <div className="panel">
          <div className="panelTitle"><Wallet size={18}/> 下一步</div>
          <ul className="todo">
            <li>接入基金实时/历史净值 API</li>
            <li>自动生成每日定投交易</li>
            <li>计算真实份额、滚存收益和 XIRR</li>
            <li>增加云端数据库和登录</li>
          </ul>
        </div>
      </section>

      <nav className="bottomNav">
        <span className="active">首页</span><span>定投</span><span>基金</span><span>分析</span><span><Settings size={16}/></span>
      </nav>

      {showAdd && <div className="modalBackdrop" onClick={() => setShowAdd(false)}>
        <form className="modal" onSubmit={addPlan} onClick={e => e.stopPropagation()}>
          <h2>新增定投</h2>
          <label>基金代码<input name="code" placeholder="例如 000001" required/></label>
          <label>基金名称<input name="name" placeholder="例如 华夏成长混合" required/></label>
          <label>每次金额<input name="amount" type="number" defaultValue="100" min="1" step="1" required/></label>
          <label>周期<select name="frequency" defaultValue="daily"><option value="daily">每日</option><option value="weekly">每周</option><option value="monthly">每月</option></select></label>
          <label>开始日期<input name="startDate" type="date" defaultValue={new Date().toISOString().slice(0,10)} required/></label>
          <label>初始净值（临时）<input name="nav" type="number" defaultValue="1" min="0.0001" step="0.0001"/></label>
          <div className="modalActions"><button type="button" onClick={() => setShowAdd(false)}>取消</button><button className="primary" type="submit">保存</button></div>
        </form>
      </div>}
    </main>
  );
}