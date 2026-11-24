import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useNavigate,
  Outlet
} from "react-router-dom";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import { getErrorMessage } from "./utils/errorHelpers";
import { useEffect, useState } from "react";
import Insights from "./pages/Insights";
import Performance from "./pages/Performance";
import Analytics from "./pages/Analytics";
import Simulator from "./pages/Simulator";
import Overview from "./pages/Overview";
import Chatbot from "./pages/Chatbot";
import api from "./api";
import Sidebar from "./Sidebar";
import TechnicalAnalysis from "./components/TechnicalAnalysis";

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
     ADVANCED WHAT-IF SIMULATOR STATE
  ===================================================== */

  const [simulationResult, setSimulationResult] = useState(null);

  const [simulationLoading, setSimulationLoading] = useState(false);

  const [simulationError, setSimulationError] = useState("");

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
     ADVANCED WHAT-IF SIMULATION
  ===================================================== */

  const handleAdvancedSimulation = async (payload) => {
    if (!selectedPortfolioId) {
      setSimulationError("Please select a portfolio first.");
      return;
    }

    setSimulationLoading(true);
    setSimulationError("");
    setSimulationResult(null);

    try {
      const response = await api.post(
        `/portfolios/${selectedPortfolioId}/simulate/advanced`,
        payload,
        getConfig()
      );

      setSimulationResult(response.data);
    } catch (err) {
      console.error("Advanced simulation error:", err);

      setSimulationError(
        getErrorMessage(err, "Unable to run the advanced simulation.")
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

  const selectedPortfolio =
    portfolios.find(
      (portfolio) =>
        String(
          portfolio.portfolio_id ??
          portfolio.id
        ) ===
        String(selectedPortfolioId)
    );

  /* =====================================================
     MAIN DASHBOARD
  ===================================================== */

  return (
    <div className="dashboard">
      <Sidebar />
      
      <div className="dashboard-main">

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
              simulationLoading,
              simulationError,
              simulationResult,
              handleAdvancedSimulation,
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
          <Route path="overview" element={<Overview />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="performance" element={<Performance />} />
          <Route path="insights" element={<Insights />} />
          <Route path="simulator" element={<Simulator />} />
          <Route path="technical-analysis" element={<TechnicalAnalysis />} />
          <Route path="chatbot" element={<Chatbot />} />
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;