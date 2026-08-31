import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useNavigate,
  Outlet,
  useOutletContext
} from "react-router-dom";

import { useEffect, useState } from "react";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

/* Shared color palette for charts */
const CHART_COLORS = [
  "#3157d5",
  "#12b76a",
  "#f79009",
  "#f04438",
  "#7a5af8",
  "#0ba5ec",
  "#ee46bc",
  "#667085",
];

/* Common ticker -> company name lookup, used only for display labels.
   Falls back to the ticker itself for anything not in this list. */
const TICKER_NAMES = {
  AAPL: "Apple Inc.",
  MSFT: "Microsoft Corp.",
  NVDA: "NVIDIA Corp.",
  AMZN: "Amazon.com Inc.",
  GOOGL: "Alphabet Inc.",
  GOOG: "Alphabet Inc.",
  META: "Meta Platforms Inc.",
  TSLA: "Tesla Inc.",
  JPM: "JPMorgan Chase",
  JNJ: "Johnson & Johnson",
  V: "Visa Inc.",
  WMT: "Walmart Inc.",
  PG: "Procter & Gamble",
  MA: "Mastercard Inc.",
  UNH: "UnitedHealth Group",
  HD: "Home Depot Inc.",
  DIS: "Walt Disney Co.",
  BAC: "Bank of America",
  NFLX: "Netflix Inc.",
  XOM: "Exxon Mobil Corp.",
};

import api from "./api";
import Sidebar from "./Sidebar";


/* =========================================================
   ERROR HELPER
========================================================= */

function getErrorMessage(err, fallback) {
  const detail = err?.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.msg || "Validation error")
      .join(", ");
  }

  if (detail && typeof detail === "object") {
    return detail.message || JSON.stringify(detail);
  }

  return fallback;
}


/* =========================================================
   LOGIN
========================================================= */

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      const formData = new URLSearchParams();

      formData.append("username", email);
      formData.append("password", password);

      const response = await api.post(
        "/users/login",
        formData,
        {
          headers: {
            "Content-Type":
              "application/x-www-form-urlencoded",
          },
        }
      );

      localStorage.setItem(
        "token",
        response.data.access_token
      );

      navigate("/dashboard");
    } catch (err) {
      console.error(err);

      setError(
        getErrorMessage(
          err,
          "Login failed. Please check your credentials."
        )
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">

        <h1>StockSense</h1>

        <p>
          Smart Portfolio Intelligence
        </p>

        <form onSubmit={handleLogin}>

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
            required
          />

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
          >
            {loading
              ? "Logging in..."
              : "Login"}
          </button>

        </form>
        <p style={{ marginTop: "15px", fontSize: "0.9rem" }}>
          Don't have an account?{" "}
          <span 
            style={{ color: "var(--ss-primary)", cursor: "pointer", fontWeight: "bold" }} 
            onClick={() => navigate("/signup")}
          >
            Sign up here
          </span>
        </p>

      </div>
    </div>
  );
}

/* =========================================================
   SIGN UP
========================================================= */

function Signup() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignup = async (e) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      // Send registration data to the backend
      await api.post("/users/register", {
        name: name,
        email: email,
        password: password,
      });

      // On success, send them to the login page
      alert("Registration successful! Please log in.");
      navigate("/login");
    } catch (err) {
      console.error(err);
      setError(
        getErrorMessage(
          err,
          "Registration failed. Please try a different email."
        )
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>StockSense</h1>
        <p>Create your account</p>

        <form onSubmit={handleSignup}>
          <input
            type="text"
            placeholder="Full Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading}>
            {loading ? "Creating account..." : "Sign Up"}
          </button>
        </form>

        <p style={{ marginTop: "15px", fontSize: "0.9rem" }}>
          Already have an account?{" "}
          <span 
            style={{ color: "var(--ss-primary)", cursor: "pointer", fontWeight: "bold" }} 
            onClick={() => navigate("/login")}
          >
            Log in here
          </span>
        </p>
      </div>
    </div>
  );
}

/* =========================================================
   DASHBOARD
========================================================= */

