import { useOutletContext } from "react-router-dom";
import {
  ResponsiveContainer,
  LineChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Line,
} from "recharts";

function Overview() {
  const {
    valuation,
    selectedPortfolio,
    portfolios,
    selectedPortfolioId,
    handlePortfolioChange,
    setShowAddHolding,
    setShowCreatePortfolio,
    handleDeleteHolding,
    analytics,
    interpretation,
    recommendations,
    benchmarkHistory,
    benchmarkError,
    dailySummary,
  } = useOutletContext();

  const performance = analytics?.performance || {};
  const risk = analytics?.risk || {};
  const diversification = analytics?.diversification || {};
  const portfolioInterpretation = interpretation?.interpretation;

  const healthScore = Number(
    recommendations?.overall_assessment?.health_score ??
    analytics?.health?.health_score ??
    0
  );

  const healthRating =
    recommendations?.overall_assessment?.rating ??
    analytics?.health?.rating ??
    "--";

  const totalValue = Number(valuation?.current_value || 0);
  const holdings = valuation?.holdings || [];

  const ruleInsights = [
    ...(portfolioInterpretation?.strengths || []).map((text) => ({
      text,
      tone: "good",
      icon: "✓",
    })),
    ...(portfolioInterpretation?.warnings || []).map((text) => ({
      text,
      tone: "warn",
      icon: "!",
    })),
    ...(recommendations?.recommendations || []).map((item) => ({
      text: item?.message || item?.title,
      tone: "tip",
      icon: "★",
    })),
  ]
    .filter((item) => item.text)
    .slice(0, 4);

  const topHoldings = [...holdings]
    .sort(
      (a, b) =>
        Number(b.current_value || 0) -
        Number(a.current_value || 0)
    )
    .slice(0, 5)
    .map((h) => ({
      ...h,
      weight:
        totalValue > 0
          ? (Number(h.current_value || 0) / totalValue) * 100
          : 0,
    }));

  const concentration = Number(
    diversification.concentration_index ?? 0
  );

  const diversificationLabel =
    concentration === 0
      ? "--"
      : concentration <= 0.25
        ? "Good"
        : concentration <= 0.40
          ? "Moderate"
          : "Concentrated";

  const overviewChartData = (
    Array.isArray(benchmarkHistory) ? benchmarkHistory : []
  )
    .map((row) => ({
      date: row.date,
      portfolio: Number(row.portfolio),
      benchmark: Number(row.benchmark),
    }))
    .filter(
      (row) =>
        row.date &&
        Number.isFinite(row.portfolio) &&
        Number.isFinite(row.benchmark)
    );

  return (
    <div className="feature-page">
      <div
        className="portfolio-selector-card"
        style={{ marginBottom: "24px" }}
      >
        <div>
          <h2>Your Portfolio</h2>
          <p>Select and manage your portfolio.</p>
        </div>

        <div className="portfolio-actions">
          <select
            value={selectedPortfolioId}
            onChange={handlePortfolioChange}
          >
            {portfolios.map((portfolio) => (
              <option
                key={portfolio.portfolio_id ?? portfolio.id}
                value={portfolio.portfolio_id ?? portfolio.id}
              >
                {portfolio.name ??
                  portfolio.portfolio_name ??
                  `Portfolio ${portfolio.portfolio_id ?? portfolio.id}`}
              </option>
            ))}
          </select>

          <button
            className="secondary-button"
            onClick={() => setShowAddHolding(true)}
          >
            + Add Holding
          </button>

          <button
            className="primary-button"
            onClick={() => setShowCreatePortfolio(true)}
          >
            + Add Portfolio
          </button>
        </div>
      </div>

      <div className="ss-overview-header">
        <div
          className="feature-hero"
          style={{ marginBottom: 0 }}
        >
          <div className="feature-eyebrow">PORTFOLIO OVERVIEW</div>

          <h1>
            {selectedPortfolio?.name ??
              selectedPortfolio?.portfolio_name ??
              "Your portfolio"},
            <br />
            <span>at a glance.</span>
          </h1>
        </div>

        {(recommendations?.status === "success" || analytics?.health) && (
          <div
            className="ss-health-pill"
            data-rating={String(healthRating).toLowerCase()}
          >
            Health Score <strong>{healthScore.toFixed(0)}/100</strong>
          </div>
        )}
      </div>

      <div className="feature-grid">
        <div className="feature-card">
          <h3>Portfolio Value</h3>
          <h2 style={{ marginTop: "10px", fontSize: "2rem" }}>
            ${totalValue.toFixed(2)}
          </h2>
        </div>

        <div className="feature-card">
          <h3>
            {dailySummary?.isToday
              ? "Today's Gain"
              : "Latest Daily Gain"}
          </h3>

          <h2
            className={
              Number(dailySummary?.gain ?? 0) >= 0
                ? "ss-positive"
                : "ss-negative"
            }
            style={{ marginTop: "10px", fontSize: "2rem" }}
          >
            {dailySummary
              ? `${dailySummary.gain >= 0 ? "+" : "-"}$${Math.abs(dailySummary.gain).toFixed(2)}`
              : "--"}
          </h2>

          {!dailySummary && (
            <span className="ss-metric-pending-note">
              Waiting for at least two portfolio snapshots.
            </span>
          )}
        </div>

        <div className="feature-card">
          <h3>Annual Return</h3>
          <h2 style={{ marginTop: "10px", fontSize: "2rem" }}>
            {Number(performance.annualized_return ?? 0).toFixed(2)}%
          </h2>
        </div>

        <div className="feature-card">
          <h3>Sharpe Ratio</h3>
          <h2 style={{ marginTop: "10px", fontSize: "2rem" }}>
            {Number(performance.sharpe_ratio ?? 0).toFixed(2)}
          </h2>
        </div>
      </div>

      <div className="ss-two-col" style={{ marginTop: "24px" }}>
        <div className="welcome-card">
          <h2>Portfolio vs. S&amp;P 500</h2>

          <div className="ss-chart-legend">
            <span>
              <span
                className="ss-legend-dot"
                style={{ background: "#3157d5" }}
              />
              My Portfolio
            </span>

            <span>
              <span
                className="ss-legend-dot"
                style={{ background: "#12b76a" }}
              />
              S&amp;P 500 (SPY)
            </span>
          </div>

          {overviewChartData.length >= 2 ? (
            <div style={{ width: "100%", height: "300px" }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={overviewChartData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="var(--ss-border-light)"
                    vertical={false}
                  />

                  <XAxis
                    dataKey="date"
                    tick={{
                      fontSize: 11,
                      fill: "var(--ss-text-muted)",
                    }}
                    axisLine={false}
                    tickLine={false}
                  />

                  <YAxis
                    tick={{
                      fontSize: 11,
                      fill: "var(--ss-text-muted)",
                    }}
                    axisLine={false}
                    tickLine={false}
                  />

                  <Tooltip
                    formatter={(value) => Number(value).toFixed(2)}
                  />

                  <Legend />

                  <Line
                    type="monotone"
                    dataKey="portfolio"
                    name="My Portfolio"
                    stroke="#3157d5"
                    strokeWidth={2.5}
                    dot={false}
                  />

                  <Line
                    type="monotone"
                    dataKey="benchmark"
                    name="S&P 500 (SPY)"
                    stroke="#12b76a"
                    strokeWidth={2.5}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="ss-chart-placeholder">
              <span className="ss-chart-placeholder-icon">📈</span>
              <p>
                {benchmarkError ||
                  "At least two benchmark observations are required to render this chart."}
              </p>
            </div>
          )}
        </div>

        <div className="welcome-card">
          <h2>Rule-Based Insights</h2>

          {ruleInsights.length === 0 ? (
            <p style={{ marginTop: "12px" }}>
              Insights will appear once enough data is available.
            </p>
          ) : (
            <div className="ss-pill-list">
              {ruleInsights.map((item, index) => (
                <div
                  key={index}
                  className={`ss-pill ss-pill-${item.tone}`}
                >
                  <span className="ss-pill-icon">{item.icon}</span>
                  <span>{item.text}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="ss-two-col" style={{ marginTop: "24px" }}>
        <div className="welcome-card">
          <h2>Top Holdings</h2>

          {topHoldings.length === 0 ? (
            <p>No holdings in this portfolio yet.</p>
          ) : (
            <table className="ss-holdings-table">
              <thead>
                <tr>
                  <th>Stock</th>
                  <th>Weight</th>
                  <th>Return</th>
                </tr>
              </thead>

              <tbody>
                {topHoldings.map((holding) => (
                  <tr
                    key={
                      holding.holding_id ??
                      holding.id ??
                      holding.ticker
                    }
                  >
                    <td><strong>{holding.ticker}</strong></td>
                    <td>{holding.weight.toFixed(0)}%</td>

                    <td
                      className={
                        Number(holding.gain_loss_percentage || 0) >= 0
                          ? "ss-positive"
                          : "ss-negative"
                      }
                    >
                      {Number(holding.gain_loss_percentage || 0) >= 0
                        ? "+"
                        : ""}
                      {Number(
                        holding.gain_loss_percentage || 0
                      ).toFixed(0)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="welcome-card">
          <h2>Risk Metrics</h2>

          <div className="ss-risk-list">
            <div className="ss-risk-row">
              <span>Beta</span>
              <strong>
                {Number.isFinite(Number(risk.beta))
                  ? Number(risk.beta).toFixed(2)
                  : "--"}
              </strong>
            </div>

            <div className="ss-risk-row">
              <span>Volatility</span>
              <strong>
                {Number(
                  performance.annualized_volatility ?? 0
                ).toFixed(1)}%
              </strong>
            </div>

            <div className="ss-risk-row">
              <span>Max Drawdown</span>
              <strong>
                {Number(performance.max_drawdown ?? 0).toFixed(1)}%
              </strong>
            </div>

            <div className="ss-risk-row">
              <span>Diversification</span>
              <strong>{diversificationLabel}</strong>
            </div>
          </div>
        </div>
      </div>

      <div className="welcome-card" style={{ marginTop: "24px" }}>
        <h2>Your Holdings</h2>

        {!holdings.length ? (
          <p>No holdings in this portfolio yet.</p>
        ) : (
          holdings.map((holding) => (
            <div
              key={
                holding.holding_id ??
                holding.id ??
                holding.ticker
              }
              className="holding-row"
            >
              <strong>{holding.ticker}</strong>
              <span>{holding.quantity} shares</span>
              <span>
                ${Number(holding.current_value || 0).toFixed(2)}
              </span>

              <span
                className={
                  Number(holding.gain_loss_percentage || 0) >= 0
                    ? "ss-positive"
                    : "ss-negative"
                }
              >
                {Number(holding.gain_loss_percentage || 0) >= 0
                  ? "+"
                  : ""}
                {Number(
                  holding.gain_loss_percentage || 0
                ).toFixed(2)}%
              </span>

              {(holding.holding_id || holding.id) && (
                <button
                  className="delete-button"
                  onClick={() =>
                    handleDeleteHolding(
                      holding.holding_id ?? holding.id
                    )
                  }
                >
                  Remove
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Overview;