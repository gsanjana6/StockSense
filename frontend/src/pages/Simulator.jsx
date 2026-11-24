import { useOutletContext } from "react-router-dom";
import { useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Bar,
} from "recharts";

function Simulator() {
  const {
    simulationLoading,
    simulationError,
    simulationResult,
    handleAdvancedSimulation,
  } = useOutletContext();

  const [changes, setChanges] = useState([
    { ticker: "", action: "add", amount: "" },
  ]);
  const [period, setPeriod] = useState("1y");

  const simulation = simulationResult?.simulation;
  const current = simulation?.current;
  const simulated = simulation?.simulated;
  const comparison = simulation?.comparison;

  const updateChange = (index, field, value) => {
    setChanges((previous) =>
      previous.map((change, i) =>
        i === index ? { ...change, [field]: value } : change
      )
    );
  };

  const addChange = () => {
    setChanges((previous) => [
      ...previous,
      { ticker: "", action: "add", amount: "" },
    ]);
  };

  const removeChange = (index) => {
    setChanges((previous) =>
      previous.filter((_, i) => i !== index)
    );
  };

  const submitSimulation = (e) => {
    e.preventDefault();

    const validChanges = changes.map((change) => ({
      ticker: change.ticker.trim().toUpperCase(),
      action: change.action,
      ...(change.action !== "remove"
        ? { amount: Number(change.amount) }
        : {}),
    }));

    if (
      validChanges.some(
        (change) =>
          !change.ticker ||
          (change.action !== "remove" &&
            (!Number.isFinite(change.amount) || change.amount <= 0))
      )
    ) {
      return;
    }

    handleAdvancedSimulation({
      changes: validChanges,
      benchmark: "SPY",
      period,
    });
  };

  const comparisonRows = [
    ["Portfolio Value", "total_value", "$"],
    ["Annualized Return", "annualized_return", "%"],
    ["Annualized Volatility", "annualized_volatility", "%"],
    ["Sharpe Ratio", "sharpe_ratio", ""],
    ["Beta", "beta", ""],
    ["Maximum Drawdown", "max_drawdown", "%"],
    ["Concentration Index", "concentration_index", ""],
    ["Effective Holdings", "effective_holdings", ""],
  ];

  const formatMetric = (value, suffix = "") =>
    Number.isFinite(Number(value))
      ? `${suffix === "$" ? "$" : ""}${Number(value).toFixed(2)}${suffix === "%" ? "%" : ""}`
      : "--";

  const riskContributionData = simulated?.risk_contributions
    ? Object.entries(simulated.risk_contributions).map(([ticker, data]) => ({
        ticker,
        risk: Number(data.percentage_risk_contribution ?? 0),
      }))
    : [];

  const scatterData = simulated?.risk_return_scatter || [];

  return (
    <div className="feature-page">
      <div className="feature-hero">
        <div className="feature-eyebrow">ADVANCED WHAT-IF SIMULATOR</div>
        <h1>
          Test a different strategy.
          <br />
          <span>Understand its risk before making a move.</span>
        </h1>
      </div>

      <div className="welcome-card" style={{ marginTop: "24px" }}>
        <h2>Build Your Scenario</h2>
        <p style={{ marginBottom: "20px" }}>
          Add, reduce, or remove holdings using investment amounts.
          These changes are hypothetical and do not modify your actual portfolio.
        </p>

        <form onSubmit={submitSimulation}>
          {changes.map((change, index) => (
            <div
              key={index}
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
                gap: "12px",
                marginBottom: "14px",
                alignItems: "center",
              }}
            >
              <input
                type="text"
                placeholder="Ticker e.g. NVDA"
                value={change.ticker}
                onChange={(e) =>
                  updateChange(index, "ticker", e.target.value.toUpperCase())
                }
                required
              />

              <select
                value={change.action}
                onChange={(e) =>
                  updateChange(index, "action", e.target.value)
                }
              >
                <option value="add">Add investment</option>
                <option value="reduce">Reduce investment</option>
                <option value="remove">Remove holding</option>
              </select>

              {change.action !== "remove" && (
                <input
                  type="number"
                  min="0.01"
                  step="any"
                  placeholder="Amount ($)"
                  value={change.amount}
                  onChange={(e) =>
                    updateChange(index, "amount", e.target.value)
                  }
                  required
                />
              )}

              {changes.length > 1 && (
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => removeChange(index)}
                >
                  Remove row
                </button>
              )}
            </div>
          ))}

          <button
            type="button"
            className="secondary-button"
            onClick={addChange}
            style={{ marginBottom: "20px" }}
          >
            + Add another change
          </button>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: "14px",
              marginBottom: "20px",
            }}
          >
            <div>
              <label>Benchmark</label>
              <p><strong>S&P 500 (SPY)</strong></p>
            </div>

            <div>
              <label>Analysis Period</label>
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
              >
                <option value="1y">1 Year</option>
                <option value="2y">2 Years</option>
                <option value="5y">5 Years</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            className="primary-button"
            disabled={simulationLoading}
          >
            {simulationLoading ? "Running simulation..." : "Run Advanced Simulation"}
          </button>
        </form>

        {simulationError && (
          <div className="error-message" style={{ marginTop: "15px" }}>
            {simulationError}
          </div>
        )}
      </div>

      {simulation && current && simulated && (
        <>
          <div className="welcome-card" style={{ marginTop: "24px" }}>
            <h2>Current vs Simulated Portfolio</h2>
            <div style={{ overflowX: "auto", marginTop: "16px" }}>
              <table className="ss-holdings-table">
                <thead>
                  <tr>
                    <th>Metric</th>
                    <th>Current</th>
                    <th>Simulated</th>
                    <th>Change</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonRows.map(([label, key, suffix]) => {
                    const before = Number(current[key] ?? 0);
                    const after = Number(simulated[key] ?? 0);

                    return (
                      <tr key={key}>
                        <td><strong>{label}</strong></td>
                        <td>{formatMetric(before, suffix)}</td>
                        <td>{formatMetric(after, suffix)}</td>
                        <td className={after >= before ? "ss-positive" : "ss-negative"}>
                          {formatMetric(after - before, suffix)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="feature-grid" style={{ marginTop: "24px" }}>
            <div className="feature-card">
              <h3>Investment Value Change</h3>
              <h2 style={{ marginTop: "10px" }}>
                ${Number(comparison?.investment_value_change ?? 0).toFixed(2)}
              </h2>
            </div>
            <div className="feature-card">
              <h3>Return Change</h3>
              <h2 style={{ marginTop: "10px" }}>
                {Number(comparison?.return_change ?? 0).toFixed(2)}%
              </h2>
            </div>
            <div className="feature-card">
              <h3>Volatility Change</h3>
              <h2 style={{ marginTop: "10px" }}>
                {Number(comparison?.volatility_change ?? 0).toFixed(2)}%
              </h2>
            </div>
            <div className="feature-card">
              <h3>Sharpe Change</h3>
              <h2 style={{ marginTop: "10px" }}>
                {Number(comparison?.sharpe_change ?? 0).toFixed(2)}
              </h2>
            </div>
          </div>

          <div className="ss-two-col" style={{ marginTop: "24px" }}>
            <div className="welcome-card">
              <h2>Portfolio Allocation</h2>
              {Object.entries(simulated.weights || {}).map(([ticker, weight]) => (
                <div key={ticker} className="ss-risk-row">
                  <span>{ticker}</span>
                  <strong>{Number(weight).toFixed(2)}%</strong>
                </div>
              ))}
            </div>

            <div className="welcome-card">
              <h2>Drawdown &amp; Recovery</h2>
              <div className="ss-risk-list">
                <div className="ss-risk-row">
                  <span>Maximum Drawdown</span>
                  <strong>{Number(simulated.drawdown_recovery?.max_drawdown ?? 0).toFixed(2)}%</strong>
                </div>
                <div className="ss-risk-row">
                  <span>Peak Date</span>
                  <strong>{simulated.drawdown_recovery?.peak_date || "--"}</strong>
                </div>
                <div className="ss-risk-row">
                  <span>Trough Date</span>
                  <strong>{simulated.drawdown_recovery?.trough_date || "--"}</strong>
                </div>
                <div className="ss-risk-row">
                  <span>Recovery Date</span>
                  <strong>{simulated.drawdown_recovery?.recovery_date || "Not recovered"}</strong>
                </div>
                <div className="ss-risk-row">
                  <span>Recovery Duration</span>
                  <strong>
                    {simulated.drawdown_recovery?.recovery_days != null
                      ? `${simulated.drawdown_recovery.recovery_days} days`
                      : "--"}
                  </strong>
                </div>
              </div>
            </div>
          </div>

          <div className="welcome-card" style={{ marginTop: "24px" }}>
            <h2>Risk Contribution by Holding</h2>
            {riskContributionData.length > 0 ? (
              <div style={{ width: "100%", height: "320px", marginTop: "16px" }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={riskContributionData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="ticker" />
                    <YAxis unit="%" />
                    <Tooltip formatter={(value) => `${Number(value).toFixed(2)}%`} />
                    <Bar dataKey="risk" name="Risk Contribution" fill="var(--ss-primary)" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p>Risk contribution data is unavailable.</p>
            )}

            <div style={{ overflowX: "auto" }}>
              <table className="ss-holdings-table">
                <thead>
                  <tr>
                    <th>Holding</th>
                    <th>Marginal Contribution to Risk</th>
                    <th>Component Risk</th>
                    <th>% Risk Contribution</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(simulated.risk_contributions || {}).map(([ticker, data]) => (
                    <tr key={ticker}>
                      <td><strong>{ticker}</strong></td>
                      <td>{Number(data.marginal_contribution_to_risk).toFixed(4)}</td>
                      <td>{Number(data.component_risk).toFixed(4)}</td>
                      <td>{Number(data.percentage_risk_contribution).toFixed(2)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="welcome-card" style={{ marginTop: "24px" }}>
            <h2>Risk-Return Analysis</h2>
            <div style={{ overflowX: "auto", marginTop: "16px" }}>
              <table className="ss-holdings-table">
                <thead>
                  <tr>
                    <th>Holding</th>
                    <th>Annualized Return</th>
                    <th>Annualized Volatility</th>
                    <th>Portfolio Weight</th>
                  </tr>
                </thead>
                <tbody>
                  {scatterData.map((item) => (
                    <tr key={item.ticker}>
                      <td><strong>{item.ticker}</strong></td>
                      <td>{Number(item.annualized_return).toFixed(2)}%</td>
                      <td>{Number(item.annualized_volatility).toFixed(2)}%</td>
                      <td>{Number(item.weight).toFixed(2)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="welcome-card" style={{ marginTop: "24px" }}>
            <h2>Correlation Matrix</h2>
            {Object.keys(simulated.correlation_matrix || {}).length > 0 ? (
              <div style={{ overflowX: "auto", marginTop: "16px" }}>
                <table className="ss-matrix-table">
                  <thead>
                    <tr>
                      <th></th>
                      {Object.keys(simulated.correlation_matrix).map((ticker) => (
                        <th key={ticker}>{ticker}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(simulated.correlation_matrix).map(([ticker, values]) => (
                      <tr key={ticker}>
                        <td className="ss-matrix-row-label">{ticker}</td>
                        {Object.keys(simulated.correlation_matrix).map((column) => (
                          <td key={column}>
                            {Number(values?.[column] ?? 0).toFixed(3)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p>Correlation data is unavailable.</p>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default Simulator;