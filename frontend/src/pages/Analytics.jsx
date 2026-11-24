import { useOutletContext } from "react-router-dom";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  PieChart,
  Pie,
  Legend,
} from "recharts";
import { CHART_COLORS } from "../utils/dashboardConstants";

function Analytics() {
  const { analytics, exposure, valuation, geographicExposure, geographicError } = useOutletContext();

  const performance = analytics?.performance || {};
  const risk = analytics?.risk || {};
  const diversification = analytics?.diversification || {};
  const correlationMatrix = risk.correlation_matrix || {};

  const allocationData = Object.entries(diversification.weights || {}).map(([ticker, weight]) => ({
    name: ticker, value: Number(weight),
  }));

  const exposureData = exposure?.exposure || {};
  const sectorExposure = exposureData.sector_exposure || {};
  const sectorChartData = Object.entries(sectorExposure).map(([sector, weight], index) => ({
    name: sector, value: Number(weight), fill: CHART_COLORS[index % CHART_COLORS.length],
  }));

  const largestSector = exposureData.largest_sector || "--";
  const largestSectorWeight = Number(exposureData.largest_sector_weight || 0);

  const holdings = valuation?.holdings || [];
  const totalValue = Number(valuation?.current_value || 0);

  const returnAttributionData = holdings.map((h) => {
    const weight = totalValue > 0 ? (Number(h.current_value || 0) / totalValue) : 0;
    const individualReturn = Number(h.gain_loss_percentage || 0);

    return {
      ticker: h.ticker,
      return: weight * individualReturn,
    };
  });

  return (
    <div className="feature-page">
      <div className="feature-hero">
        <div className="feature-eyebrow">RISK ANALYTICS</div>
        <h1>Know your risk.<br /><span>Measure your portfolio.</span></h1>
      </div>

      {/* CORE PERFORMANCE METRICS */}
      <div className="feature-grid">
        <div className="feature-card">
          <h3>Sharpe Ratio</h3>
          <h2 style={{marginTop: "10px", fontSize: "2rem"}}>{Number(performance.sharpe_ratio ?? 0).toFixed(2)}</h2>
        </div>
        <div className="feature-card">
          <h3>Portfolio Beta</h3>
          <h2 style={{marginTop: "10px", fontSize: "2rem"}}>{Number.isFinite(Number(risk.beta)) ? Number(risk.beta).toFixed(2) : "--"}</h2>
        </div>
        <div className="feature-card">
          <h3>Annualized Volatility</h3>
          <h2 style={{marginTop: "10px", fontSize: "2rem"}}>{Number(performance.annualized_volatility ?? 0).toFixed(2)}%</h2>
        </div>
        <div className="feature-card">
          <h3>Max Drawdown</h3>
          <h2 style={{marginTop: "10px", fontSize: "2rem"}} className="ss-negative">{Number(performance.max_drawdown ?? 0).toFixed(2)}%</h2>
        </div>
      </div>

      {/* RETURN ATTRIBUTION + SECTOR EXPOSURE */}
      <div className="ss-two-col" style={{ marginTop: "24px" }}>
        <div className="welcome-card">
          <h2>Return Attribution by Holding</h2>
          {returnAttributionData.length > 0 ? (
            <div style={{ width: "100%", height: "300px", marginTop: "16px" }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={returnAttributionData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--ss-border-light)" vertical={false} />
                  <XAxis dataKey="ticker" tick={{ fontSize: 12, fill: "var(--ss-text-muted)" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 12, fill: "var(--ss-text-muted)" }} axisLine={false} tickLine={false} unit="%" />
                  <Tooltip formatter={(value) => `${Number(value).toFixed(2)}%`} cursor={{ fill: "var(--ss-surface-soft)" }} />
                  <Bar dataKey="return" radius={[6, 6, 0, 0]}>
                    {returnAttributionData.map((entry, index) => (
                      <Cell key={`return-cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : <p style={{ marginTop: "12px" }}>No holdings to attribute returns to yet.</p>}
        </div>

        <div className="welcome-card">
          <h2>Sector Exposure</h2>
          {sectorChartData.length > 0 ? (
            <>
              <div style={{ width: "100%", height: "220px", marginTop: "12px" }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={sectorChartData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={2}>
                      {sectorChartData.map((entry, index) => (
                        <Cell key={`sector-cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${Number(value).toFixed(2)}%`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="ss-legend-list">
                {sectorChartData.map((entry, index) => (
                  <div key={index} className="ss-legend-item">
                    <span className="ss-legend-dot" style={{ background: entry.fill }} />
                    {entry.name} {entry.value.toFixed(0)}%
                  </div>
                ))}
              </div>
              {largestSectorWeight > 40 && (
                <div className="ss-inline-warning">
                  ⚠ {largestSector} exposure exceeds 40%. Consider rebalancing.
                </div>
              )}
            </>
          ) : <p style={{ marginTop: "12px" }}>Sector exposure data is not available yet.</p>}
        </div>
      </div>

      {/* CORRELATION MATRIX */}
      <div className="welcome-card" style={{marginTop: "24px"}}>
        <h2>Correlation Matrix</h2>
        {Object.keys(correlationMatrix).length > 0 ? (
          <div style={{ overflowX: "auto", marginTop: "16px" }}>
            <table className="ss-matrix-table">
              <thead>
                <tr>
                  <th></th>
                  {Object.keys(correlationMatrix).map((ticker) => (
                    <th key={ticker}>{ticker}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(correlationMatrix).map(([ticker, values]) => (
                  <tr key={ticker}>
                    <td className="ss-matrix-row-label">{ticker}</td>
                    {Object.keys(correlationMatrix).map((column) => (
                      <td key={column} className={column === ticker ? "ss-matrix-diagonal" : ""}>
                        {Number(values?.[column] ?? 0).toFixed(2)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <p>Correlation data is not available yet.</p>}
      </div>

      {/* GEOGRAPHIC EXPOSURE + CONCENTRATION SUMMARY */}
      <div className="ss-two-col" style={{ marginTop: "24px" }}>
        <div className="welcome-card">
          <h2>Geographic Exposure</h2>
          {geographicExposure?.exposure?.length > 0 ? (
            <>
              <div style={{width: "100%", height: "240px", marginTop: "12px"}}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={geographicExposure.exposure.map((item)=>({name:item.country,value:Number(item.weight)}))} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={2}>
                      {geographicExposure.exposure.map((item,index)=>(
                        <Cell key={`country-cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]}/>
                      ))}
                    </Pie>
                    <Tooltip formatter={(value)=>`${Number(value).toFixed(2)}%`}/>
                    <Legend/>
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <p className="ss-text-muted-cell" style={{marginTop: "8px"}}>
                Largest country: <strong>{geographicExposure.largest_country}</strong> ({Number(geographicExposure.largest_country_weight).toFixed(1)}%)
              </p>
            </>
          ) : (
            <div className="ss-chart-placeholder" style={{minHeight: "160px"}}>
              <span className="ss-chart-placeholder-icon">🌍</span>
              <p>{geographicError || "Country data is not available for the current holdings."}</p>
            </div>
          )}
        </div>

        <div className="welcome-card">
          <h2>Concentration Summary</h2>
          <div className="ss-risk-list">
            <div className="ss-risk-row">
              <span>Largest sector</span>
              <strong>{largestSector} {largestSectorWeight > 0 ? `(${largestSectorWeight.toFixed(0)}%)` : ""}</strong>
            </div>
            <div className="ss-risk-row">
              <span>Largest holding</span>
              <strong>{diversification.largest_holding ?? "--"} {diversification.largest_weight ? `(${Number(diversification.largest_weight).toFixed(0)}%)` : ""}</strong>
            </div>
            <div className="ss-risk-row">
              <span>Number of holdings</span>
              <strong>{holdings.length}</strong>
            </div>
            <div className="ss-risk-row">
              <span>Concentration warning</span>
              <strong className={largestSectorWeight > 40 || Number(diversification.largest_weight || 0) > 30 ? "ss-negative" : "ss-positive"}>
                {largestSectorWeight > 40 || Number(diversification.largest_weight || 0) > 30 ? "Yes" : "No"}
              </strong>
            </div>
          </div>
        </div>
      </div>

      {/* PORTFOLIO ALLOCATION PIE CHART */}
      <div className="welcome-card" style={{marginTop: "24px"}}>
        <h2>Full Portfolio Allocation</h2>
        {allocationData.length > 0 ? (
          <div style={{ width: "100%", height: "350px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={allocationData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={110} label>
                  {allocationData.map((entry, index) => (
                    <Cell key={`allocation-cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        ) : <p>Allocation data is not available yet.</p>}
      </div>
    </div>
  );
}

export default Analytics;