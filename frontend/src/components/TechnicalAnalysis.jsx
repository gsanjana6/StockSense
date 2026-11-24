
import { useState } from "react";
import api from "../api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const INDICATORS = [
  { key: "close", label: "Closing Price", color: "#3157d5" },
  { key: "sma_20", label: "SMA 20", color: "#12b76a" },
  { key: "sma_50", label: "SMA 50", color: "#f79009" },
  { key: "sma_200", label: "SMA 200", color: "#7a5af8" },
  { key: "bb_upper", label: "Bollinger Upper", color: "#94a3b8" },
  { key: "bb_lower", label: "Bollinger Lower", color: "#64748b" },
];

function TechnicalAnalysis() {
  const [ticker, setTicker] = useState("AAPL");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [visibleIndicators, setVisibleIndicators] = useState({
    close: true,
    sma_20: true,
    sma_50: true,
    sma_200: true,
    bb_upper: true,
    bb_lower: true,
  });

  const toggleIndicator = (key) => {
    setVisibleIndicators((previous) => ({
      ...previous,
      [key]: !previous[key],
    }));
  };

  const selectAll = () => {
    setVisibleIndicators(
      Object.fromEntries(INDICATORS.map((item) => [item.key, true]))
    );
  };

  const clearAll = () => {
    setVisibleIndicators(
      Object.fromEntries(INDICATORS.map((item) => [item.key, false]))
    );
  };

  const fetchAnalysis = async (e) => {
    e.preventDefault();

    const symbol = ticker.trim().toUpperCase();

    if (!symbol) return;

    setLoading(true);
    setError("");
    setData(null);

    try {
      const response = await api.get(
        `/stocks/${encodeURIComponent(symbol)}/technical-analysis`
      );

      setData(response.data);
    } catch (err) {
      console.error("Technical Analysis error:", err);

      setError(
        err.response?.data?.detail ||
          "Unable to fetch technical analysis."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="feature-page">
      {/* PAGE HEADER */}

      <div className="feature-hero">
        <div className="feature-eyebrow">
          TECHNICAL ANALYSIS
        </div>

        <h1>
          Understand stock trends.
          <br />
          <span>Explore technical indicators.</span>
        </h1>
      </div>

      {/* STOCK SEARCH */}

      <div className="welcome-card">
        <h2>Search a Stock</h2>

        <form
          onSubmit={fetchAnalysis}
          style={{
            display: "flex",
            gap: "12px",
            marginTop: "16px",
          }}
        >
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            placeholder="Enter ticker, e.g. AAPL"
            required
          />

          <button
            type="submit"
            className="primary-button"
            disabled={loading}
          >
            {loading ? "Loading..." : "Analyze"}
          </button>
        </form>

        {error && (
          <p className="error-message" role="alert">
            {typeof error === "string" ? error : JSON.stringify(error)}
          </p>
        )}
      </div>

      {data && (
        <>
          {/* INDICATOR SUMMARY CARDS */}

          <div
            className="feature-grid"
            style={{ marginTop: "24px" }}
          >
            {[
              ["Closing Price", data.current_price],
              ["SMA 20", data.indicators?.sma_20],
              ["SMA 50", data.indicators?.sma_50],
              ["SMA 200", data.indicators?.sma_200],
              ["RSI (14)", data.indicators?.rsi_14],
              ["MACD", data.indicators?.macd],
              ["ATR (14)", data.indicators?.atr_14],
            ].map(([label, value]) => (
              <div className="feature-card" key={label}>
                <h3>{label}</h3>

                <h2 style={{ marginTop: "10px" }}>
                  {value == null ? "--" : Number(value).toFixed(2)}
                </h2>
              </div>
            ))}
          </div>

          {/* STOCK PRICE AND TECHNICAL INDICATORS CHART */}

          <div
            className="welcome-card"
            style={{ marginTop: "24px" }}
          >
            <h2>Stock Price & Technical Indicators</h2>

            <p
              style={{
                marginTop: "8px",
                marginBottom: "20px",
              }}
            >
              Select the indicators you want to display on the chart.
            </p>

            {/* INDICATOR SELECTORS */}

            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                alignItems: "center",
                gap: "10px",
                marginBottom: "22px",
              }}
            >
              {INDICATORS.map((indicator) => {
                const active = visibleIndicators[indicator.key];

                return (
                  <button
                    key={indicator.key}
                    type="button"
                    onClick={() => toggleIndicator(indicator.key)}
                    aria-pressed={active}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "8px",
                      padding: "9px 13px",
                      borderRadius: "9px",
                      border: active
                        ? `1px solid ${indicator.color}`
                        : "1px solid #dfe3ed",
                      background: active ? "#f4f6ff" : "#ffffff",
                      color: active ? "#172033" : "#8992a5",
                      fontSize: "13px",
                      fontWeight: active ? 600 : 400,
                      cursor: "pointer",
                      transition: "all 0.2s ease",
                    }}
                  >
                    <span
                      style={{
                        width: "9px",
                        height: "9px",
                        borderRadius: "50%",
                        background: active
                          ? indicator.color
                          : "#cbd0dc",
                      }}
                    />

                    {indicator.label}
                  </button>
                );
              })}

              <div
                style={{
                  display: "flex",
                  gap: "12px",
                  marginLeft: "auto",
                }}
              >
                <button
                  type="button"
                  onClick={selectAll}
                  style={chartActionStyle}
                >
                  Select all
                </button>

                <button
                  type="button"
                  onClick={clearAll}
                  style={chartActionStyle}
                >
                  Clear all
                </button>
              </div>
            </div>

            {/* CHART */}

            {Array.isArray(data.chart) && data.chart.length > 0 ? (
              <div style={{ width: "100%", height: "380px" }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={data.chart}
                    margin={{
                      top: 10,
                      right: 20,
                      left: 10,
                      bottom: 10,
                    }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="#e5e7eb"
                      vertical={false}
                    />

                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 11 }}
                      minTickGap={35}
                    />

                    <YAxis
                      domain={["auto", "auto"]}
                      tick={{ fontSize: 11 }}
                      width={65}
                    />

                    <Tooltip
                      formatter={(value) =>
                        value == null ? "--" : Number(value).toFixed(2)
                      }
                    />

                    <Legend />

                    {INDICATORS.map((indicator) =>
                      visibleIndicators[indicator.key] ? (
                        <Line
                          key={indicator.key}
                          type="monotone"
                          dataKey={indicator.key}
                          name={indicator.label}
                          stroke={indicator.color}
                          strokeWidth={
                            indicator.key === "close" ? 3 : 2
                          }
                          strokeDasharray={
                            indicator.key.startsWith("bb_")
                              ? "5 5"
                              : undefined
                          }
                          dot={false}
                          connectNulls
                        />
                      ) : null
                    )}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p>Historical chart data is unavailable.</p>
            )}
          </div>

          {/* TECHNICAL INTERPRETATION */}

          <div
            className="welcome-card"
            style={{ marginTop: "24px" }}
          >
            <h2>Technical Interpretation</h2>

            <p
              style={{
                marginTop: "8px",
                color: "#667085",
              }}
            >
              Understand what the technical indicators reveal about the
              stock's recent price behaviour.
            </p>

            {/* OVERALL SUMMARY */}

            <div
              style={{
                marginTop: "20px",
                padding: "18px",
                borderRadius: "12px",
                background: "#f4f6ff",
                border: "1px solid #e0e7ff",
              }}
            >
              <h3 style={{ marginBottom: "8px" }}>
                Overall Analysis
              </h3>

              <p style={{ lineHeight: 1.7 }}>
                {data.interpretation?.overall_summary ||
                  data.interpretation?.explanation ||
                  "No overall interpretation available."}
              </p>
            </div>

            {/* INDIVIDUAL INDICATOR EXPLANATIONS */}

            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "repeat(auto-fit, minmax(240px, 1fr))",
                gap: "14px",
                marginTop: "20px",
              }}
            >
              {[
                {
                  title: "Long-Term Trend",
                  value: data.interpretation?.long_term_trend,
                  explanation:
                    data.interpretation?.long_term_trend_explanation,
                },
                {
                  title: "Moving Average Alignment",
                  value:
                    data.interpretation?.moving_average_alignment,
                  explanation:
                    data.interpretation?.moving_average_explanation,
                },
                {
                  title: "Relative Strength Index (RSI)",
                  value: data.interpretation?.rsi,
                  explanation:
                    data.interpretation?.rsi_explanation,
                },
                {
                  title: "MACD Momentum",
                  value: data.interpretation?.macd,
                  explanation:
                    data.interpretation?.macd_explanation,
                },
                {
                  title: "Volatility (ATR)",
                  value: data.interpretation?.volatility,
                  explanation:
                    data.interpretation?.volatility_explanation,
                },
                {
                  title: "Bollinger Bands",
                  value: data.interpretation?.bollinger_state,
                  explanation:
                    data.interpretation?.bollinger_explanation,
                },
              ].map((item) => (
                <div
                  key={item.title}
                  style={{
                    padding: "16px",
                    border: "1px solid #e5e7eb",
                    borderRadius: "12px",
                    background: "#ffffff",
                  }}
                >
                  <h3
                    style={{
                      fontSize: "15px",
                      marginBottom: "8px",
                    }}
                  >
                    {item.title}
                  </h3>

                  <p
                    style={{
                      fontWeight: 600,
                      color: "#3157d5",
                      marginBottom: "9px",
                    }}
                  >
                    {item.value || "Not available"}
                  </p>

                  <p
                    style={{
                      fontSize: "13px",
                      lineHeight: 1.7,
                      color: "#667085",
                    }}
                  >
                    {item.explanation ||
                      "Interpretation unavailable."}
                  </p>
                </div>
              ))}
            </div>

            {/* DATA SOURCE */}

            <p
              style={{
                marginTop: "20px",
                fontSize: "12px",
                color: "#667085",
              }}
            >
              Source: {data.data_source} | Data date: {data.data_date}
            </p>

            {/* DISCLAIMER */}

            <p
              style={{
                marginTop: "8px",
                fontSize: "12px",
                color: "#667085",
              }}
            >
              {data.disclaimer}
            </p>
          </div>
        </>
      )}
    </div>
  );
}

const chartActionStyle = {
  border: "none",
  background: "transparent",
  color: "#3157d5",
  fontSize: "12px",
  fontWeight: 600,
  cursor: "pointer",
  padding: "6px",
};

export default TechnicalAnalysis;
