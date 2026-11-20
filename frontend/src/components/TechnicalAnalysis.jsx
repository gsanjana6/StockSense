
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

function TechnicalAnalysis() {
  const [ticker, setTicker] = useState("AAPL");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

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

      <div className="welcome-card">
        <h2>Search a Stock</h2>

        <form
          onSubmit={fetchAnalysis}
          style={{ display: "flex", gap: "12px", marginTop: "16px" }}
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
          <div className="feature-grid" style={{ marginTop: "24px" }}>
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
          
          {/* STOCK PRICE AND MOVING AVERAGES CHART */}
          <div className="welcome-card" style={{ marginTop: "24px" }}>
            <h2>Stock Price & Moving Averages</h2>

            <p style={{ marginTop: "8px", marginBottom: "20px" }}>
              Compare the closing price with its 20-day, 50-day and
              200-day moving averages and Bollinger Bands.
            </p>

            {Array.isArray(data.chart) && data.chart.length > 0 ? (
              <div style={{ width: "100%", height: "380px" }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={data.chart}
                    margin={{ top: 10, right: 20, left: 10, bottom: 10 }}
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

                    <Line
                      type="monotone"
                      dataKey="close"
                      name="Closing Price"
                      stroke="#3157d5"
                      strokeWidth={3}
                      dot={false}
                    />

                    <Line
                      type="monotone"
                      dataKey="sma_20"
                      name="SMA 20"
                      stroke="#12b76a"
                      strokeWidth={2}
                      dot={false}
                    />

                    <Line
                      type="monotone"
                      dataKey="sma_50"
                      name="SMA 50"
                      stroke="#f79009"
                      strokeWidth={2}
                      dot={false}
                    />

                    <Line
                      type="monotone"
                      dataKey="sma_200"
                      name="SMA 200"
                      stroke="#7a5af8"
                      strokeWidth={2}
                      dot={false}
                    />

                    <Line
                      type="monotone"
                      dataKey="bb_upper"
                      name="Bollinger Upper"
                      stroke="#94a3b8"
                      strokeWidth={1.5}
                      strokeDasharray="5 5"
                      dot={false}
                    />

                    <Line
                      type="monotone"
                      dataKey="bb_lower"
                      name="Bollinger Lower"
                      stroke="#94a3b8"
                      strokeWidth={1.5}
                      strokeDasharray="5 5"
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p>Historical chart data is unavailable.</p>
            )}
          </div>

          <div className="welcome-card" style={{ marginTop: "24px" }}>
            <h2>Technical Interpretation</h2>
            <p style={{ marginTop: "12px" }}>
              {data.interpretation?.explanation ||
                "No interpretation available."}
            </p>
            <p style={{ marginTop: "12px", fontSize: "13px" }}>
              Source: {data.data_source} | Data date: {data.data_date}
            </p>
          </div>
        </>
      )}
    </div>
  );
}

export default TechnicalAnalysis;
