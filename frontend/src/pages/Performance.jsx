import { useOutletContext } from "react-router-dom";
import { useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Line,
} from "recharts";
import { TICKER_NAMES } from "../utils/dashboardConstants";

function Performance() {
  const { analytics, valuation, benchmarkHistory, benchmarkError, companies } = useOutletContext();
  const performance = analytics?.performance || {};
  const holdings = valuation?.holdings || [];
  const totalValue = Number(valuation?.current_value || 0);

  const [range, setRange] = useState("1M");

  const rangeCount = range === "1M" ? 21 : range === "3M" ? 63 : 252;
  const chartData = (Array.isArray(benchmarkHistory) ? benchmarkHistory : []).slice(-rangeCount).map((row) => ({ date: row.date, portfolio: Number(row.portfolio), benchmark: Number(row.benchmark) })).filter((row) => row.date && Number.isFinite(row.portfolio) && Number.isFinite(row.benchmark));
  const benchmarkStats = chartData.length >= 2 ? (() => { const first=chartData[0], last=chartData[chartData.length-1]; const portfolioReturn=((last.portfolio/first.portfolio)-1)*100; const benchmarkReturn=((last.benchmark/first.benchmark)-1)*100; return {portfolioReturn,benchmarkReturn,alpha:portfolioReturn-benchmarkReturn}; })() : null;

  const attributionRows = holdings.map((h) => {
    const weight = totalValue > 0 ? (Number(h.current_value || 0) / totalValue) * 100 : 0;
    const individualReturn = Number(h.gain_loss_percentage || 0);
    const contribution = (weight * individualReturn) / 100;
    return {
      ticker: h.ticker,
      company: companies?.[h.ticker] || TICKER_NAMES[h.ticker] || h.ticker,
      weight,
      individualReturn,
      contribution,
    };
  }).sort((a, b) => b.weight - a.weight);

  return (
    <div className="feature-page">
      <div className="feature-hero">
        <div className="feature-eyebrow">PERFORMANCE</div>
        <h1>Portfolio returns<br /><span>benchmarked against the S&amp;P 500.</span></h1>
      </div>

      {/* STAT CARDS */}
      <div className="feature-grid">
        <div className="feature-card">
          <h3>Portfolio Return</h3>
          <h2 className="ss-positive" style={{marginTop: "10px", fontSize: "2rem"}}>
            {Number(valuation?.return_percentage ?? 0) >= 0 ? "+" : ""}
            {Number(valuation?.return_percentage ?? 0).toFixed(1)}%
          </h2>
        </div>
        <div className="feature-card"><h3>S&amp;P 500 Return</h3><h2 className={benchmarkStats ? (benchmarkStats.benchmarkReturn >= 0 ? "ss-positive" : "ss-negative") : ""} style={{marginTop: "10px", fontSize: "2rem"}}>{benchmarkStats ? `${benchmarkStats.benchmarkReturn >= 0 ? "+" : ""}${benchmarkStats.benchmarkReturn.toFixed(1)}%` : "--"}</h2></div>
        <div className="feature-card"><h3>Alpha vs Benchmark</h3><h2 className={benchmarkStats ? (benchmarkStats.alpha >= 0 ? "ss-positive" : "ss-negative") : ""} style={{marginTop: "10px", fontSize: "2rem"}}>{benchmarkStats ? `${benchmarkStats.alpha >= 0 ? "+" : ""}${benchmarkStats.alpha.toFixed(1)}%` : "--"}</h2></div>
        <div className="feature-card">
          <h3>Max Drawdown</h3>
          <h2 className="ss-negative" style={{marginTop: "10px", fontSize: "2rem"}}>
            {Number(performance.max_drawdown ?? 0).toFixed(1)}%
          </h2>
        </div>
      </div>

      {/* CUMULATIVE RETURN CHART */}
      <div className="welcome-card" style={{ marginTop: "24px" }}>
        <div className="ss-chart-header">
          <h2>Cumulative Return vs S&amp;P 500</h2>
          <div className="ss-range-toggle">
            {["1M", "3M", "1Y"].map((label) => (
              <button
                key={label}
                type="button"
                className={range === label ? "ss-range-active" : ""}
                onClick={() => setRange(label)}
              >
                {label === "1M" ? "1 Month" : label === "3M" ? "3 Months" : "1 Year"}
              </button>
            ))}
          </div>
        </div>
        <div className="ss-chart-legend">
          <span><span className="ss-legend-dot" style={{ background: "#3157d5" }} /> My Portfolio</span>
          <span><span className="ss-legend-dot" style={{ background: "#12b76a" }} /> S&amp;P 500 (SPY)</span>
        </div>
        {chartData.length >= 2 ? (
          <div style={{width: "100%", height: "360px", marginTop: "12px"}}><ResponsiveContainer width="100%" height="100%"><LineChart data={chartData}><CartesianGrid strokeDasharray="3 3" stroke="var(--ss-border-light)" vertical={false}/><XAxis dataKey="date" tick={{fontSize: 11, fill: "var(--ss-text-muted)"}} axisLine={false} tickLine={false}/><YAxis tick={{fontSize: 12, fill: "var(--ss-text-muted)"}} axisLine={false} tickLine={false}/><Tooltip formatter={(value)=>Number(value).toFixed(2)}/><Line type="monotone" dataKey="portfolio" name="My Portfolio" stroke="#3157d5" strokeWidth={2.5} dot={false}/><Line type="monotone" dataKey="benchmark" name="S&amp;P 500 (SPY)" stroke="#12b76a" strokeWidth={2.5} dot={false}/></LineChart></ResponsiveContainer></div>
        ) : (
          <div className="ss-chart-placeholder"><span className="ss-chart-placeholder-icon">📈</span><p>{benchmarkError || "At least two benchmark observations are required for this range."}</p></div>
        )}
      </div>

      {/* RETURN ATTRIBUTION TABLE */}
      <div className="welcome-card" style={{ marginTop: "24px" }}>
        <h2>Return Attribution by Holding</h2>
        {attributionRows.length === 0 ? (
          <p style={{ marginTop: "12px" }}>No holdings to attribute returns to yet.</p>
        ) : (
          <div style={{ overflowX: "auto", marginTop: "16px" }}>
            <table className="ss-attribution-table">
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th>Company</th>
                  <th>Weight</th>
                  <th>Individual Return</th>
                  <th>Contribution to Portfolio</th>
                </tr>
              </thead>
              <tbody>
                {attributionRows.map((row) => (
                  <tr key={row.ticker}>
                    <td><strong>{row.ticker}</strong></td>
                    <td className="ss-text-muted-cell">{row.company}</td>
                    <td>{row.weight.toFixed(0)}%</td>
                    <td className={row.individualReturn >= 0 ? "ss-positive" : "ss-negative"}>
                      {row.individualReturn >= 0 ? "+" : ""}{row.individualReturn.toFixed(1)}%
                    </td>
                    <td className={row.contribution >= 0 ? "ss-positive" : "ss-negative"}>
                      {row.contribution >= 0 ? "+" : ""}{row.contribution.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Performance;