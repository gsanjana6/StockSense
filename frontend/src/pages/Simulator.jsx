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
  Cell,
} from "recharts";

function Simulator() {
  const {
    simulationLoading,
    simulationError,
    simulationResult,
    handleAdvancedSimulation,
  } = useOutletContext();

  const [changes, setChanges] = useState([
    {
      ticker: "",
      action: "add",
      amount: "",
      amount_type: "dollars",
    },
  ]);

  const [period, setPeriod] = useState("1y");

  const simulation = simulationResult?.simulation;
  const current = simulation?.current;
  const simulated = simulation?.simulated;
  const comparison = simulation?.comparison;

  const tickerColors = [
    "#4169E1",
    "#16A085",
    "#E09F3E",
    "#9B59B6",
    "#E05D6F",
    "#2697B8",
  ];

  const getTickerColor = (ticker) => {
    const tickers = Object.keys(simulated?.correlation_matrix || {});
    const index = tickers.indexOf(ticker);

    return tickerColors[
      (index >= 0 ? index : 0) % tickerColors.length
    ];
  };

  const formatDateOnly = (date) => {
    if (!date) return "--";

    const parsed = new Date(date);

    if (Number.isNaN(parsed.getTime())) return date;

    return parsed.toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      timeZone: "UTC",
    });
  };

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
      {
        ticker: "",
        action: "add",
        amount: "",
        amount_type: "dollars",
      },
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
      amount_type: change.amount_type,
      ...(change.action !== "remove"
        ? { amount: Number(change.amount) }
        : {}),
    }));

    if (
      validChanges.some(
        (change) =>
          !change.ticker ||
          (change.action !== "remove" &&
            (!Number.isFinite(change.amount) ||
              change.amount <= 0))
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

  const formatMetric = (value, suffix = "") => {
    if (!Number.isFinite(Number(value))) return "--";

    const formatted = Number(value).toFixed(2);

    if (suffix === "$") return `$${formatted}`;
    if (suffix === "%") return `${formatted}%`;

    return formatted;
  };

  const riskContributionData = simulated?.risk_contributions
    ? Object.entries(simulated.risk_contributions).map(
        ([ticker, data]) => ({
          ticker,
          risk: Number(
            data.percentage_risk_contribution ?? 0
          ),
        })
      )
    : [];

  const scatterData = simulated?.risk_return_scatter || [];

  return (
    <div className="feature-page simulator-page">
      {/* PAGE INTRODUCTION */}

      <div className="feature-hero">
        <div className="feature-eyebrow">
          ADVANCED WHAT-IF SIMULATOR
        </div>

        <h1>
          Test a different strategy.
          <br />
          <span>
            Understand its risk before making a move.
          </span>
        </h1>

        <p>
          Explore hypothetical investment changes and see how
          they could affect your portfolio's risk and performance.
        </p>
      </div>

      {/* SCENARIO BUILDER */}

      <div className="welcome-card simulator-builder">
        <div className="simulator-section-heading">
          <div>
            <span className="simulator-step">
              SCENARIO BUILDER
            </span>

            <h2>Build Your Scenario</h2>

            <p>
              Add, reduce, or remove holdings using either
              investment amounts or share quantities.
              These changes will not modify your actual portfolio.
            </p>
          </div>
        </div>

        <form onSubmit={submitSimulation}>
          <div className="simulator-change-list">
            {changes.map((change, index) => (
              <div
                className="simulator-change-row"
                key={index}
              >
                <div className="simulator-field">
                  <label>Stock ticker</label>

                  <input
                    type="text"
                    placeholder="e.g. MSFT"
                    value={change.ticker}
                    onChange={(e) =>
                      updateChange(
                        index,
                        "ticker",
                        e.target.value.toUpperCase()
                      )
                    }
                    required
                  />
                </div>

                <div className="simulator-field">
                  <label>Action</label>

                  <select
                    value={change.action}
                    onChange={(e) =>
                      updateChange(
                        index,
                        "action",
                        e.target.value
                      )
                    }
                  >
                    <option value="add">Add investment</option>
                    <option value="reduce">Reduce holding</option>
                    <option value="remove">Remove holding</option>
                  </select>
                </div>

                {change.action !== "remove" && (
                  <>
                    <div className="simulator-field">
                      <label>Input type</label>

                      <select
                        value={change.amount_type}
                        onChange={(e) =>
                          updateChange(
                            index,
                            "amount_type",
                            e.target.value
                          )
                        }
                      >
                        <option value="dollars">
                          Investment amount ($)
                        </option>

                        <option value="shares">
                          Number of shares
                        </option>
                      </select>
                    </div>

                    <div className="simulator-field">
                      <label>
                        {change.amount_type === "shares"
                          ? "Share quantity"
                          : "Investment amount"}
                      </label>

                      <input
                        type="number"
                        min="0.01"
                        step="any"
                        placeholder={
                          change.amount_type === "shares"
                            ? "e.g. 5 shares"
                            : "e.g. 1000"
                        }
                        value={change.amount}
                        onChange={(e) =>
                          updateChange(
                            index,
                            "amount",
                            e.target.value
                          )
                        }
                        required
                      />
                    </div>
                  </>
                )}

                {changes.length > 1 && (
                  <button
                    type="button"
                    className="simulator-remove-row"
                    onClick={() => removeChange(index)}
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}
          </div>

          <button
            type="button"
            className="secondary-button simulator-add-button"
            onClick={addChange}
          >
            + Add another change
          </button>

          <div className="simulator-settings">
            <div className="simulator-benchmark">
              <span>BENCHMARK</span>
              <strong>S&P 500 (SPY)</strong>
            </div>

            <div className="simulator-field simulator-period">
              <label>Analysis period</label>

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

          <div className="simulator-submit-area">
            <button
              type="submit"
              className="primary-button simulator-run-button"
              disabled={simulationLoading}
            >
              {simulationLoading
                ? "Running simulation..."
                : "Run Advanced Simulation →"}
            </button>
          </div>
        </form>

        {simulationError && (
          <div
            className="error-message"
            style={{ marginTop: "15px" }}
          >
            {simulationError}
          </div>
        )}
      </div>

      {/* SIMULATION RESULTS */}

      {simulation && current && simulated && (
        <>
          {/* CURRENT VS SIMULATED */}

          <div className="welcome-card">
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
                    const difference = after - before;

                    return (
                      <tr key={key}>
                        <td>
                          <strong>{label}</strong>
                        </td>

                        <td>{formatMetric(before, suffix)}</td>

                        <td>{formatMetric(after, suffix)}</td>

                        <td
                          className={
                            difference >= 0
                              ? "ss-positive"
                              : "ss-negative"
                          }
                        >
                          {formatMetric(difference, suffix)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* KPI CARDS */}

          <div
            className="feature-grid"
            style={{ marginTop: "24px" }}
          >
            <div className="feature-card">
              <h3>Investment Value Change</h3>
              <h2>
                $
                {Number(
                  comparison?.investment_value_change ?? 0
                ).toFixed(2)}
              </h2>
            </div>

            <div className="feature-card">
              <h3>Return Change</h3>
              <h2>
                {Number(
                  comparison?.return_change ?? 0
                ).toFixed(2)}
                %
              </h2>
            </div>

            <div className="feature-card">
              <h3>Volatility Change</h3>
              <h2>
                {Number(
                  comparison?.volatility_change ?? 0
                ).toFixed(2)}
                %
              </h2>
            </div>

            <div className="feature-card">
              <h3>Sharpe Change</h3>
              <h2>
                {Number(
                  comparison?.sharpe_change ?? 0
                ).toFixed(2)}
              </h2>
            </div>
          </div>

          {/* ALLOCATION AND DRAWDOWN */}

          <div
            className="ss-two-col"
            style={{ marginTop: "24px" }}
          >
            <div className="welcome-card">
              <h2>Portfolio Allocation</h2>

              {Object.entries(simulated.weights || {}).map(
                ([ticker, weight]) => (
                  <div
                    key={ticker}
                    className="ss-risk-row"
                  >
                    <span>{ticker}</span>
                    <strong>
                      {Number(weight).toFixed(2)}%
                    </strong>
                  </div>
                )
              )}
            </div>

            <div className="welcome-card">
              <h2>Drawdown &amp; Recovery</h2>

              <div className="ss-risk-list">
                <div className="ss-risk-row">
                  <span>Maximum Drawdown</span>
                  <strong>
                    {Number(
                      simulated.drawdown_recovery?.max_drawdown ?? 0
                    ).toFixed(2)}%
                  </strong>
                </div>

                <div className="ss-risk-row">
                  <span>Peak Date</span>
                  <strong>
                    {formatDateOnly(
                      simulated.drawdown_recovery?.peak_date
                    )}
                  </strong>
                </div>

                <div className="ss-risk-row">
                  <span>Trough Date</span>
                  <strong>
                    {formatDateOnly(
                      simulated.drawdown_recovery?.trough_date
                    )}
                  </strong>
                </div>

                <div className="ss-risk-row">
                  <span>Recovery Date</span>
                  <strong>
                    {formatDateOnly(
                      simulated.drawdown_recovery?.recovery_date
                    )}
                  </strong>
                </div>

                <div className="ss-risk-row">
                  <span>Recovery Duration</span>
                  <strong>
                    {simulated.drawdown_recovery?.recovery_days != null
                      ? `${simulated.drawdown_recovery.recovery_days} trading days`
                      : "--"}
                  </strong>
                </div>
              </div>
            </div>
          </div>

          {/* RISK CONTRIBUTION */}

          <div
            className="welcome-card"
            style={{ marginTop: "24px" }}
          >
            <h2>Risk Contribution by Holding</h2>

            {riskContributionData.length > 0 ? (
              <div
                style={{
                  width: "100%",
                  height: "320px",
                  marginTop: "16px",
                }}
              >
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={riskContributionData}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                    />

                    <XAxis dataKey="ticker" />

                    <YAxis unit="%" />

                    <Tooltip
                      formatter={(value) =>
                        `${Number(value).toFixed(2)}%`
                      }
                    />

                    <Bar
                      dataKey="risk"
                      name="Risk Contribution"
                      radius={[7, 7, 0, 0]}
                    >
                      {riskContributionData.map((entry) => (
                        <Cell
                          key={entry.ticker}
                          fill={getTickerColor(entry.ticker)}
                        />
                      ))}
                    </Bar>
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
                  {Object.entries(
                    simulated.risk_contributions || {}
                  ).map(([ticker, data]) => (
                    <tr key={ticker}>
                      <td>
                        <strong>{ticker}</strong>
                      </td>

                      <td>
                        {Number(
                          data.marginal_contribution_to_risk
                        ).toFixed(4)}
                      </td>

                      <td>
                        {Number(data.component_risk).toFixed(4)}
                      </td>

                      <td>
                        {Number(
                          data.percentage_risk_contribution
                        ).toFixed(2)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* RISK-RETURN ANALYSIS */}

          <div
            className="welcome-card"
            style={{ marginTop: "24px" }}
          >
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
                      <td>
                        <strong>{item.ticker}</strong>
                      </td>

                      <td>
                        {Number(item.annualized_return).toFixed(2)}%
                      </td>

                      <td>
                        {Number(item.annualized_volatility).toFixed(2)}%
                      </td>

                      <td>
                        {Number(item.weight).toFixed(2)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* CORRELATION MATRIX */}

          <div
            className="welcome-card"
            style={{ marginTop: "24px" }}
          >
            <h2>Correlation Matrix</h2>

            {Object.keys(
              simulated.correlation_matrix || {}
            ).length > 0 ? (
              <div
                style={{
                  overflowX: "auto",
                  marginTop: "20px",
                }}
              >
                <table className="ss-matrix-table">
                  <thead>
                    <tr>
                      <th></th>

                      {Object.keys(
                        simulated.correlation_matrix
                      ).map((ticker) => (
                        <th key={ticker}>{ticker}</th>
                      ))}
                    </tr>
                  </thead>

                  <tbody>
                    {Object.entries(
                      simulated.correlation_matrix
                    ).map(([ticker, values]) => (
                      <tr key={ticker}>
                        <td
                          className="ss-matrix-row-label"
                          style={{
                            backgroundColor: "#eef1ff",
                            color: "#263b70",
                            fontWeight: 700,
                            textAlign: "left",
                          }}
                        >
                          {ticker}
                        </td>

                        {Object.keys(
                          simulated.correlation_matrix
                        ).map((column) => {
                          const value = Number(
                            values?.[column] ?? 0
                          );

                          const isDiagonal = ticker === column;

                          return (
                            <td
                              key={column}
                              style={{
                                backgroundColor: isDiagonal
                                  ? "#f8f9fa"
                                  : "#ffffff",
                                color: "#172033",
                                fontWeight: isDiagonal ? 800 : 400,
                                textAlign: "center",
                                fontVariantNumeric: "tabular-nums",
                              }}
                            >
                              {value.toFixed(2)}
                            </td>
                          );
                        })}
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