function Dashboard() {
  const navigate = useNavigate();

  const [portfolios, setPortfolios] =
    useState([]);

  const [selectedPortfolioId, setSelectedPortfolioId] =
    useState(
      localStorage.getItem(
        "selectedPortfolioId"
      ) || ""
    );

  const [valuation, setValuation] =
    useState(null);

  const [analytics, setAnalytics] =
    useState(null);

  const [interpretation, setInterpretation] =
    useState(null);

  const [exposure, setExposure] =
    useState(null);

  const [recommendations, setRecommendations] =
    useState(null);

  const [benchmarkHistory, setBenchmarkHistory] = useState([]);
  const [benchmarkError, setBenchmarkError] = useState("");
  const [dailySummary, setDailySummary] = useState(null);
  const [geographicExposure, setGeographicExposure] = useState(null);
  const [geographicError, setGeographicError] = useState("");
  const [companies, setCompanies] = useState({});

  const [loadingRecommendations, setLoadingRecommendations] =
    useState(false);

  const [recommendationError, setRecommendationError] =
    useState("");

  const [loadingPortfolios, setLoadingPortfolios] =
    useState(true);

  const [loadingDashboard, setLoadingDashboard] =
    useState(false);

  const [error, setError] =
    useState("");

  const [showCreatePortfolio, setShowCreatePortfolio] =
    useState(false);

  const [showAddHolding, setShowAddHolding] =
    useState(false);

  const [portfolioName, setPortfolioName] =
    useState("");

  const [ticker, setTicker] =
    useState("");

  const [quantity, setQuantity] =
    useState("");

  const [avgBuyPrice, setAvgBuyPrice] =
    useState("");

  const [actionMessage, setActionMessage] =
    useState("");

  const [actionError, setActionError] =
    useState("");

  const [actionLoading, setActionLoading] =
    useState(false);

  /* =====================================================
     WHAT-IF SIMULATOR STATE
  ===================================================== */

  const [simulationTicker, setSimulationTicker] =
    useState("");

  const [simulationQuantity, setSimulationQuantity] =
    useState("");

  const [simulationResult, setSimulationResult] =
    useState(null);

  const [simulationLoading, setSimulationLoading] =
    useState(false);

  const [simulationError, setSimulationError] =
    useState("");

  /* =====================================================
     CONFIG
  ===================================================== */

  const getConfig = () => {
    const token =
      localStorage.getItem("token");

    return {
      headers: {
        Authorization:
          `Bearer ${token}`,
      },
    };
  };


  /* =====================================================
     LOAD PORTFOLIOS
  ===================================================== */

  const fetchPortfolios = async () => {
    try {
      const response =
        await api.get(
          "/portfolios",
          getConfig()
        );

      let data = response.data;

      if (
        !Array.isArray(data) &&
        Array.isArray(data?.portfolios)
      ) {
        data = data.portfolios;
      }

      if (!Array.isArray(data)) {
        data = [];
      }

      setPortfolios(data);

      if (data.length > 0) {

        const savedId =
          localStorage.getItem(
            "selectedPortfolioId"
          );

        const savedExists =
          data.some(
            (portfolio) =>
              String(
                portfolio.portfolio_id ??
                portfolio.id
              ) === String(savedId)
          );

        if (savedExists) {

          setSelectedPortfolioId(
            String(savedId)
          );

        } else {

          const firstId =
            data[0].portfolio_id ??
            data[0].id;

          setSelectedPortfolioId(
            String(firstId)
          );

          localStorage.setItem(
            "selectedPortfolioId",
            String(firstId)
          );
        }

      } else {

        setSelectedPortfolioId("");
      }

    } catch (err) {

      console.error(err);

      setError(
        getErrorMessage(
          err,
          "Unable to load portfolios."
        )
      );

    } finally {

      setLoadingPortfolios(false);
    }
  };


  /* =====================================================
     INITIAL LOAD
  ===================================================== */

  useEffect(() => {
    fetchPortfolios();
  }, []);


  /* =====================================================
     LOAD PORTFOLIO DATA
  ===================================================== */

  useEffect(() => {

    if (!selectedPortfolioId) {
      return;
    }

    const fetchDashboard = async () => {

      setLoadingDashboard(true);
      setError("");

      const config = getConfig();


      /* -----------------------------
         VALUATION
      ----------------------------- */

      try {

        const response =
          await api.get(
            `/portfolios/${selectedPortfolioId}/valuation`,
            config
          );

        setValuation(
          response.data
        );

      } catch (err) {

        console.error(
          "Valuation error:",
          err
        );

        setValuation(null);
      }


      /* -----------------------------
         ANALYTICS
      ----------------------------- */

      try {

        const response =
          await api.get(
            `/portfolios/${selectedPortfolioId}/analytics`,
            config
          );

        setAnalytics(
          response.data
        );

      } catch (err) {

        console.error(
          "Analytics unavailable:",
          err
        );

        setAnalytics(null);
      }


      /* -----------------------------
         INTERPRETATION
      ----------------------------- */

      try {

        const response =
          await api.get(
            `/portfolios/${selectedPortfolioId}/interpretation`,
            config
          );

        setInterpretation(
          response.data
        );

      } catch (err) {

        console.error(
          "Interpretation unavailable:",
          err
        );

        setInterpretation(null);
      }


      /* -----------------------------
         EXPOSURE
      ----------------------------- */

      try {

        const response =
          await api.get(
            `/portfolios/${selectedPortfolioId}/exposure`,
            config
          );

        setExposure(
          response.data
        );

      } catch (err) {

        console.error(
          "Exposure unavailable:",
          err
        );

        setExposure(null);
      }


      /* -----------------------------
         RECOMMENDATIONS
      ----------------------------- */

      setLoadingRecommendations(true);
      setRecommendationError("");

      try {

        const response =
          await api.get(
            `/portfolios/${selectedPortfolioId}/recommendations`,
            config
          );

        setRecommendations(
          response.data
        );

      } catch (err) {

        console.error(
          "Recommendations unavailable:",
          err
        );

        setRecommendations(null);

        setRecommendationError(
          getErrorMessage(
            err,
            "Portfolio recommendations are currently unavailable."
          )
        );

      } finally {

        setLoadingRecommendations(false);
      }


     /* BENCHMARK HISTORY */
      try {
        const response = await api.get(`/portfolios/${selectedPortfolioId}/benchmark-history`, config);
        const historyData = Array.isArray(response.data?.history) ? response.data.history : [];
        setBenchmarkHistory(historyData);
        setBenchmarkError("");
      } catch (err) {
        console.error("Benchmark history unavailable:", err);
        setBenchmarkHistory([]);
        setBenchmarkError(getErrorMessage(err, "Benchmark history is currently unavailable."));
      }

      /* SNAPSHOT / DAILY GAIN */
      try {
        const response = await api.get(`/portfolios/${selectedPortfolioId}/snapshots`, config);
        const snapshots = Array.isArray(response.data?.snapshots)
          ? [...response.data.snapshots].sort((a, b) => String(a.date).localeCompare(String(b.date)))
          : [];
        if (snapshots.length >= 2) {
          const latest = snapshots[snapshots.length - 1];
          const previous = snapshots[snapshots.length - 2];
          const latestValue = Number(latest.total_value);
          const previousValue = Number(previous.total_value);
          if (Number.isFinite(latestValue) && Number.isFinite(previousValue)) {
            setDailySummary({ gain: latestValue - previousValue, date: latest.date, isToday: latest.date === (() => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`; })() });
          } else setDailySummary(null);
        } else setDailySummary(null);
      } catch (err) {
        console.error("Snapshot history unavailable:", err);
        setDailySummary(null);
      }

      /* GEOGRAPHIC EXPOSURE */
      try {
        const response = await api.get(`/portfolios/${selectedPortfolioId}/geographic-exposure`, config);
        setGeographicExposure(response.data);
        setGeographicError("");
      } catch (err) {
        console.error("Geographic exposure unavailable:", err);
        setGeographicExposure(null);
        setGeographicError(getErrorMessage(err, "Geographic exposure is currently unavailable."));
      }

      /* COMPANY NAMES */
      try {
        const response = await api.get(`/portfolios/${selectedPortfolioId}/companies`, config);
        setCompanies(response.data?.companies || {});
      } catch (err) {
        console.error("Company names unavailable:", err);
        setCompanies({});
      }

      setLoadingDashboard(false);
    };


    fetchDashboard();

  }, [selectedPortfolioId]);


  /* =====================================================
     CREATE PORTFOLIO
  ===================================================== */

  const handleCreatePortfolio = async (e) => {

    e.preventDefault();

    if (!portfolioName.trim()) {

      setActionError(
        "Please enter a portfolio name."
      );

      return;
    }

    setActionLoading(true);
    setActionMessage("");
    setActionError("");

    try {

      const response =
        await api.post(
          "/portfolios/",
          {
            portfolio_name:
              portfolioName.trim(),
          },
          getConfig()
        );

      const newPortfolio =
        response.data;

      setPortfolioName("");
      setShowCreatePortfolio(false);

      setActionMessage(
        "Portfolio created successfully!"
      );

      await fetchPortfolios();

      const newId =
        newPortfolio?.portfolio_id ??
        newPortfolio?.id;

      if (newId) {

        setSelectedPortfolioId(
          String(newId)
        );

        localStorage.setItem(
          "selectedPortfolioId",
          String(newId)
        );
      }

    } catch (err) {

      console.error(err);

      setActionError(
        getErrorMessage(
          err,
          "Unable to create portfolio."
        )
      );

    } finally {

      setActionLoading(false);
    }
  };


  /* =====================================================
     ADD HOLDING
  ===================================================== */

  const handleAddHolding = async (e) => {

    e.preventDefault();

    if (!selectedPortfolioId) {

      setActionError(
        "Please select a portfolio first."
      );

      return;
    }

    setActionLoading(true);
    setActionMessage("");
    setActionError("");

    try {

      await api.post(
        `/portfolios/${selectedPortfolioId}/holdings`,
        {
          ticker:
            ticker.toUpperCase(),

          quantity:
            Number(quantity),

          avg_buy_price:
            Number(avgBuyPrice),
        },
        getConfig()
      );

      setTicker("");
      setQuantity("");
      setAvgBuyPrice("");

      setShowAddHolding(false);

      setActionMessage(
        "Holding added successfully!"
      );


      /* Refresh valuation */

      const config =
        getConfig();

      try {

        const response =
          await api.get(
            `/portfolios/${selectedPortfolioId}/valuation`,
            config
          );

        setValuation(
          response.data
        );

      } catch (err) {
        console.error(err);
      }


      /* Refresh analytics */

      try {

        const response =
          await api.get(
            `/portfolios/${selectedPortfolioId}/analytics`,
            config
          );

        setAnalytics(
          response.data
        );

      } catch (err) {
        console.error(err);
      }


      /* Refresh interpretation */

      try {

        const response =
          await api.get(
            `/portfolios/${selectedPortfolioId}/interpretation`,
            config
          );

        setInterpretation(
          response.data
        );

      } catch (err) {
        console.error(err);
      }


      /* Refresh exposure */

      try {

        const response =
          await api.get(
            `/portfolios/${selectedPortfolioId}/exposure`,
            config
          );

        setExposure(
          response.data
        );

      } catch (err) {
        console.error(err);
      }

      /* Refresh geographic exposure */
      try {
        const response = await api.get(
          `/portfolios/${selectedPortfolioId}/geographic-exposure`,
          config
        );
        setGeographicExposure(response.data);
        setGeographicError("");
      } catch (err) {
        console.error("Geographic exposure refresh failed:", err);
      }

      /* Refresh recommendations */
      try {

        const response =
          await api.get(
            `/portfolios/${selectedPortfolioId}/recommendations`,
            config
          );

        setRecommendations(
          response.data
        );

        setRecommendationError("");

      } catch (err) {

        console.error(err);

        setRecommendations(null);

        setRecommendationError(
          getErrorMessage(
            err,
            "Portfolio recommendations are currently unavailable."
          )
        );
      }

    } catch (err) {

      console.error(err);

      setActionError(
        getErrorMessage(
          err,
          "Unable to add holding."
        )
      );

    } finally {

      setActionLoading(false);
    }
  };


  /* =====================================================
     DELETE HOLDING
  ===================================================== */

  const handleDeleteHolding = async (
    holdingId
  ) => {

    const confirmed =
      window.confirm(
        "Are you sure you want to remove this holding?"
      );

    if (!confirmed) {
      return;
    }

    setActionMessage("");
    setActionError("");

    try {

      await api.delete(
        `/portfolios/${selectedPortfolioId}/holdings/${holdingId}`,
        getConfig()
      );

      setActionMessage(
        "Holding removed successfully!"
      );

      const config =
        getConfig();


      /* Refresh valuation */

      try {

        const response =
          await api.get(
            `/portfolios/${selectedPortfolioId}/valuation`,
            config
          );

        setValuation(
          response.data
        );

      } catch (err) {
        console.error(err);
      }


      /* Refresh analytics */

      try {

        const response =
          await api.get(
            `/portfolios/${selectedPortfolioId}/analytics`,
            config
          );

        setAnalytics(
          response.data
        );

      } catch (err) {
        console.error(err);
      }


      /* Refresh interpretation */

      try {

        const response =
          await api.get(
            `/portfolios/${selectedPortfolioId}/interpretation`,
            config
          );

        setInterpretation(
          response.data
        );

      } catch (err) {
        console.error(err);
      }


      /* Refresh exposure */

      try {

        const response =
          await api.get(
            `/portfolios/${selectedPortfolioId}/exposure`,
            config
          );

        setExposure(
          response.data
        );

      } catch (err) {
        console.error(err);
      }

      /* Refresh geographic exposure */
      try {
        const response = await api.get(
          `/portfolios/${selectedPortfolioId}/geographic-exposure`,
          config
        );
        setGeographicExposure(response.data);
        setGeographicError("");
      } catch (err) {
        console.error("Geographic exposure refresh failed:", err);
      }

      /* Refresh recommendations */
      try {

        const response =
          await api.get(
            `/portfolios/${selectedPortfolioId}/recommendations`,
            config
          );

        setRecommendations(
          response.data
        );

        setRecommendationError("");

      } catch (err) {

        console.error(err);

        setRecommendations(null);

        setRecommendationError(
          getErrorMessage(
            err,
            "Portfolio recommendations are currently unavailable."
          )
        );
      }

    } catch (err) {

      console.error(err);

      setActionError(
        getErrorMessage(
          err,
          "Unable to remove holding."
        )
      );
    }
  };


  /* =====================================================
     PORTFOLIO CHANGE
  ===================================================== */

  const handlePortfolioChange = (e) => {

    const newId =
      e.target.value;

    setSelectedPortfolioId(
      newId
    );

    localStorage.setItem(
      "selectedPortfolioId",
      newId
    );

    setActionMessage("");
    setActionError("");

    setSimulationResult(null);
    setSimulationError("");
    setSimulationTicker("");
    setSimulationQuantity("");

    setRecommendations(null);
    setRecommendationError("");
    setBenchmarkHistory([]);
    setBenchmarkError("");
    setDailySummary(null);
    setGeographicExposure(null);
    setGeographicError("");
    setCompanies({});
  };


  /* =====================================================
     WHAT-IF SIMULATION
  ===================================================== */

  const handleSimulation = async (e) => {
    e.preventDefault();

    if (!selectedPortfolioId) {
      setSimulationError(
        "Please select a portfolio first."
      );
      return;
    }

    if (!simulationTicker.trim()) {
      setSimulationError(
        "Please enter a stock ticker."
      );
      return;
    }

    const parsedQuantity =
      Number(simulationQuantity);

    if (
      !Number.isFinite(parsedQuantity) ||
      parsedQuantity <= 0
    ) {
      setSimulationError(
        "Please enter a valid quantity greater than 0."
      );
      return;
    }

    setSimulationLoading(true);
    setSimulationError("");
    setSimulationResult(null);

    try {
      const response = await api.post(
        `/portfolios/${selectedPortfolioId}/simulate`,
        {
          holdings: [
            {
              ticker:
                simulationTicker
                  .trim()
                  .toUpperCase(),
              quantity:
                parsedQuantity,
            },
          ],
        },
        getConfig()
      );

      setSimulationResult(
        response.data
      );

    } catch (err) {
      console.error(
        "Simulation error:",
        err
      );

      setSimulationError(
        getErrorMessage(
          err,
          "Unable to run the portfolio simulation."
        )
      );

    } finally {
      setSimulationLoading(false);
    }
  };


  /* =====================================================
     LOGOUT
  ===================================================== */

  const logout = () => {

    localStorage.removeItem(
      "token"
    );

    localStorage.removeItem(
      "selectedPortfolioId"
    );

    navigate("/login");
  };


  /* =====================================================
     LOADING
  ===================================================== */

  if (loadingPortfolios) {

    return (
      <div className="dashboard">

        <h2>
          Loading portfolios...
        </h2>

      </div>
    );
  }


  /* =====================================================
     NO PORTFOLIOS
  ===================================================== */

  if (
    !loadingPortfolios &&
    portfolios.length === 0
  ) {

    return (
      <div className="dashboard">
        {/* SIDEBAR */}
        <Sidebar />
        <div className="dashboard-main">

          <header className="dashboard-header">

            <div>

              <h1>
                StockSense
              </h1>

              <p>
                Portfolio Intelligence Dashboard
              </p>

            </div>

            <button onClick={logout}>
              Logout
            </button>

          </header>


          <main className="dashboard-content">

            <div className="welcome-card">

              <h2>
                No portfolios yet
              </h2>

              <p>
                Create your first portfolio to get started.
              </p>

              <button
                className="primary-button"
                onClick={() =>
                  setShowCreatePortfolio(true)
                }
              >
                + Create Portfolio
              </button>

            </div>

          </main>


          {showCreatePortfolio && (

            <div className="modal-overlay">

              <div className="modal-card">

                <h2>
                  Create Portfolio
                </h2>

                <form
                  onSubmit={
                    handleCreatePortfolio
                  }
                >

                  <input
                    type="text"
                    placeholder="Portfolio name"
                    value={portfolioName}
                    onChange={(e) =>
                      setPortfolioName(
                        e.target.value
                      )
                    }
                    required
                  />

                  {actionError && (
                    <div className="error-message">
                      {actionError}
                    </div>
                  )}

                  <div className="modal-actions">

                    <button
                      type="button"
                      onClick={() =>
                        setShowCreatePortfolio(
                          false
                        )
                      }
                    >
                      Cancel
                    </button>

                    <button
                      type="submit"
                      className="primary-button"
                      disabled={actionLoading}
                    >
                      {actionLoading
                        ? "Creating..."
                        : "Create Portfolio"}
                    </button>

                  </div>

                </form>

              </div>

            </div>
          )}

        </div>
      </div>
    );
  }


  /* =====================================================
     DASHBOARD LOADING
  ===================================================== */

  if (
    loadingDashboard ||
    !valuation
  ) {

    return (
      <div className="dashboard">
        <Sidebar />

        <div className="dashboard-main">

          <header className="dashboard-header">

            <div>

              <h1>
                StockSense
              </h1>

              <p>
                Portfolio Intelligence Dashboard
              </p>

            </div>

            <button onClick={logout}>
              Logout
            </button>

          </header>

          <main className="dashboard-content">

            <div className="welcome-card">

              <h2>
                Loading portfolio...
              </h2>

              <p>
                Preparing your portfolio data.
              </p>

            </div>

          </main>
        </div>
      </div>
    );
  }


  /* =====================================================
     DATA
  ===================================================== */

  const performance =
    analytics?.performance || {};

  const risk =
    analytics?.risk || {};

  const diversification =
    analytics?.diversification || {};

  const allocationData =
    Object.entries(
      diversification.weights || {}
    ).map(
      ([ticker, weight]) => ({
        name: ticker,
        value: Number(weight),
      })
    );


  const correlationMatrix =
    risk.correlation_matrix || {};


  const selectedPortfolio =
    portfolios.find(
      (portfolio) =>
        String(
          portfolio.portfolio_id ??
          portfolio.id
        ) ===
        String(selectedPortfolioId)
    );


  const portfolioInterpretation =
    interpretation?.interpretation;


  /* =====================================================
     EXPOSURE DATA
  ===================================================== */

  const exposureData =
    exposure?.exposure || {};

  const sectorExposure =
    exposureData.sector_exposure || {};

  const sectorChartData =
    Object.entries(
      sectorExposure
    ).map(
      ([sector, weight]) => ({
        name: sector,
        value: Number(weight),
      })
    );


  const largestSector =
    exposureData.largest_sector ||
    "--";

  const largestSectorWeight =
    Number(
      exposureData.largest_sector_weight || 0
    );

  const sectorCount =
    exposureData.sector_count || 0;


  /* =====================================================
     MAIN DASHBOARD
  ===================================================== */

  return (
    <div className="dashboard">
      <Sidebar />
      
      <div className="dashboard-main">
        <header className="dashboard-header">
          <div>
            <h1>StockSense</h1>
            <p>Portfolio Intelligence Dashboard</p>
          </div>
          <button onClick={logout}>Logout</button>
        </header>

        <main className="dashboard-content">
          {/* 
            This is the magic part. The Outlet acts as a window to your sub-pages.
            We are passing all your fetched data through the "context" so the pages can use it.
          */}
          <Outlet context={{
            selectedPortfolio,
            portfolios,
            selectedPortfolioId,
            handlePortfolioChange,
            setShowCreatePortfolio,
            setShowAddHolding,
            valuation,
            analytics,
            interpretation,
            exposure,
            recommendations,
            benchmarkHistory,
            benchmarkError,
            dailySummary,
            geographicExposure,
            geographicError,
            companies,
            simulationTicker,
            setSimulationTicker,
            simulationQuantity,
            setSimulationQuantity,
            simulationLoading,
            simulationError,
            simulationResult,
            handleSimulation,
            handleDeleteHolding
          }} />
        </main>

        {/* CREATE PORTFOLIO MODAL */}
        {showCreatePortfolio && (
          <div className="modal-overlay">
            <div className="modal-card">
              <h2>Create New Portfolio</h2>
              <form onSubmit={handleCreatePortfolio}>
                <input
                  type="text"
                  placeholder="e.g. Long Term Investments"
                  value={portfolioName}
                  onChange={(e) => setPortfolioName(e.target.value)}
                  required
                />
                {actionError && <div className="error-message">{actionError}</div>}
                <div className="modal-actions">
                  <button type="button" onClick={() => setShowCreatePortfolio(false)}>Cancel</button>
                  <button type="submit" className="primary-button" disabled={actionLoading}>
                    {actionLoading ? "Creating..." : "Create Portfolio"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* ADD HOLDING MODAL */}
        {showAddHolding && (
          <div className="modal-overlay">
            <div className="modal-card">
              <h2>Add Holding</h2>
              <form onSubmit={handleAddHolding}>
                <input
                  type="text"
                  placeholder="Ticker e.g. AAPL"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  required
                />
                <input
                  type="number"
                  min="0.0001"
                  step="any"
                  placeholder="Quantity"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  required
                />
                <input
                  type="number"
                  min="0.01"
                  step="any"
                  placeholder="Average Buy Price"
                  value={avgBuyPrice}
                  onChange={(e) => setAvgBuyPrice(e.target.value)}
                  required
                />
                {actionError && <div className="error-message">{actionError}</div>}
                <div className="modal-actions">
                  <button type="button" onClick={() => setShowAddHolding(false)}>Cancel</button>
                  <button type="submit" className="primary-button" disabled={actionLoading}>
                    {actionLoading ? "Adding..." : "Add Holding"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function OverviewPage() {
  const { valuation, selectedPortfolio, portfolios, selectedPortfolioId, handlePortfolioChange, setShowAddHolding, setShowCreatePortfolio, handleDeleteHolding, analytics, interpretation, recommendations, benchmarkHistory, benchmarkError, dailySummary } = useOutletContext();
  const performance = analytics?.performance || {};
  const risk = analytics?.risk || {};
  const diversification = analytics?.diversification || {};
  const portfolioInterpretation = interpretation?.interpretation;
  const healthScore = Number(recommendations?.overall_assessment?.health_score ?? analytics?.health?.health_score ?? 0);
  const healthRating = recommendations?.overall_assessment?.rating ?? analytics?.health?.rating ?? "--";
  const totalValue = Number(valuation?.current_value || 0);
  const holdings = valuation?.holdings || [];
  const ruleInsights = [
    ...(portfolioInterpretation?.strengths || []).map((text) => ({ text, tone: "good", icon: "✓" })),
    ...(portfolioInterpretation?.warnings || []).map((text) => ({ text, tone: "warn", icon: "!" })),
    ...(recommendations?.recommendations || []).map((item) => ({ text: item?.message || item?.title, tone: "tip", icon: "★" })),
  ].filter((item) => item.text).slice(0, 4);
  const topHoldings = [...holdings].sort((a, b) => Number(b.current_value || 0) - Number(a.current_value || 0)).slice(0, 5).map((h) => ({ ...h, weight: totalValue > 0 ? (Number(h.current_value || 0) / totalValue) * 100 : 0 }));
  const concentration = Number(diversification.concentration_index ?? 0);
  const diversificationLabel = concentration === 0 ? "--" : concentration <= 0.25 ? "Good" : concentration <= 0.40 ? "Moderate" : "Concentrated";
  const overviewChartData = (Array.isArray(benchmarkHistory) ? benchmarkHistory : []).map((row) => ({ date: row.date, portfolio: Number(row.portfolio), benchmark: Number(row.benchmark) })).filter((row) => row.date && Number.isFinite(row.portfolio) && Number.isFinite(row.benchmark));

  return (
    <div className="feature-page">
      <div className="portfolio-selector-card" style={{marginBottom: "24px"}}>
        <div><h2>Your Portfolio</h2><p>Select and manage your portfolio.</p></div>
        <div className="portfolio-actions">
          <select value={selectedPortfolioId} onChange={handlePortfolioChange}>
            {portfolios.map((portfolio) => <option key={portfolio.portfolio_id ?? portfolio.id} value={portfolio.portfolio_id ?? portfolio.id}>{portfolio.name ?? portfolio.portfolio_name ?? `Portfolio ${portfolio.portfolio_id ?? portfolio.id}`}</option>)}
          </select>
          <button className="secondary-button" onClick={() => setShowAddHolding(true)}>+ Add Holding</button>
          <button className="primary-button" onClick={() => setShowCreatePortfolio(true)}>+ Add Portfolio</button>
        </div>
      </div>

      <div className="ss-overview-header">
        <div className="feature-hero" style={{marginBottom: 0}}>
          <div className="feature-eyebrow">PORTFOLIO OVERVIEW</div>
          <h1>{selectedPortfolio?.name ?? selectedPortfolio?.portfolio_name ?? "Your portfolio"},<br/><span>at a glance.</span></h1>
        </div>
        {(recommendations?.status === "success" || analytics?.health) && <div className="ss-health-pill" data-rating={String(healthRating).toLowerCase()}>Health Score <strong>{healthScore.toFixed(0)}/100</strong></div>}
      </div>

      <div className="feature-grid">
        <div className="feature-card"><h3>Portfolio Value</h3><h2 style={{marginTop: "10px", fontSize: "2rem"}}>${totalValue.toFixed(2)}</h2></div>
        <div className="feature-card"><h3>{dailySummary?.isToday ? "Today's Gain" : "Latest Daily Gain"}</h3><h2 className={Number(dailySummary?.gain ?? 0) >= 0 ? "ss-positive" : "ss-negative"} style={{marginTop: "10px", fontSize: "2rem"}}>{dailySummary ? `${dailySummary.gain >= 0 ? "+" : "-"}$${Math.abs(dailySummary.gain).toFixed(2)}` : "--"}</h2>{!dailySummary && <span className="ss-metric-pending-note">Waiting for at least two portfolio snapshots.</span>}</div>
        <div className="feature-card"><h3>Annual Return</h3><h2 style={{marginTop: "10px", fontSize: "2rem"}}>{Number(performance.annualized_return ?? 0).toFixed(2)}%</h2></div>
        <div className="feature-card"><h3>Sharpe Ratio</h3><h2 style={{marginTop: "10px", fontSize: "2rem"}}>{Number(performance.sharpe_ratio ?? 0).toFixed(2)}</h2></div>
      </div>

      <div className="ss-two-col" style={{marginTop: "24px"}}>
        <div className="welcome-card">
          <h2>Portfolio vs. S&amp;P 500</h2>
          <div className="ss-chart-legend"><span><span className="ss-legend-dot" style={{background: "#3157d5"}} /> My Portfolio</span><span><span className="ss-legend-dot" style={{background: "#12b76a"}} /> S&amp;P 500 (SPY)</span></div>
          {overviewChartData.length >= 2 ? <div style={{width: "100%", height: "300px"}}><ResponsiveContainer width="100%" height="100%"><LineChart data={overviewChartData}><CartesianGrid strokeDasharray="3 3" stroke="var(--ss-border-light)" vertical={false}/><XAxis dataKey="date" tick={{fontSize: 11, fill: "var(--ss-text-muted)"}} axisLine={false} tickLine={false}/><YAxis tick={{fontSize: 11, fill: "var(--ss-text-muted)"}} axisLine={false} tickLine={false}/><Tooltip formatter={(value) => Number(value).toFixed(2)}/><Legend/><Line type="monotone" dataKey="portfolio" name="My Portfolio" stroke="#3157d5" strokeWidth={2.5} dot={false}/><Line type="monotone" dataKey="benchmark" name="S&amp;P 500 (SPY)" stroke="#12b76a" strokeWidth={2.5} dot={false}/></LineChart></ResponsiveContainer></div> : <div className="ss-chart-placeholder"><span className="ss-chart-placeholder-icon">📈</span><p>{benchmarkError || "At least two benchmark observations are required to render this chart."}</p></div>}
        </div>
        <div className="welcome-card"><h2>Rule-Based Insights</h2>{ruleInsights.length === 0 ? <p style={{marginTop: "12px"}}>Insights will appear once enough data is available.</p> : <div className="ss-pill-list">{ruleInsights.map((item,index)=><div key={index} className={`ss-pill ss-pill-${item.tone}`}><span className="ss-pill-icon">{item.icon}</span><span>{item.text}</span></div>)}</div>}</div>
      </div>

      <div className="ss-two-col" style={{marginTop: "24px"}}>
        <div className="welcome-card"><h2>Top Holdings</h2>{topHoldings.length === 0 ? <p>No holdings in this portfolio yet.</p> : <table className="ss-holdings-table"><thead><tr><th>Stock</th><th>Weight</th><th>Return</th></tr></thead><tbody>{topHoldings.map((holding)=><tr key={holding.holding_id ?? holding.id ?? holding.ticker}><td><strong>{holding.ticker}</strong></td><td>{holding.weight.toFixed(0)}%</td><td className={Number(holding.gain_loss_percentage || 0) >= 0 ? "ss-positive" : "ss-negative"}>{Number(holding.gain_loss_percentage || 0) >= 0 ? "+" : ""}{Number(holding.gain_loss_percentage || 0).toFixed(0)}%</td></tr>)}</tbody></table>}</div>
        <div className="welcome-card"><h2>Risk Metrics</h2><div className="ss-risk-list"><div className="ss-risk-row"><span>Beta</span><strong>{Number.isFinite(Number(risk.beta)) ? Number(risk.beta).toFixed(2) : "--"}</strong></div><div className="ss-risk-row"><span>Volatility</span><strong>{Number(performance.annualized_volatility ?? 0).toFixed(1)}%</strong></div><div className="ss-risk-row"><span>Max Drawdown</span><strong>{Number(performance.max_drawdown ?? 0).toFixed(1)}%</strong></div><div className="ss-risk-row"><span>Diversification</span><strong>{diversificationLabel}</strong></div></div></div>
      </div>

      <div className="welcome-card" style={{marginTop: "24px"}}><h2>Your Holdings</h2>{!holdings.length ? <p>No holdings in this portfolio yet.</p> : holdings.map((holding)=><div key={holding.holding_id ?? holding.id ?? holding.ticker} className="holding-row"><strong>{holding.ticker}</strong><span>{holding.quantity} shares</span><span>${Number(holding.current_value || 0).toFixed(2)}</span><span className={Number(holding.gain_loss_percentage || 0) >= 0 ? "ss-positive" : "ss-negative"}>{Number(holding.gain_loss_percentage || 0) >= 0 ? "+" : ""}{Number(holding.gain_loss_percentage || 0).toFixed(2)}%</span>{(holding.holding_id || holding.id) && <button className="delete-button" onClick={() => handleDeleteHolding(holding.holding_id ?? holding.id)}>Remove</button>}</div>)}</div>
    </div>
  );
}

function AnalyticsPage() {
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
  const returnAttributionData = holdings.map((h) => ({
    ticker: h.ticker,
    return: Number(h.gain_loss_percentage || 0),
  }));

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
              <div style={{width: "100%", height: "240px", marginTop: "12px"}}><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={geographicExposure.exposure.map((item)=>({name:item.country,value:Number(item.weight)}))} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={2}>{geographicExposure.exposure.map((item,index)=><Cell key={`country-cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]}/>)}</Pie><Tooltip formatter={(value)=>`${Number(value).toFixed(2)}%`}/><Legend/></PieChart></ResponsiveContainer></div>
              <p className="ss-text-muted-cell" style={{marginTop: "8px"}}>Largest country: <strong>{geographicExposure.largest_country}</strong> ({Number(geographicExposure.largest_country_weight).toFixed(1)}%)</p>
            </>
          ) : <div className="ss-chart-placeholder" style={{minHeight: "160px"}}><span className="ss-chart-placeholder-icon">🌍</span><p>{geographicError || "Country data is not available for the current holdings."}</p></div>}
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

function PerformancePage() {
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

function InsightsPage() {
  const { interpretation, recommendations } = useOutletContext();
  const portfolioInterpretation = interpretation?.interpretation;

  const healthScore = Number(recommendations?.overall_assessment?.health_score ?? 0);
  const healthRating = recommendations?.overall_assessment?.rating ?? "--";

  return (
    <div className="feature-page">
      <div className="feature-hero">
        <div className="feature-eyebrow">PORTFOLIO INSIGHTS</div>
        <h1>Numbers are useful.<br /><span>Understanding them is better.</span></h1>
        <p>{portfolioInterpretation?.summary ?? "Portfolio insights will appear once enough data is available."}</p>
      </div>

      {/* OVERALL HEALTH — one compact hero stat instead of a paragraph */}
      {recommendations?.status === "success" && (
        <div className="ss-health-banner">
          <div className="ss-health-score-ring" data-rating={healthRating.toLowerCase()}>
            <span>{healthScore.toFixed(0)}</span>
            <small>/100</small>
          </div>
          <div>
            <div className="ss-health-rating">{healthRating}</div>
            <p>{recommendations.overall_assessment?.message ?? "No overall assessment is available."}</p>
          </div>
        </div>
      )}

      {/* STRENGTHS & WARNINGS — compact pill lists, not paragraph cards */}
      {portfolioInterpretation && (
        <div className="ss-insight-columns">
          <div className="ss-insight-block">
            <h3 className="ss-insight-block-title ss-good">Strengths</h3>
            <ul className="ss-insight-list">
              {portfolioInterpretation.strengths?.map((item, index) => (
                <li key={index} className="ss-insight-item ss-good">
                  <span className="ss-insight-dot" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div className="ss-insight-block">
            <h3 className="ss-insight-block-title ss-warn">Watch out for</h3>
            <ul className="ss-insight-list">
              {portfolioInterpretation.warnings?.map((item, index) => (
                <li key={index} className="ss-insight-item ss-warn">
                  <span className="ss-insight-dot" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* RECOMMENDATIONS — condensed rows instead of stacked cards */}
      {recommendations?.status === "success" && (
        <div className="welcome-card" style={{ marginTop: "24px" }}>
          <h2>Key Recommendations</h2>
          <div className="ss-rec-list">
            {recommendations.recommendations?.map((item, index) => {
              const severity = item?.severity ?? "medium";
              return (
                <div key={`${item?.type ?? "recommendation"}-${index}`} className="ss-rec-row">
                  <span className={`ss-severity-dot ss-severity-${severity}`} title={severity} />
                  <div className="ss-rec-body">
                    <div className="ss-rec-title">{item?.title ?? "Portfolio Recommendation"}</div>
                    <p className="ss-rec-message">{item?.message ?? ""}</p>
                    <div className="ss-rec-meta">
                      {item?.metric && (
                        <span className="ss-rec-metric">
                          {item.metric.name}:{" "}
                          <strong>
                            {typeof item.metric.value === "number"
                              ? Number(item.metric.value).toFixed(item.metric.name === "Concentration Index" ? 4 : 2)
                              : item.metric.value}
                          </strong>
                        </span>
                      )}
                      {item?.action && <span className="ss-rec-action">→ {item.action}</span>}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function SimulatorPage() {
  const { 
    simulationTicker, setSimulationTicker, simulationQuantity, setSimulationQuantity, 
    simulationLoading, simulationError, handleSimulation, simulationResult, analytics
  } = useOutletContext();

  // Prefer a "current" baseline returned by the simulation itself; fall back
  // to the portfolio's existing analytics if the API doesn't provide one.
  const simulated = simulationResult?.simulation?.simulated;
  const current = simulationResult?.simulation?.current ?? analytics?.performance;

  const comparisonData = simulated
    ? [
        {
          metric: "Annualized Return",
          Current: Number(current?.annualized_return ?? 0),
          Simulated: Number(simulated.annualized_return ?? 0),
        },
        {
          metric: "Annualized Volatility",
          Current: Number(current?.annualized_volatility ?? 0),
          Simulated: Number(simulated.annualized_volatility ?? 0),
        },
      ]
    : [];

  return (
    <div className="feature-page">
      <div className="feature-hero">
        <div className="feature-eyebrow">WHAT-IF SIMULATOR</div>
        <h1>Explore possibilities.<br /><span>Without changing your portfolio.</span></h1>
      </div>

      <div className="welcome-card" style={{marginTop: "30px"}}>
        <form onSubmit={handleSimulation} style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
          <input
            type="text"
            placeholder="Ticker e.g. MSFT"
            value={simulationTicker}
            onChange={(e) => setSimulationTicker(e.target.value.toUpperCase())}
            required
          />
          <input
            type="number"
            min="0.0001"
            step="any"
            placeholder="Quantity"
            value={simulationQuantity}
            onChange={(e) => setSimulationQuantity(e.target.value)}
            required
          />
          <button type="submit" className="primary-button" disabled={simulationLoading}>
            {simulationLoading ? "Simulating..." : "Run Simulation"}
          </button>
        </form>
        {simulationError && <div className="error-message" style={{marginTop: "15px"}}>{simulationError}</div>}
      </div>

      {simulationResult?.simulation && (
        <>
          <div className="feature-grid" style={{ marginTop: "30px" }}>
            <div className="feature-card">
              <div className="feature-icon">↗</div>
              <h3>Simulated Return</h3>
              <h2 style={{ marginTop: "10px", fontSize: "2rem" }}>
                {Number(simulated.annualized_return ?? 0).toFixed(2)}%
              </h2>
            </div>
            <div className="feature-card">
              <div className="feature-icon">σ</div>
              <h3>Simulated Volatility</h3>
              <h2 style={{ marginTop: "10px", fontSize: "2rem" }}>
                {Number(simulated.annualized_volatility ?? 0).toFixed(2)}%
              </h2>
            </div>
          </div>

          <div className="welcome-card" style={{ marginTop: "24px" }}>
            <h2>Before vs. After</h2>
            <p style={{ marginBottom: "20px" }}>
              How your portfolio's return and volatility would shift with this change.
            </p>
            <div style={{ width: "100%", height: "320px" }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={comparisonData} barGap={8}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--ss-border-light)" vertical={false} />
                  <XAxis dataKey="metric" tick={{ fontSize: 13, fill: "var(--ss-text-muted)" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 12, fill: "var(--ss-text-muted)" }} axisLine={false} tickLine={false} unit="%" />
                  <Tooltip formatter={(value) => `${Number(value).toFixed(2)}%`} cursor={{ fill: "var(--ss-surface-soft)" }} />
                  <Legend />
                  <Bar dataKey="Current" fill="#98a2b3" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="Simulated" fill="var(--ss-primary)" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

/* =========================================================
   APP ROUTER
========================================================= */

/* =========================================================
   APP ROUTER
========================================================= */

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        {/* ADD THE SIGNUP ROUTE HERE */}
        <Route path="/signup" element={<Signup />} />
        
        {/* The Parent Dashboard Layout */}
        <Route path="/dashboard" element={<Dashboard />}>
          {/* Default to overview if they just type /dashboard */}
          <Route index element={<Navigate to="overview" replace />} />
          
          {/* Child Routes */}
          <Route path="overview" element={<OverviewPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="performance" element={<PerformancePage />} />
          <Route path="insights" element={<InsightsPage />} />
          <Route path="simulator" element={<SimulatorPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
