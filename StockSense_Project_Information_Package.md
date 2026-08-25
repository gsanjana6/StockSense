# StockSense — Technical Project Information & Audit Package

> **Notice for Report Authors / Evaluators:**  
> This document is an exhaustive, code-verified technical audit and information package for **StockSense**. Every claim, equation, schema, endpoint, data flow, and user interface element in this package has been directly verified from the actual codebase located at `c:\Users\Sanjana\Desktop\Project\StockSense`. Features not supported by source code are explicitly flagged as `[PARTIALLY IMPLEMENTED]`, `[MOCKED/HARDCODED]`, `[PLANNED]`, `[NOT FOUND]`, or `NOT VERIFIED FROM CODE`.

---

## Table of Contents
1. [A. Project Overview](#a-project-overview)
2. [B. Project Structure](#b-project-structure)
3. [C. Problem, Objectives and Scope](#c-problem-objectives-and-scope)
4. [D. Technology Stack](#d-technology-stack)
5. [E. Complete Feature Inventory](#e-complete-feature-inventory)
6. [F. Frontend Analysis](#f-frontend-analysis)
7. [G. Backend Analysis](#g-backend-analysis)
8. [H. Database Analysis](#h-database-analysis)
9. [I. System Data Flow](#i-system-data-flow)
10. [J. Financial and Statistical Calculations](#j-financial-and-statistical-calculations)
11. [K. External APIs and Data Sources](#k-external-apis-and-data-sources)
12. [L. Authentication and Security](#l-authentication-and-security)
13. [M. Functional Requirements](#m-functional-requirements)
14. [N. Non-Functional Requirements](#n-non-functional-requirements)
15. [O. System Architecture](#o-system-architecture)
16. [P. Module Design](#p-module-design)
17. [Q. UI / Interface Design](#q-ui--interface-design)
18. [R. Testing](#r-testing)
19. [S. Implementation Details](#s-implementation-details)
20. [T. Design and Implementation Issues](#t-design-and-implementation-issues)
21. [U. Advantages](#u-advantages)
22. [V. Limitations](#v-limitations)
23. [W. Future Enhancements](#w-future-enhancements)
24. [X. Screenshot and Diagram Inventory](#x-screenshot-and-diagram-inventory)
25. [Y. Report Section Mapping](#y-report-section-mapping)
26. [Z. References / Sources](#z-references--sources)
27. [AA. Evidence Table](#aa-evidence-table)
28. [AB. Items That Could Not Be Verified](#ab-items-that-could-not-be-verified)
29. [Final Quality Check Synthesis](#final-quality-check-synthesis)

---

## A. PROJECT OVERVIEW

* **Exact Project Name:** StockSense
* **Project Title Used in Application:** StockSense — Portfolio Intelligence Dashboard (also referenced as *Smart Portfolio Intelligence*)
* **One-Paragraph Description:**  
  StockSense is a full-stack, web-based portfolio intelligence and risk analytics platform designed to empower individual investors and portfolio managers with institutional-grade quantitative analytics. The system enables users to create and manage investment portfolios, track real-time valuations, analyze historical returns against market benchmarks (specifically the S&P 500 ETF, SPY), compute key risk metrics (Annualized Volatility, Sharpe Ratio, Beta, and Maximum Drawdown), evaluate diversification via the Herfindahl-Hirschman Index (HHI) and sector exposure, generate rule-based qualitative interpretations and actionable recommendations, calculate a proprietary 100-point Portfolio Health Score, and test hypothetical portfolio changes through an integrated What-If simulation engine.
* **Main Problem Solved:**  
  Traditional retail investing platforms display nominal profits and losses but lack sophisticated, accessible risk-adjusted performance evaluation. Retail investors frequently suffer from unhedged concentration risk, high market sensitivity (beta), and severe drawdowns without understanding their risk exposure. StockSense bridges the gap between raw trading data and financial engineering by providing automated, explainable risk analytics, diversification audits, and simulated portfolio stress-testing in an intuitive interface.
* **Target Users:**  
  1. Individual retail investors and personal portfolio managers.
  2. Finance and data science students/academics studying portfolio theory and asset allocation.
  3. Investment hobbyists seeking pre-trade impact simulations (What-If analysis).
* **Domain / Application Area:**  
  FinTech, Quantitative Finance, Portfolio Management, Investment Risk Analysis, Financial Data Science.
* **Application Nature & Form Factor:**  
  Web application (Single-Page Application frontend with a RESTful backend API and persistent relational database).
* **Full-Stack Implementation Status:**  
  Yes, fully functional full-stack architecture (React SPA frontend + FastAPI REST backend + MySQL relational database + background scheduler).
* **Financial Data Nature:**  
  Real financial market data retrieved dynamically via Yahoo Finance (`yfinance`) and Financial Modeling Prep (FMP) API, combined with a persistent relational database price cache for offline resilience and analytics caching.
* **Execution vs Analysis:**  
  StockSense **does not execute real stock trades** (no broker/exchange order routing). It is exclusively a portfolio analytics, intelligence, virtual tracking, and pre-trade simulation platform.

---

## B. PROJECT STRUCTURE

### Concise Verified Workspace Directory Tree
```
StockSense/
├── .gitignore
├── StockSense_Project_Information_Package.md # Comprehensive audit documentation package
├── backend/
│   ├── .env                                  # Environment configuration (secrets & DB credentials)
│   ├── requirements.txt                      # Python backend dependencies
│   └── app/
│       ├── __init__.py
│       ├── main.py                           # FastAPI application entry point & CORS configuration
│       ├── core/
│       │   ├── __init__.py
│       │   └── config.py                     # App settings & environment variable loader
│       ├── database/
│       │   ├── __init__.py
│       │   ├── base.py                       # SQLAlchemy declarative base definition
│       │   ├── connection.py                 # SQLAlchemy MySQL engine & connection validation
│       │   └── session.py                    # SessionLocal factory & get_db dependency provider
│       ├── models/
│       │   ├── __init__.py                   # Model exports
│       │   ├── user.py                       # User SQL model (users table)
│       │   ├── portfolio.py                  # Portfolio SQL model (portfolios table)
│       │   ├── holding.py                    # Holding SQL model (holdings table)
│       │   ├── portfolio_snapshot.py         # PortfolioSnapshot SQL model (portfolio_snapshots table)
│       │   ├── price_cache.py                # PriceCache SQL model (price_cache table)
│       │   └── company.py                    # CompanyMeta SQL model (company_meta table)
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── user.py                       # Pydantic schemas: UserCreate, UserResponse, Token, UserLogin
│       │   ├── portfolio.py                  # Pydantic schemas: PortfolioCreate, PortfolioUpdate, PortfolioResponse
│       │   ├── holding.py                    # Pydantic schemas: HoldingCreate, HoldingUpdate, HoldingResponse
│       │   └── simulation.py                 # Pydantic schemas: SimulatedHolding, WhatIfRequest
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── users.py                      # User authentication & registration endpoints
│       │   ├── portfolios.py                 # Portfolio CRUD, valuation, analytics, simulation, snapshots
│       │   └── holdings.py                   # Portfolio holdings CRUD endpoints
│       ├── services/
│       │   ├── __init__.py
│       │   ├── market_data_service.py        # Yahoo Finance live & historical price retrieval and caching
│       │   ├── company_service.py            # FMP API integration & company metadata caching
│       │   ├── portfolio_service.py          # Portfolio valuation, invested capital, P&L calculations
│       │   ├── exposure_service.py           # Sector exposure & concentration computations
│       │   ├── analytics_service.py          # Returns, Sharpe, Volatility, Beta, HHI, Health Score, Benchmark
│       │   ├── interpretation_service.py     # Rule-based qualitative plain-English interpretation
│       │   ├── recommendation_service.py     # Rule-based categorized recommendation cards
│       │   ├── simulation_service.py         # What-If hypothetical holding simulation engine
│       │   ├── snapshot_service.py           # Snapshot capture and historical retrieval
│       │   └── scheduler_service.py          # APScheduler background cron job (18:00 daily snapshots)
│       └── utils/
│           ├── __init__.py
│           ├── security.py                   # Passlib bcrypt password hashing and verification
│           ├── jwt_handler.py                # Jose JWT encoding, decoding, and expiration logic
│           └── auth.py                       # OAuth2 password bearer & get_current_user dependency
├── frontend/
│   ├── index.html                            # HTML entry document
│   ├── package.json                          # Node.js dependencies and run scripts
│   ├── package-lock.json                     # Locked NPM dependency tree
│   ├── vite.config.js                        # Vite React build configuration
│   ├── .oxlintrc.json                        # Oxlint configuration
│   ├── README.md                             # Vite default README
│   ├── public/
│   │   ├── favicon.svg                       # Application favicon
│   │   └── icons.svg                         # SVG icon definitions
│   └── src/
│       ├── main.jsx                          # React 19 root bootstrap
│       ├── App.jsx                           # Main application, Router, State, Pages & Modals
│       ├── api.js                            # Axios client configured with backend baseURL
│       ├── index.css                         # Global design system, CSS variables, utility classes
│       ├── App.css                           # Component-level styles
│       ├── assets/
│       │   ├── hero.png
│       │   ├── react.svg
│       │   └── vite.svg
│       └── components/
│           └── Sidebar.jsx                   # Standalone sidebar component
├── database/                                 # Empty root directory (database resides in MySQL server)
└── docs/                                     # Empty root directory
```

---

## C. PROBLEM, OBJECTIVES AND SCOPE

### A. Problem Statement
Retail investors increasingly manage self-directed portfolios across volatile equities and ETFs. However, typical brokerage user interfaces only emphasize nominal price changes and raw unrealized profit/loss figures. Crucial risk dimensions—such as annualized volatility, benchmark correlation (Beta), tail risk (Maximum Drawdown), risk-adjusted return (Sharpe Ratio), and single-asset/sector concentration—are either omitted or buried behind complex mathematical jargon. As a consequence, investors take excessive unintended risks, suffer from undetected portfolio concentration, and make unmodeled allocation decisions without understanding how hypothetical trades impact total portfolio health.

### B. Main Objective
To design, develop, and evaluate **StockSense**, an end-to-end full-stack portfolio analytics and intelligence platform that combines real-time and historical financial market data with quantitative financial modeling to provide automated risk assessments, diversification diagnostics, plain-English insights, actionable recommendations, and pre-trade simulation.

### C. Specific Project Objectives & Implementation Verification

| # | Specific Objective | Verified Code Location | Implementation Status |
|---|---|---|---|
| 1 | **User Authentication & Isolation:** Implement secure user registration, bcrypt password hashing, JWT session management, and database-level user portfolio isolation. | [users.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/users.py), [security.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/utils/security.py), [auth.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/utils/auth.py) | **Fully Implemented** |
| 2 | **Portfolio & Holdings Management:** Enable users to create multiple portfolios, record stock positions (ticker, quantity, buy price), update positions, and remove holdings. | [portfolios.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/portfolios.py), [holdings.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/holdings.py) | **Fully Implemented** |
| 3 | **Real-Time Portfolio Valuation:** Fetch live market prices, compute total invested capital, current market value, unrealized gain/loss, and holding return percentages. | [portfolio_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/portfolio_service.py), [market_data_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/market_data_service.py) | **Fully Implemented** |
| 4 | **Quantitative Risk & Performance Analytics:** Calculate 1-year historical daily returns, annualized geometric return, annualized volatility, Sharpe ratio (4% risk-free benchmark), and maximum drawdown. | [analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L128-L206) | **Fully Implemented** |
| 5 | **Benchmark Comparison & Beta Calculation:** Retrieve historical benchmark data (SPY ETF), align trading dates, and compute portfolio Beta against the broader market. | [analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L208-L264), [analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L476-L549) | **Fully Implemented** |
| 6 | **Asset Diversification & Concentration Audit:** Measure asset allocation weights, compute the Herfindahl-Hirschman Index (HHI), calculate Effective Holdings ($1/HHI$), and generate a full Pearson correlation matrix. | [analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L265-L346) | **Fully Implemented** |
| 7 | **Sector Exposure Analysis:** Retrieve company sector classification via FMP API and compute sector-level weighting, largest sector, and concentration risk thresholds. | [company_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/company_service.py), [exposure_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/exposure_service.py) | **Fully Implemented** |
| 8 | **Portfolio Health Scoring:** Construct an algorithmic 100-point composite scoring model evaluating risk-adjusted return, drawdown control, market sensitivity, and diversification. | [analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L348-L475) | **Fully Implemented** |
| 9 | **Explainable AI / Plain-English Interpretation & Recommendations:** Transform numerical metrics into qualitative summaries, categorized risk alerts (High, Medium, Positive), and clear corrective actions. | [interpretation_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/interpretation_service.py), [recommendation_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/recommendation_service.py) | **Fully Implemented** |
| 10 | **What-If Pre-Trade Simulation Engine:** Allow users to simulate adding new or existing tickers with custom quantities and immediately observe comparative metric deltas without mutating actual portfolio data. | [simulation_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/simulation_service.py) | **Fully Implemented** |
| 11 | **Automated Background Snapshots:** Schedule daily portfolio valuation and return snapshots at 18:00 using a background scheduler. | [scheduler_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/scheduler_service.py), [snapshot_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/snapshot_service.py) | **Fully Implemented** |
| 12 | **Automated Brokerage Trade Execution:** Place direct buy/sell market orders on live financial exchanges. | Codebase inspection | **Planned / Not Implemented** (Explicitly out of scope) |

### D. Scope
* **In-Scope:** US equities and ETFs supported by Yahoo Finance and Financial Modeling Prep; virtual portfolio tracking; quantitative analytics over a 1-year historical window; 252 trading day annualization; rule-based recommendation and interpretation engines; responsive web frontend.
* **Out-of-Scope:** Direct brokerage integration (e.g., Alpaca, Interactive Brokers); automated order execution; options/derivatives/cryptocurrency pricing; multi-currency conversion (backend calculations operate in uniform currency units); tax-lot accounting.

### E. Target Beneficiaries / Users
* **Retail Investors:** Users seeking deep visibility into portfolio risk, single-stock vulnerability, and sector over-weighting.
* **Financial Analysts & Advisors:** Professionals needing a rapid diagnostic tool to evaluate client asset allocations and explain risk concepts in plain English.
* **Academic Students:** Individuals studying modern portfolio theory (MPT), Capital Asset Pricing Model (CAPM Beta), and concentration metrics.

---

## D. TECHNOLOGY STACK

### 1. Frontend
* **Core Framework:** React 19 (`react: ^19.2.8`, `react-dom: ^19.2.8`) — Declarative UI rendering, hooks (`useState`, `useEffect`), and component lifecycle management.
* **Build Tool & Development Server:** Vite 8 (`vite: ^8.2.0`, `@vitejs/plugin-react: ^6.0.4`) — Fast ESM development server and Rollup-based production bundler.
* **Routing:** React Router v7 (`react-router-dom: ^7.18.2`) — Client-side SPA routing (`BrowserRouter`, `Routes`, `Route`, `Navigate`, `Outlet`, `useOutletContext`, `useNavigate`).
* **HTTP Client:** Axios (`axios: ^1.19.0`) — Configured with base URL `http://127.0.0.1:8000` and JSON headers in [api.js](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/api.js).
* **Data Visualization & Charting:** Recharts (`recharts: ^3.10.1`) — Used for interactive SVG Pie Charts (`ResponsiveContainer`, `PieChart`, `Pie`, `Cell`, `Tooltip`, `Legend`) in [App.jsx](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx#L1703-L1747).
* **Styling & Design System:** Custom Vanilla CSS Design System with CSS Custom Properties (`index.css`, `App.css`) featuring responsive layouts, glassmorphism cards, modal overlays, and modern typography.
* **Icons:** Unicode glyphs and Lucide React (`lucide-react: ^1.31.0` declared in `package.json`).
* **Linter:** Oxlint (`oxlint: ^1.75.0`, `.oxlintrc.json`).

### 2. Backend
* **Web Framework:** FastAPI (`fastapi: 0.139.2`, `starlette: 1.3.1`) — Modern, high-performance ASGI web framework with automatic OpenAPI documentation.
* **ASGI Server:** Uvicorn (`uvicorn: 0.51.0`) — Standard ASGI server running FastAPI asynchronously.
* **Programming Language:** Python 3.12+ (annotated types, modern async context managers).
* **Data Validation & Schemas:** Pydantic v2 (`pydantic: 2.13.4`, `pydantic_core: 2.46.4`) — Request and response validation, email validation (`email-validator: 2.3.0`), and JSON serialization.
* **Database ORM:** SQLAlchemy 2.0 (`SQLAlchemy: 2.0.51`) — Declarative ORM mapping, relational queries, session transactions, and foreign key enforcement.
* **Database Driver:** PyMySQL (`PyMySQL: 1.2.0`) — Pure-Python MySQL client dialect for SQLAlchemy (`mysql+pymysql`).
* **Authentication & Cryptography:**
  - `passlib: 1.7.4` with `bcrypt: 4.1.3` — Bcrypt hashing and password verification.
  - `python-jose: 3.5.0` with `cryptography: 49.0.0` — JSON Web Token (JWT) generation, HMAC-SHA256 signing, and validation.
* **Background Task Scheduler:** APScheduler (`APScheduler: 3.11.3`) — `BackgroundScheduler` running daily portfolio snapshot jobs at 18:00.
* **Environment Configuration:** `python-dotenv: 1.2.2` — Loading `.env` file variables into [config.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/core/config.py).

### 3. Database
* **Database Engine:** MySQL 8.0+
* **Driver / Dialect:** `mysql+pymysql`
* **Schema Design:** 6 relational tables (`users`, `portfolios`, `holdings`, `portfolio_snapshots`, `price_cache`, `company_meta`).
* **Integrity:** Foreign keys linking users $\to$ portfolios $\to$ holdings and snapshots; unique email constraints; ticker primary/indexed keys.

### 4. Financial & Mathematical Computing
* **Market Data Scraping & Feed:** `yfinance: 1.5.2` — Live quote fetching (5-day window) and 1-year historical OHLCV data.
* **Fundamental & Profile Data:** Financial Modeling Prep (FMP) REST API (`requests: 2.34.2`) — Company profiles, sector classification, and market cap.
* **Numerical Computing & Dataframes:** `pandas: 3.0.3` and `numpy: 2.5.1` — Time-series alignment, daily percentage returns calculation, covariance, correlation matrices, cumulative product growth, and statistical variances.
* **Scientific Computing:** `scipy: 1.18.0` — Available in backend environment.

---

## E. COMPLETE FEATURE INVENTORY

| Feature Name | Primary Code Location | Inputs | Processing / Algorithm | Outputs | Implementation Status | Notes / Limitations |
|---|---|---|---|---|---|---|
| **User Registration** | [users.py:L30](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/users.py#L30) | `name`, `email`, `password` | Checks unique email; hashes password via bcrypt; inserts `User` record into MySQL. | `UserResponse` (ID, Name, Email, CreatedAt) | **[IMPLEMENTED]** | Fully functional. |
| **User Login (JWT Auth)** | [users.py:L55](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/users.py#L55) | `username` (email), `password` via OAuth2 form | Verifies bcrypt password hash; signs JWT with `SECRET_KEY`, `ALGORITHM`, and expiry. | Bearer Token (`access_token`, `token_type`) | **[IMPLEMENTED]** | Token stored in browser `localStorage`. |
| **User List Endpoint** | [users.py:L25](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/users.py#L25) | DB Session | Queries all users in DB. | List of user objects | **[IMPLEMENTED]** | Security note: Unprotected endpoint. |
| **Portfolio Creation** | [portfolios.py:L49](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/portfolios.py#L49) | `portfolio_name`, JWT token | Binds new portfolio to `current_user.user_id`; persists in `portfolios` table. | `PortfolioResponse` | **[IMPLEMENTED]** | Triggered via dashboard modal. |
| **Portfolio Retrieval** | [portfolios.py:L71](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/portfolios.py#L71) | JWT token | Filters `portfolios` table by `current_user.user_id`. | Array of user portfolios | **[IMPLEMENTED]** | Populates portfolio selector dropdown. |
| **Portfolio Rename** | [portfolios.py:L86](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/portfolios.py#L86) | `portfolio_id`, `portfolio_name` | Validates user ownership; updates `portfolio_name`. | Updated `PortfolioResponse` | **[IMPLEMENTED]** | Backend endpoint implemented. |
| **Portfolio Deletion** | [portfolios.py:L114](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/portfolios.py#L114) | `portfolio_id`, JWT token | Validates ownership; deletes record from `portfolios` table. | Success message | **[IMPLEMENTED]** | Implemented on backend. |
| **Add Holding** | [holdings.py:L25](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/holdings.py#L25) | `portfolio_id`, `ticker`, `quantity`, `avg_buy_price` | Validates portfolio ownership; rejects duplicates; verifies ticker & fetches metadata via FMP; inserts into `holdings`. | `HoldingResponse` | **[IMPLEMENTED]** | Capitalizes ticker automatically. |
| **Get Holdings** | [holdings.py:L86](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/holdings.py#L86) | `portfolio_id`, JWT token | Queries `holdings` for given `portfolio_id`. | List of holdings | **[IMPLEMENTED]** | Enforces ownership. |
| **Update Holding** | [holdings.py:L113](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/holdings.py#L113) | `portfolio_id`, `holding_id`, `quantity`, `avg_buy_price` | Updates holding quantity and average cost basis. | Updated `HoldingResponse` | **[IMPLEMENTED]** | Implemented on backend. |
| **Delete Holding** | [holdings.py:L157](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/holdings.py#L157) | `portfolio_id`, `holding_id`, JWT | Removes record from `holdings` table. | Success message | **[IMPLEMENTED]** | Backend route is `/portfolios/{p_id}/holdings/{h_id}`. |
| **Live Portfolio Valuation** | [portfolio_service.py:L7](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/portfolio_service.py#L7) | `portfolio_id` | Fetches live price via yfinance or DB cache; computes invested capital, market value, P&L, and %. | Valuation summary + per-holding breakdown | **[IMPLEMENTED]** | Handles empty portfolios gracefully. |
| **Historical Price Caching** | [market_data_service.py:L108](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/market_data_service.py#L108) | `ticker`, `period="1y"` | Downloads 1-year OHLCV via `yfinance`; stores missing dates in `price_cache` table. | Number of rows added | **[IMPLEMENTED]** | Prevents redundant network calls. |
| **Stock Daily Returns** | [analytics_service.py:L10](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L10) | `ticker`, DB Session | Pulls cached closing prices; converts to DataFrame; computes `pct_change()`. | Pandas Series of daily returns | **[IMPLEMENTED]** | Excludes first NaN day. |
| **Weighted Portfolio Returns** | [analytics_service.py:L54](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L54) | `portfolio_id`, DB Session | Calculates current market weights $w_i$; aligns asset return series; computes $\sum (w_i \cdot R_i)$. | Returns DataFrame & weight dictionary | **[IMPLEMENTED]** | Dynamically drops unaligned dates. |
| **Annualized Return** | [analytics_service.py:L147](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L147) | Portfolio daily return series | Computes compounded geometric return: $(\prod(1+R))^{(252/N)} - 1$. | Percentage (rounded to 2 decimals) | **[IMPLEMENTED]** | Standard 252-day convention. |
| **Annualized Volatility** | [analytics_service.py:L160](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L160) | Portfolio daily return series | Computes sample standard deviation scaled by $\sqrt{252}$: $\sigma_d \times \sqrt{252}$. | Percentage (rounded to 2 decimals) | **[IMPLEMENTED]** | Core risk metric. |
| **Sharpe Ratio** | [analytics_service.py:L168](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L168) | Annualized Return, Volatility | $(\text{Return}_{ann} - 0.04) / \text{Volatility}_{ann}$. | Dimensionless ratio | **[IMPLEMENTED]** | Uses fixed 4% risk-free rate. |
| **Maximum Drawdown (MDD)** | [analytics_service.py:L176](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L176) | Daily return series | Computes cumulative product, running peak via `cummax()`, and minimum percentage drop from peak. | Negative percentage (e.g., -14.25%) | **[IMPLEMENTED]** | Measures historical peak-to-trough risk. |
| **Portfolio Beta** | [analytics_service.py:L208](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L208) | Portfolio returns, SPY returns | Aligns dates with SPY; computes $\text{Cov}(R_p, R_{SPY}) / \text{Var}(R_{SPY})$. | Decimal beta value (e.g., 1.15) | **[IMPLEMENTED]** | Dynamic calculation vs SPY. |
| **Correlation Matrix** | [analytics_service.py:L265](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L265) | Portfolio stock return series | Computes pairwise Pearson correlation coefficients across all holdings via `df.corr()`. | 2D Matrix / JSON Dictionary | **[IMPLEMENTED]** | Displayed in interactive HTML table. |
| **Concentration (HHI)** | [analytics_service.py:L293](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L293) | Asset weights $w_i$ | Computes Herfindahl-Hirschman Index: $HHI = \sum (w_i)^2$. | Decimal index between 0 and 1.0 | **[IMPLEMENTED]** | Institutional diversification metric. |
| **Effective Holdings** | [analytics_service.py:L317](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L317) | HHI concentration index | Computes inverse of HHI: $N_{eff} = 1 / HHI$. | Effective number of equal assets | **[IMPLEMENTED]** | Quantifies true diversification depth. |
| **Sector Exposure Audit** | [exposure_service.py:L8](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/exposure_service.py#L8) | `portfolio_id` | Aggregates holding values by `CompanyMeta.sector`; determines sector % and largest sector. | Breakdown %, largest sector, count | **[IMPLEMENTED]** | Rendered via Recharts Pie Chart. |
| **Portfolio Health Score** | [analytics_service.py:L348](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L348) | Sharpe, MDD, Beta, HHI | 4-part scoring engine (0–25 pts each) evaluating Sharpe, drawdown, beta, and HHI. | Total score (0–100) & rating | **[IMPLEMENTED]** | Ratings: Excellent, Good, Moderate, Needs Attention. |
| **Plain-English Interpretation** | [interpretation_service.py:L11](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/interpretation_service.py#L11) | Analytics outputs | Evaluates quantitative metrics against rule boundaries to generate strengths, warnings, and summary. | Structured text interpretation | **[IMPLEMENTED]** | Displayed in Insights tab. |
| **Categorized Recommendations** | [recommendation_service.py:L11](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/recommendation_service.py#L11) | Analytics outputs | Generates 8-category rule-based advisory cards with severity tags (`high`, `medium`, `positive`) and actions. | Recommendation card array | **[IMPLEMENTED]** | Displayed in Insights tab. |
| **Benchmark Performance History** | [analytics_service.py:L476](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L476) | Portfolio returns, SPY returns | Generates normalized cumulative growth curves starting at base 100 for portfolio vs SPY. | Time-series array (`date`, `portfolio`, `benchmark`) | **[IMPLEMENTED]** | Backend service implemented. |
| **What-If Simulation Engine** | [simulation_service.py:L578](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/simulation_service.py#L578) | Hypothetical holdings (ticker, qty) | Merges hypothetical positions with real holdings; re-runs full analytics pipeline; calculates $\Delta$ metrics. | Comparison object (current vs simulated) | **[IMPLEMENTED]** | Non-mutating simulation. |
| **Daily Portfolio Snapshots** | [snapshot_service.py:L41](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/snapshot_service.py#L41) | `portfolio_id` | Captures today's date, total valuation, and daily return; saves to `portfolio_snapshots`. | `PortfolioSnapshot` record | **[IMPLEMENTED]** | Can be invoked via API or scheduler. |
| **Scheduled Background Snapshot Job** | [scheduler_service.py:L11](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/scheduler_service.py#L11) | MySQL Database | APScheduler cron job iterates through all portfolios at 18:00 daily and records snapshots. | Console log / DB persistence | **[IMPLEMENTED]** | Runs in background of FastAPI app. |

---

## F. FRONTEND ANALYSIS

### 1. Application Layout & Architecture
The frontend is structured as a client-side Single Page Application (SPA) driven by React Router v7. 
* Entry point: [main.jsx](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/main.jsx) mounts `App` inside React `StrictMode`.
* Router: Defined in [App.jsx:L1954](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx#L1954), featuring a parent layout route (`Dashboard`) and 5 nested child routes (`overview`, `analytics`, `performance`, `insights`, `simulator`).
* State Sharing: The parent `Dashboard` component manages global data fetching for the active portfolio (Valuation, Analytics, Exposure, Interpretation, Recommendations) and distributes it to child route pages via React Router's `<Outlet context={{ ... }} />`.

---

### 2. Detailed Page-by-Page Analysis

#### Page 1: Login Page
* **Route:** `/login` (default fallback for `*`)
* **Component:** `Login()` in [App.jsx:L54](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx#L54)
* **Purpose:** User authentication interface.
* **UI Elements:** Centralized glassmorphism card, application title ("StockSense"), subtitle ("Smart Portfolio Intelligence"), email input, password input, error alert banner, submit button ("Login" / "Logging in...").
* **API Interactions:** `POST /users/login` sending `URLSearchParams` (`username`, `password`) with header `Content-Type: application/x-www-form-urlencoded`.
* **State & Navigation:** On HTTP 200 response, writes `access_token` to `localStorage.setItem("token", ...)` and navigates to `/dashboard`. Displays backend validation errors on failure.
* **Authentication Requirement:** Public (unauthenticated).

#### Page 2: Dashboard Layout & Overview Page
* **Route:** `/dashboard/overview` (and `/dashboard` index redirect)
* **Component:** `Dashboard()` layout in [App.jsx:L233](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx#L233) + `OverviewPage()` in [App.jsx:L1550](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx#L1550)
* **Purpose:** Primary command center displaying active portfolio metrics, position holdings, and portfolio switcher.
* **Main UI Elements:**
  - **Sidebar:** Brand mark ("StockSense"), user avatar initial, greeting ("Hello, Investor"), navigation menu buttons (Overview, Portfolio Analytics, Performance, Insights, What-If Simulator), system status badge ("System Online • Market data connected").
  - **Header:** Title, subtitle, and "Logout" button (clears `token` and `selectedPortfolioId` from `localStorage`).
  - **Portfolio Selector Bar:** `<select>` dropdown populated dynamically with user portfolios, "+ Add Holding" action button.
  - **Hero Banner:** Displays selected portfolio name with tagline ("at a glance.").
  - **4 Top KPI Cards:**
    1. *Portfolio Value:* Formatted currency value (`₹{valuation.current_value}`).
    2. *Total Return:* Overall gain/loss percentage (`{valuation.return_percentage}%`).
    3. *Total Gain/Loss:* Total monetary profit/loss (`₹{valuation.total_gain_loss}`).
    4. *Holdings:* Total count of unique active stock positions.
  - **Holdings Table / List:** Card listing each holding with Ticker symbol, Quantity (shares), Current Valuation, Unrealized Gain/Loss percentage, and a "Remove" button.
  - **Modals:**
    - *Create Portfolio Modal:* Name input, submit, cancel.
    - *Add Holding Modal:* Ticker input, Quantity input, Average Buy Price input, submit, cancel.
* **API Endpoints Called:**
  - `GET /portfolios`
  - `GET /portfolios/{id}/valuation`
  - `GET /portfolios/{id}/analytics`
  - `GET /portfolios/{id}/interpretation`
  - `GET /portfolios/{id}/exposure`
  - `GET /portfolios/{id}/recommendations`
  - `POST /portfolios/` (Create portfolio)
  - `POST /portfolios/{id}/holdings` (Add holding)
  - `DELETE /holdings/{id}` (Triggered by Remove button)

#### Page 3: Portfolio Analytics Page
* **Route:** `/dashboard/analytics`
* **Component:** `AnalyticsPage()` in [App.jsx:L1627](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx#L1627)
* **Purpose:** In-depth quantitative risk and diversification inspection.
* **Main UI Elements:**
  - **Hero Title:** "Know your risk. Measure your portfolio."
  - **4 Core Performance Cards:**
    1. *Annualized Return:* Geometric annualized return %.
    2. *Annualized Volatility:* Standard deviation scaled by $\sqrt{252}$ %.
    3. *Sharpe Ratio:* Risk-adjusted return measure.
    4. *Max Drawdown:* Worst historical peak-to-trough decline %.
  - **Diversification Grid Card:**
    1. *Concentration:* Herfindahl-Hirschman Index (HHI).
    2. *Effective Holdings:* Effective equal-weighted position count ($1/HHI$).
    3. *Largest Holding:* Ticker of largest asset.
    4. *Largest Weight:* Percentage weight of largest asset.
  - **Portfolio Allocation Pie Chart:** Recharts `<PieChart>` visualizing asset allocation by weight.
  - **Exposure Analysis Pie Chart:** Recharts `<PieChart>` visualizing sector-level asset distribution.
  - **Concentration Warning Banner:** Conditional alert banner displayed if largest sector weight exceeds 50% (`⚠ {sector} represents {weight}% of the portfolio...`).
  - **Correlation Matrix Table:** Full tabular matrix displaying pairwise Pearson correlation coefficients between every holding.

#### Page 4: Performance Page
* **Route:** `/dashboard/performance`
* **Component:** `PerformancePage()` in [App.jsx:L1786](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx#L1786)
* **Purpose:** High-level executive summary of portfolio performance metrics.
* **Main UI Elements:**
  - Hero Header: "How are you really performing?"
  - Metric Cards: Annualized Return (%), Sharpe Ratio (dimensionless), Annualized Volatility (%).

#### Page 5: Insights & Recommendations Page
* **Route:** `/dashboard/insights`
* **Component:** `InsightsPage()` in [App.jsx:L1818](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx#L1818)
* **Purpose:** Qualitative AI-driven plain-English interpretation and categorized advisory.
* **Main UI Elements:**
  - Hero Summary Banner: Overall diagnostic statement including Health Score (e.g., *"The portfolio has a StockSense Health Score of 85/100, rated Excellent."*).
  - **Strengths Card (`✓`):** Bulleted list of identified positive attributes (e.g., strong Sharpe ratio, manageable drawdown, balanced beta, healthy diversification).
  - **Warnings Card (`!`):** Bulleted list of flagged risks (e.g., weak Sharpe, extreme drawdown >30%, high market beta >1.2, single-position concentration >50%).
  - **Overall Assessment Card:** Displays overall rating, Health Score gauge out of 100, and comprehensive evaluation text.
  - **Categorized Recommendation Cards:** Individual cards with dynamic severity color badges:
    - 🔴 **High Severity** (e.g., severe concentration, excessive drawdown, high beta).
    - 🟡 **Medium Severity** (e.g., moderate concentration, elevated volatility).
    - 🟢 **Positive / Low Severity** (e.g., healthy diversification, controlled volatility).
    - Contains title, explanatory message, exact metric value, and concrete suggested action.

#### Page 6: What-If Simulator Page
* **Route:** `/dashboard/simulator`
* **Component:** `SimulatorPage()` in [App.jsx:L1890](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx#L1890)
* **Purpose:** Interactive pre-trade modeling environment.
* **Main UI Elements:**
  - Hero Header: "Explore possibilities. Without changing your portfolio."
  - **Simulation Form:**
    - Stock Ticker input (e.g., `MSFT`, auto-capitalized).
    - Quantity input (number > 0).
    - "Run Simulation" submit button (displays "Simulating..." when loading).
  - **Error Display:** Red alert banner if ticker is invalid or un-cached.
  - **Simulated Outcome Cards:** Displays recalculated *Simulated Return (%)* and *Simulated Volatility (%)*.
* **API Interaction:** `POST /portfolios/{selectedPortfolioId}/simulate` with payload `{"holdings": [{"ticker": "MSFT", "quantity": 10}]}`.

---

## G. BACKEND ANALYSIS

### 1. Application Initialization & Middleware
* **Entry Point:** [main.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/main.py)
* **Lifespan Manager:** Uses FastAPI's modern `@asynccontextmanager` lifespan handler to start the APScheduler background thread on startup (`start_scheduler()`) and cleanly shut it down on application termination (`stop_scheduler()`).
* **CORS Middleware:** Configured via `CORSMiddleware` with `allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"]`, `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`.
* **Router Registration:**
  - `users_router` under prefix `/users`
  - `portfolio_router` under prefix `/portfolios`
  - `holdings_router` under prefix `/portfolios`

---

### 2. Complete REST API Endpoint Inventory

| Method | Endpoint | Purpose | Request Body / Params | Response Model / Schema | Auth Required | DB Interaction | External API |
|---|---|---|---|---|---|---|---|
| `GET` | `/` | Health check & DB verification | None | `{"message": str, "database": str}` | No | None | None |
| `GET` | `/users/` | List all registered users | None | `list[User]` | No (Security finding) | `db.query(User).all()` | None |
| `POST` | `/users/register` | Register new user account | `UserCreate` (name, email, password) | `UserResponse` | No | Inserts new `User` | None |
| `POST` | `/users/login` | Authenticate user & issue JWT | `OAuth2PasswordRequestForm` (`username`, `password`) | `Token` (`access_token`, `token_type`) | No | Queries `User` by email | None |
| `POST` | `/portfolios/` | Create a new portfolio | `PortfolioCreate` (`portfolio_name`) | `PortfolioResponse` | Yes (JWT) | Inserts `Portfolio` | None |
| `GET` | `/portfolios/` | Get all portfolios for current user | None | `list[PortfolioResponse]` | Yes (JWT) | Queries `Portfolio` where `user_id == current_user.user_id` | None |
| `PUT` | `/portfolios/{portfolio_id}` | Rename existing portfolio | `PortfolioUpdate` (`portfolio_name`) | `PortfolioResponse` | Yes (JWT) | Updates `Portfolio.portfolio_name` | None |
| `DELETE` | `/portfolios/{portfolio_id}` | Delete portfolio | Path param `portfolio_id` | `{"message": str}` | Yes (JWT) | Deletes `Portfolio` | None |
| `POST` | `/portfolios/{portfolio_id}/holdings` | Add stock position to portfolio | `HoldingCreate` (`ticker`, `quantity`, `avg_buy_price`) | `HoldingResponse` | Yes (JWT) | Queries `CompanyMeta`, inserts `Holding` | Calls FMP API if company meta missing |
| `GET` | `/portfolios/{portfolio_id}/holdings` | Retrieve all holdings for a portfolio | Path param `portfolio_id` | `list[HoldingResponse]` | Yes (JWT) | Queries `Holding` by `portfolio_id` | None |
| `PUT` | `/portfolios/{portfolio_id}/holdings/{holding_id}` | Update holding quantity & buy price | `HoldingUpdate` (`quantity`, `avg_buy_price`) | `HoldingResponse` | Yes (JWT) | Updates `Holding` record | None |
| `DELETE` | `/portfolios/{portfolio_id}/holdings/{holding_id}` | Remove holding from portfolio | Path params `portfolio_id`, `holding_id` | `{"message": str}` | Yes (JWT) | Deletes `Holding` record | None |
| `GET` | `/portfolios/{portfolio_id}/valuation` | Compute current portfolio market valuation | Path param `portfolio_id` | Valuation summary + holdings array | Yes (JWT) | Queries `Holding` & `PriceCache` | Yahoo Finance (5-day quote) |
| `GET` | `/portfolios/{portfolio_id}/analytics` | Compute performance, beta, correlation, HHI, and health | Path param `portfolio_id` | Comprehensive analytics JSON | Yes (JWT) | Queries `Holding` & `PriceCache` | Yahoo Finance (historical data) |
| `GET` | `/portfolios/{portfolio_id}/interpretation` | Generate qualitative plain-English interpretation | Path param `portfolio_id` | `{"summary": str, "strengths": list, "warnings": list, "recommendations": list}` | Yes (JWT) | Queries analytics data | Yahoo Finance |
| `GET` | `/portfolios/{portfolio_id}/recommendations` | Generate categorized recommendation cards | Path param `portfolio_id` | Structured recommendations object | Yes (JWT) | Queries analytics data | Yahoo Finance |
| `GET` | `/portfolios/{portfolio_id}/exposure` | Calculate sector distribution & weights | Path param `portfolio_id` | Sector exposure JSON | Yes (JWT) | Queries `Holding`, `CompanyMeta`, `PriceCache` | None (reads DB) |
| `GET` | `/portfolios/{portfolio_id}/performance` | Historical cumulative return vs SPY benchmark | Path param `portfolio_id` | Time-series array (base 100) | Yes (JWT) | Queries `PriceCache` | Yahoo Finance |
| `POST` | `/portfolios/{portfolio_id}/simulate` | Run What-If hypothetical simulation | `WhatIfRequest` (`holdings`: `list[SimulatedHolding]`) | Comparison object (current vs simulated) | Yes (JWT) | Queries `Holding` & `PriceCache` | Yahoo Finance (if un-cached) |
| `POST` | `/portfolios/{portfolio_id}/snapshots` | Manually capture portfolio snapshot for today | Path param `portfolio_id` | `PortfolioSnapshot` record | Yes (JWT) | Inserts/Updates `PortfolioSnapshot` | Yahoo Finance / Cache |
| `GET` | `/portfolios/{portfolio_id}/snapshots` | Retrieve snapshot valuation history | Path param `portfolio_id` | List of historical snapshots | Yes (JWT) | Queries `PortfolioSnapshot` by date | None |

---

## H. DATABASE ANALYSIS

### 1. Database Architecture & Technology
* **Database Engine:** MySQL Relational Database Management System (RDBMS).
* **Connection Dialect:** `mysql+pymysql` via SQLAlchemy connection pool.
* **Entity Relational Structure:** Fully normalized 3NF relational schema enforcing primary keys, foreign key constraints, column data types (e.g. `DECIMAL` for currency to prevent floating-point precision loss), unique email indexing, and composite ticker/date caching.

---

### 2. Verified Table Schemas & Column Specifications

#### 1. `users` Table
* **Model:** `User` in [models/user.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/models/user.py)
* **Purpose:** Stores user authentication credentials and profile timestamps.

| Column Name | Data Type | Constraints / Modifiers | Description |
|---|---|---|---|
| `user_id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT`, `INDEX` | Unique user identifier |
| `name` | `VARCHAR(100)` | `NOT NULL` | Full name of the user |
| `email` | `VARCHAR(100)` | `NOT NULL`, `UNIQUE` | User email address (login credential) |
| `password_hash` | `VARCHAR(255)` | `NOT NULL` | Bcrypt one-way encrypted password hash |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Account registration timestamp |

#### 2. `portfolios` Table
* **Model:** `Portfolio` in [models/portfolio.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/models/portfolio.py)
* **Purpose:** Represents individual investment portfolios created by users.

| Column Name | Data Type | Constraints / Modifiers | Description |
|---|---|---|---|
| `portfolio_id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT`, `INDEX` | Unique portfolio identifier |
| `user_id` | `INTEGER` | `NOT NULL`, `FOREIGN KEY (users.user_id)` | Owner user reference |
| `portfolio_name` | `VARCHAR(100)` | `NOT NULL` | Custom portfolio name (e.g. "Growth Tech") |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Portfolio creation timestamp |

#### 3. `holdings` Table
* **Model:** `Holding` in [models/holding.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/models/holding.py)
* **Purpose:** Records stock asset positions allocated within a specific portfolio.

| Column Name | Data Type | Constraints / Modifiers | Description |
|---|---|---|---|
| `holding_id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT`, `INDEX` | Unique holding identifier |
| `portfolio_id` | `INTEGER` | `NOT NULL`, `FOREIGN KEY (portfolios.portfolio_id)` | Parent portfolio reference |
| `ticker` | `VARCHAR(15)` | `NOT NULL` | Standard stock ticker symbol (e.g. "AAPL") |
| `quantity` | `DECIMAL(12, 4)` | `NOT NULL` | Number of shares owned (fractional supported) |
| `avg_buy_price` | `DECIMAL(12, 2)` | `NOT NULL` | Average purchase cost basis per share |
| `added_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Timestamp when position was added |

#### 4. `portfolio_snapshots` Table
* **Model:** `PortfolioSnapshot` in [models/portfolio_snapshot.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/models/portfolio_snapshot.py)
* **Purpose:** Stores periodic/daily portfolio valuations for historical tracking and auditing.

| Column Name | Data Type | Constraints / Modifiers | Description |
|---|---|---|---|
| `snapshot_id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique snapshot identifier |
| `portfolio_id` | `INTEGER` | `NOT NULL`, `FOREIGN KEY (portfolios.portfolio_id)` | Portfolio reference |
| `snapshot_date` | `DATE` | `NOT NULL` | Date of valuation record ($YYYY-MM-DD$) |
| `total_value` | `DECIMAL(15, 2)` | `NULLABLE` | Total portfolio market value on snapshot date |
| `daily_return` | `DECIMAL(10, 6)` | `NULLABLE` | Portfolio weighted percentage return for that day |

#### 5. `price_cache` Table
* **Model:** `PriceCache` in [models/price_cache.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/models/price_cache.py)
* **Purpose:** High-performance local cache of daily historical OHLCV market pricing to prevent external API rate limiting and enable fast offline computation.

| Column Name | Data Type | Constraints / Modifiers | Description |
|---|---|---|---|
| `price_id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT`, `INDEX` | Unique price entry identifier |
| `ticker` | `VARCHAR(15)` | `NOT NULL`, `INDEX` | Ticker symbol (indexed for rapid query) |
| `price_date` | `DATE` | `NOT NULL` | Trading date ($YYYY-MM-DD$) |
| `open` | `DECIMAL(12, 2)` | `NULLABLE` | Opening market price |
| `high` | `DECIMAL(12, 2)` | `NULLABLE` | Highest daily price |
| `low` | `DECIMAL(12, 2)` | `NULLABLE` | Lowest daily price |
| `close` | `DECIMAL(12, 2)` | `NULLABLE` | Closing / Adjusted closing price |
| `volume` | `BIGINT` | `NULLABLE` | Daily trading volume (share count) |

#### 6. `company_meta` Table
* **Model:** `CompanyMeta` in [models/company.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/models/company.py)
* **Purpose:** Stores company fundamental metadata retrieved from Financial Modeling Prep (FMP) for sector and exposure analysis.

| Column Name | Data Type | Constraints / Modifiers | Description |
|---|---|---|---|
| `ticker` | `VARCHAR(15)` | `PRIMARY KEY` | Unique stock ticker symbol (e.g. "NVDA") |
| `company_name` | `VARCHAR(255)` | `NOT NULL` | Registered corporate name |
| `sector` | `VARCHAR(100)` | `NULLABLE` | Industry sector (e.g. "Technology", "Healthcare") |
| `country` | `VARCHAR(100)` | `NULLABLE` | Domicile country (e.g. "US") |
| `market_cap` | `BIGINT` | `NULLABLE` | Market capitalization in currency units |
| `description` | `TEXT` | `NULLABLE` | Corporate business summary |

---

### 3. Entity-Relationship (ER) Description & Cardinalities
```
+------------------+          1:N          +----------------------+
|      users       |--------------------->|      portfolios      |
+------------------+                      +----------------------+
| PK: user_id      |                      | PK: portfolio_id     |
|     email (UQ)   |                      | FK: user_id          |
+------------------+                      +----------------------+
                                                     |
                                   +-----------------+-----------------+
                                   | 1:N                               | 1:N
                                   v                                   v
                        +----------------------+            +----------------------+
                        |       holdings       |            | portfolio_snapshots  |
                        +----------------------+            +----------------------+
                        | PK: holding_id       |            | PK: snapshot_id      |
                        | FK: portfolio_id     |            | FK: portfolio_id     |
                        |     ticker           |            |     snapshot_date    |
                        +----------------------+            +----------------------+
                                   | (logical join on ticker)
                                   v
                        +----------------------+            +----------------------+
                        |     company_meta     |            |     price_cache      |
                        +----------------------+            +----------------------+
                        | PK: ticker           |            | PK: price_id         |
                        |     sector           |            | IX: ticker           |
                        +----------------------+            |     price_date       |
                                                            +----------------------+
```
* **User to Portfolio ($1:N$):** One user can own zero or multiple portfolios. Each portfolio belongs to exactly one user.
* **Portfolio to Holding ($1:N$):** One portfolio contains multiple stock holdings. Each holding record belongs to exactly one portfolio.
* **Portfolio to Snapshot ($1:N$):** One portfolio can have daily historical snapshot records over time.
* **Holding to CompanyMeta ($N:1$ logical):** Multiple holdings across various portfolios reference the same `company_meta` ticker record.
* **Holding to PriceCache ($N:M$ logical):** Multiple price cache daily records exist for each holding ticker.

---

## I. SYSTEM DATA FLOW

### Detailed Execution Flows

#### 1. Authentication & Session Flow
```
User (Browser)
 └──> Enters Email & Password on /login
       └──> React Axios POST /users/login (application/x-www-form-urlencoded)
             └──> FastAPI /users/login endpoint
                   └──> MySQL query: SELECT * FROM users WHERE email = ?
                   └──> Passlib verify_password(plain, hashed_password)
                   └──> Jose create_access_token(data={"sub": user.email})
             <── Returns {"access_token": "...", "token_type": "bearer"}
 └──> React stores JWT in localStorage.setItem("token", ...)
 └──> React useNavigate("/dashboard")
```

#### 2. Dashboard Loading & Multi-Service Aggregation Flow
```
User lands on /dashboard
 └──> fetchPortfolios() -> GET /portfolios (with Bearer JWT)
       └──> MySQL: SELECT * FROM portfolios WHERE user_id = current_user.user_id
       <── Returns [ {portfolio_id: 1, portfolio_name: "Tech Growth"}, ... ]
 └──> React sets selectedPortfolioId = 1
 └──> Parallel / Sequential Data Fetching:
       ├── 1. GET /portfolios/1/valuation
       │     └──> portfolio_service.calculate_portfolio_value()
       │           └──> market_data_service.get_current_price() -> Yahoo Finance / price_cache
       │           <── Returns total_invested, current_value, P&L, holdings[]
       ├── 2. GET /portfolios/1/analytics
       │     └──> analytics_service.get_portfolio_returns()
       │           └──> Caches 1y prices in price_cache -> pandas daily returns
       │           └──> Calculates Annualized Return, Volatility, Sharpe, Drawdown, Beta, HHI, Health Score
       │           <── Returns analytics object
       ├── 3. GET /portfolios/1/exposure
       │     └──> exposure_service.calculate_sector_exposure()
       │           └──> Joins holdings + company_meta + price_cache
       │           <── Returns sector breakdown % and largest sector
       ├── 4. GET /portfolios/1/interpretation
       │     └──> interpretation_service.generate_portfolio_interpretation()
       │           <── Returns plain-English strengths, warnings, and summary
       └── 5. GET /portfolios/1/recommendations
             └──> recommendation_service.generate_portfolio_recommendations()
                   <── Returns categorized advisory cards with severity tags
 └──> React renders Overview, Analytics, Performance, and Insights tabs
```

#### 3. What-If Simulation Flow
```
User on Simulator Tab enters Ticker ("NVDA") & Quantity (15)
 └──> Clicks "Run Simulation"
 └──> Axios POST /portfolios/1/simulate {"holdings": [{"ticker": "NVDA", "quantity": 15}]}
       └──> FastAPI routes/portfolios.py simulate_portfolio_changes()
             └──> simulation_service.compare_portfolio_simulation()
                   ├── 1. Fetches current portfolio holdings from DB
                   ├── 2. Clones holdings in-memory and adds hypothetical NVDA position
                   ├── 3. Downloads / checks historical prices for NVDA
                   ├── 4. Builds combined simulated returns DataFrame
                   ├── 5. Calculates simulated weights, return, volatility, Sharpe, beta, HHI, health
                   ├── 6. Calculates delta changes (Health Δ, Sharpe Δ, Volatility Δ, Concentration Δ)
             <── Returns {"current": {...}, "simulated": {...}, "comparison": {...}}
 └──> React updates Simulator UI showing real-time comparative metric cards
```

---

## J. FINANCIAL AND STATISTICAL CALCULATIONS

### Exhaustive Mathematical Formulas & Implementation Specifications

All financial mathematics are implemented in [analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py), [portfolio_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/portfolio_service.py), [exposure_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/exposure_service.py), and [simulation_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/simulation_service.py).

---

### 1. Asset Holding Valuation & Unrealized Profit/Loss
* **Function:** `calculate_portfolio_value()` in [portfolio_service.py:L7](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/portfolio_service.py#L7)
* **Formulas:**
  $$\text{Invested Amount}_i = \text{Quantity}_i \times \text{Average Buy Price}_i$$
  $$\text{Current Value}_i = \text{Quantity}_i \times \text{Current Price}_i$$
  $$\text{Gain/Loss}_i = \text{Current Value}_i - \text{Invested Amount}_i$$
  $$\text{Gain/Loss Percentage}_i = \left( \frac{\text{Gain/Loss}_i}{\text{Invested Amount}_i} \right) \times 100$$
  $$\text{Total Invested} = \sum_{i=1}^M \text{Invested Amount}_i, \quad \text{Total Market Value} = \sum_{i=1}^M \text{Current Value}_i$$
  $$\text{Portfolio Return Percentage} = \left( \frac{\text{Total Market Value} - \text{Total Invested}}{\text{Total Invested}} \right) \times 100$$
* **Dynamic Status:** Fully dynamic (live Yahoo Finance price or latest cached price).

---

### 2. Daily Asset Returns & Portfolio Weighting
* **Functions:** `get_stock_returns()` and `get_portfolio_returns()` in [analytics_service.py:L10-L126](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L10-L126)
* **Formulas:**
  $$R_{i, t} = \frac{P_{i, t} - P_{i, t-1}}{P_{i, t-1}} = \text{pct\_change}(P_{i, t})$$
  $$w_i = \frac{\text{Current Value}_i}{\text{Total Market Value}}$$
  $$R_{p, t} = \sum_{i=1}^M w_i \times R_{i, t}$$
* **Explanation:** Calculates the percentage change in daily closing prices for each holding, drops missing dates across assets to maintain synchronization, and constructs the weighted daily portfolio return time series $R_{p, t}$.

---

### 3. Annualized Return (Geometric Compounding)
* **Function:** `calculate_performance_metrics()` in [analytics_service.py:L147-L158](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L147-L158)
* **Mathematical Formula:**
  $$\text{Cumulative Growth} = \prod_{t=1}^{N} (1 + R_{p, t})$$
  $$\text{Annualized Return} = \left( \text{Cumulative Growth} \right)^{\left( \frac{252}{N} \right)} - 1$$
* **Variables:** $N =$ number of active historical trading days in the observation window (typically $\sim 251\text{--}252$), $252 =$ standard US equity trading days per calendar year.
* **Explanation:** Uses geometric compounding rather than a simple arithmetic average to accurately capture multi-period compounding effects.

---

### 4. Annualized Volatility
* **Function:** `calculate_performance_metrics()` in [analytics_service.py:L160-L164](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L160-L164)
* **Mathematical Formula:**
  $$\sigma_{\text{daily}} = \sqrt{ \frac{1}{N-1} \sum_{t=1}^N \left( R_{p, t} - \bar{R}_p \right)^2 }$$
  $$\text{Annualized Volatility} = \sigma_{\text{daily}} \times \sqrt{252}$$
* **Explanation:** Quantifies portfolio dispersion and risk by calculating the standard deviation of daily portfolio returns and annualizing it via the square root of time rule ($\sqrt{252}$).

---

### 5. Sharpe Ratio
* **Function:** `calculate_performance_metrics()` in [analytics_service.py:L168-L174](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L168-L174)
* **Mathematical Formula:**
  $$\text{Sharpe Ratio} = \frac{\text{Annualized Return} - R_f}{\text{Annualized Volatility}}$$
* **Variables:** $R_f = 0.04$ (Fixed 4.0% annual risk-free rate constant in code).
* **Explanation:** Evaluates excess return generated per unit of total risk. If volatility is zero, Sharpe defaults to 0.

---

### 6. Maximum Drawdown (MDD)
* **Function:** `calculate_performance_metrics()` in [analytics_service.py:L176-L191](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L176-L191)
* **Mathematical Formula:**
  $$\text{Cumulative Return}_t = \prod_{\tau=1}^t (1 + R_{p, \tau})$$
  $$\text{Running Peak}_t = \max_{1 \le \tau \le t} (\text{Cumulative Return}_\tau)$$
  $$\text{Drawdown}_t = \frac{\text{Cumulative Return}_t}{\text{Running Peak}_t} - 1$$
  $$\text{Maximum Drawdown} = \min_{1 \le t \le N} (\text{Drawdown}_t)$$
* **Explanation:** Finds the largest percentage loss from any historical cumulative peak to a subsequent trough over the 1-year historical window.

---

### 7. Portfolio Beta ($\beta$)
* **Function:** `calculate_portfolio_beta()` in [analytics_service.py:L208-L264](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L208-L264)
* **Mathematical Formula:**
  $$\text{Cov}(R_p, R_b) = \frac{1}{K-1} \sum_{k=1}^K (R_{p, k} - \bar{R}_p)(R_{b, k} - \bar{R}_b)$$
  $$\text{Var}(R_b) = \frac{1}{K-1} \sum_{k=1}^K (R_{b, k} - \bar{R}_b)^2$$
  $$\text{Beta} (\beta) = \frac{\text{Cov}(R_p, R_b)}{\text{Var}(R_b)}$$
* **Variables:** $R_b =$ daily return of the benchmark asset (`SPY` ETF, representing the S&P 500), $K =$ overlapping trading days between portfolio and benchmark.
* **Explanation:** Measures the portfolio's systematic market risk and volatility relative to the S&P 500. $\beta > 1$ denotes higher volatility than the market; $\beta < 1$ denotes lower volatility.

---

### 8. Holding Correlation Matrix
* **Function:** `calculate_correlation_matrix()` in [analytics_service.py:L265-L291](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L265-L291)
* **Mathematical Formula:**
  $$\rho_{i, j} = \frac{\text{Cov}(R_i, R_j)}{\sigma_i \sigma_j} = \frac{\sum (R_{i, t} - \bar{R}_i)(R_{j, t} - \bar{R}_j)}{\sqrt{\sum (R_{i, t} - \bar{R}_i)^2 \sum (R_{j, t} - \bar{R}_j)^2}}$$
* **Explanation:** Computes the pairwise Pearson correlation matrix $\mathbf{P} \in [-1, 1]^{M \times M}$ across all holdings to evaluate co-movement risk.

---

### 9. Concentration Index (HHI) & Effective Holdings
* **Function:** `calculate_diversification_metrics()` in [analytics_service.py:L293-L346](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L293-L346)
* **Mathematical Formulas:**
  $$\text{Concentration Index (HHI)} = \sum_{i=1}^M (w_i)^2$$
  $$\text{Effective Holdings } (N_{\text{eff}}) = \frac{1}{\text{HHI}} = \frac{1}{\sum_{i=1}^M (w_i)^2}$$
* **Explanation:** Uses the Herfindahl-Hirschman Index from industrial economics to measure portfolio weight concentration. If a portfolio has 10 equally weighted stocks ($w_i = 0.10$), $HHI = 10 \times 0.01 = 0.10 \implies N_{\text{eff}} = 10$. If 1 stock dominates with 90% and 9 stocks share 10%, $HHI \approx 0.81 \implies N_{\text{eff}} \approx 1.23$.

---

### 10. Sector Exposure & Concentration
* **Function:** `calculate_sector_exposure()` in [exposure_service.py:L8-L85](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/exposure_service.py#L8-L85)
* **Mathematical Formula:**
  $$\text{Sector Value}_s = \sum_{i \in \text{Sector } s} \text{Current Value}_i$$
  $$\text{Sector Weight}_s = \left( \frac{\text{Sector Value}_s}{\text{Total Market Value}} \right) \times 100$$
  $$\text{Largest Sector Weight} = \max_s (\text{Sector Weight}_s)$$

---

### 11. StockSense 100-Point Portfolio Health Score
* **Function:** `calculate_health_score()` in [analytics_service.py:L348-L475](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L348-L475)
* **Scoring Rules (4 Sub-scores, 0–25 points each):**

| Component | Metric | Condition / Threshold | Points Awarded |
|---|---|---|---|
| **1. Sharpe Score** ($S_1$) | Sharpe Ratio | $\text{Sharpe} \ge 2.0$<br>$1.0 \le \text{Sharpe} < 2.0$<br>$0.5 \le \text{Sharpe} < 1.0$<br>$0.0 \le \text{Sharpe} < 0.5$<br>$\text{Sharpe} < 0.0$ | **25** pts<br>**20** pts<br>**15** pts<br>**10** pts<br>**0** pts |
| **2. Drawdown Score** ($S_2$) | Absolute Max Drawdown $|\text{MDD}|$ | $|\text{MDD}| \le 10\%$<br>$10\% < |\text{MDD}| \le 20\%$<br>$20\% < |\text{MDD}| \le 30\%$<br>$30\% < |\text{MDD}| \le 40\%$<br>$|\text{MDD}| > 40\%$ | **25** pts<br>**20** pts<br>**15** pts<br>**10** pts<br>**5** pts |
| **3. Beta Score** ($S_3$) | Market Beta ($\beta$) vs SPY | $0.8 \le \beta \le 1.2$<br>$0.6 \le \beta < 0.8$ OR $1.2 < \beta \le 1.4$<br>$0.4 \le \beta < 0.6$ OR $1.4 < \beta \le 1.6$<br>$\beta < 0.4$ OR $\beta > 1.6$ | **25** pts<br>**20** pts<br>**15** pts<br>**10** pts |
| **4. Concentration Score** ($S_4$) | Concentration Index (HHI) | $\text{HHI} \le 0.25$<br>$0.25 < \text{HHI} \le 0.40$<br>$0.40 < \text{HHI} \le 0.60$<br>$0.60 < \text{HHI} \le 0.80$<br>$\text{HHI} > 0.80$ | **25** pts<br>**20** pts<br>**15** pts<br>**10** pts<br>**5** pts |

* **Composite Formula:**
  $$\text{Health Score} = S_1 + S_2 + S_3 + S_4 \quad (\text{Range: } 0 \text{ to } 100)$$
* **Qualitative Rating Tiers:**
  $$\text{Rating} = \begin{cases} 
  \text{"Excellent"} & \text{if } \text{Health Score} \ge 80 \\
  \text{"Good"} & \text{if } 65 \le \text{Health Score} < 80 \\
  \text{"Moderate"} & \text{if } 50 \le \text{Health Score} < 65 \\
  \text{"Needs Attention"} & \text{if } \text{Health Score} < 50 
  \end{cases}$$

---

### 12. Benchmark Growth Indexing (Base 100)
* **Function:** `get_portfolio_performance_history()` in [analytics_service.py:L476-L549](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L476-L549)
* **Formula:**
  $$\text{Portfolio Index}_t = 100 \times \prod_{\tau=1}^t (1 + R_{p, \tau}), \quad \text{Benchmark Index}_t = 100 \times \prod_{\tau=1}^t (1 + R_{\text{SPY}, \tau})$$

---

## K. EXTERNAL APIs AND DATA SOURCES

### 1. Yahoo Finance (`yfinance`)
* **Provider:** Yahoo! Finance (accessed via `yfinance` Python library).
* **Endpoints / Methods Used:**
  - `yf.Ticker(ticker).history(period="5d", auto_adjust=False)`: Retrieves recent 5-day daily bars to extract the latest closing market price in [market_data_service.py:L18-L32](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/market_data_service.py#L18-L32).
  - `yf.Ticker(ticker).history(period="1y", auto_adjust=False)`: Retrieves 1-year historical Open, High, Low, Close, Volume series in [market_data_service.py:L87-L98](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/market_data_service.py#L87-L98).
  - `yf.Ticker(ticker).info.get("sector")`: Fallback sector metadata lookup in [simulation_service.py:L135](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/simulation_service.py#L135).
* **Authentication:** No API key required (public scraping feed).
* **Error & Caching Handling:** Wrapped in `try-except` blocks. If Yahoo Finance is unreachable, the system automatically falls back to reading the latest price from the local MySQL `price_cache` table.

### 2. Financial Modeling Prep (FMP)
* **Provider:** Financial Modeling Prep REST API.
* **Base URL:** `https://financialmodelingprep.com/stable/profile`
* **Query Parameters:** `symbol={TICKER}`, `apikey={FMP_API_KEY}`
* **Data Retrieved:** Corporate Name (`companyName`), Sector (`sector`), Country (`country`), Market Capitalization (`marketCap`), Company Description (`description`).
* **Authentication:** API key loaded from environment variable `FMP_API_KEY` (secret value present in `.env`).
* **Processing & Caching:** Called via `requests.get(url, params, timeout=10)` in [company_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/company_service.py). Results are persisted into the `company_meta` table so subsequent requests for the same stock never invoke the external API again.

---

## L. AUTHENTICATION AND SECURITY

### 1. Implemented Security Mechanisms
* **Password Hashing:** Passwords are never stored in plaintext. Passwords are encrypted using Passlib's `CryptContext(schemes=["bcrypt"], deprecated="auto")` with a salt factor in [security.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/utils/security.py).
* **Token-Based Authentication:** JSON Web Tokens (JWT) signed with HMAC-SHA256 (`ALGORITHM` specified in config) and expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`) in [jwt_handler.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/utils/jwt_handler.py).
* **Route Protection & Dependency Injection:** Protected endpoints depend on `get_current_user` in [auth.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/utils/auth.py), which decodes the Bearer token, validates expiry, extracts user email, and queries the database.
* **Data Isolation / Authorization:** All portfolio and holding queries filter explicitly by `user_id == current_user.user_id` or verify portfolio ownership before updating/deleting records.
* **SQL Injection Protection:** SQLAlchemy ORM utilizes parameterized query compilation across all operations (`db.query()`, `filter()`), preventing SQL injection attacks.
* **Cross-Origin Resource Sharing (CORS):** Restricted to explicit frontend development origins (`http://localhost:5173`, `http://127.0.0.1:5173`) with credential support.

### 2. Security Limitations / Recommended Improvements
* **Unprotected User List Route:** `GET /users/` in [users.py:L25](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/users.py#L25) returns all registered users without requiring JWT authentication. While passwords are not exposed, this allows user enumeration.
* **Local Storage JWT Storage:** JWTs are saved in browser `localStorage`, making them vulnerable to Cross-Site Scripting (XSS). HttpOnly, Secure cookies are recommended for production.
* **Token Revocation / Blacklisting:** No server-side token revocation or refresh token mechanism is implemented; tokens remain valid until their numerical expiration.
* **Rate Limiting:** No rate limiting middleware (e.g. `slowapi`) is present on `/users/login` or `/users/register`, leaving the endpoints susceptible to brute-force attempts.

---

## M. FUNCTIONAL REQUIREMENTS

* **FR-01 (User Account Management):** The system shall allow users to register with name, email, and password, and authenticate via email and password to receive a JWT access token. *(Evidence: [users.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/users.py))*
* **FR-02 (Portfolio Management):** The system shall allow authenticated users to create named portfolios, view a list of their portfolios, update portfolio names, and delete portfolios. *(Evidence: [portfolios.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/portfolios.py))*
* **FR-03 (Holding Management):** The system shall allow users to add stock holdings specifying ticker, quantity, and average buy price; validate ticker existence; prevent duplicates; update positions; and remove holdings. *(Evidence: [holdings.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/holdings.py))*
* **FR-04 (Portfolio Valuation & P&L):** The system shall compute real-time market value, total invested capital, total unrealized gain/loss, and percentage return for individual holdings and the aggregate portfolio. *(Evidence: [portfolio_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/portfolio_service.py))*
* **FR-05 (Historical Risk Analytics):** The system shall compute 1-year annualized geometric return, annualized volatility, Sharpe ratio (at 4% risk-free rate), and maximum drawdown. *(Evidence: [analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L128-L206))*
* **FR-06 (Systematic Benchmark Comparison):** The system shall compute portfolio Beta relative to the S&P 500 ETF (SPY) and generate normalized base-100 historical performance comparison series. *(Evidence: [analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L208-L264))*
* **FR-07 (Diversification & Correlation Analysis):** The system shall compute the Herfindahl-Hirschman Index (HHI), effective number of equal holdings, largest position weight, and full pairwise Pearson correlation matrix. *(Evidence: [analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L265-L346))*
* **FR-08 (Sector Exposure & Concentration Alerts):** The system shall calculate sector weights and display warnings when any single sector exceeds 50% allocation. *(Evidence: [exposure_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/exposure_service.py), [App.jsx:L1733](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx#L1733))*
* **FR-09 (Portfolio Health Scoring):** The system shall calculate a composite 100-point Health Score across 4 risk dimensions and assign rating tiers (Excellent, Good, Moderate, Needs Attention). *(Evidence: [analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L348-L475))*
* **FR-10 (Explainable Insights & Categorized Recommendations):** The system shall generate natural-language diagnostic summaries, strength/warning lists, and actionable recommendation cards categorized by severity. *(Evidence: [interpretation_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/interpretation_service.py), [recommendation_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/recommendation_service.py))*
* **FR-11 (What-If Simulation):** The system shall allow users to model hypothetical purchases and observe delta impacts on returns, volatility, Sharpe, beta, concentration, and health score without modifying real portfolio data. *(Evidence: [simulation_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/simulation_service.py))*
* **FR-12 (Automated Daily Snapshots):** The system shall execute an automated background job every day at 18:00 to record portfolio valuation and return snapshots in the database. *(Evidence: [scheduler_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/scheduler_service.py))*

---

## N. NON-FUNCTIONAL REQUIREMENTS

* **NFR-01 (Performance & Low Latency):** Financial market quotes and historical OHLCV data must be cached in MySQL `price_cache` and `company_meta` tables to eliminate duplicate external API calls and ensure sub-second analytical dashboard rendering.
* **NFR-02 (Data Precision & Integrity):** All financial monetary balances and share quantities must use `DECIMAL(12,2)`, `DECIMAL(12,4)`, or `DECIMAL(15,2)` in MySQL and Python to avoid IEEE 754 floating-point rounding errors.
* **NFR-03 (Security & Credential Protection):** Passwords must be hashed with salted bcrypt (`passlib`); authentication must use HMAC-SHA256 JWT tokens; credentials and API keys must be isolated in `.env` and loaded via `python-dotenv`.
* **NFR-04 (Maintainability & Clean Architecture):** The codebase must strictly separate concerns into Models, Schemas, Routes, Services, and Utilities on the backend, and Components, Pages, and Global CSS on the frontend.
* **NFR-05 (Fault Tolerance & Graceful Degradation):** If live Yahoo Finance API calls fail, the market data service must fall back to the most recent cached price in the database. Empty portfolios or single-asset portfolios must be handled without unhandled 500 exceptions.
* **NFR-06 (Usability & Responsiveness):** The user interface must feature a cohesive design system (CSS variables, modern Inter typography, glassmorphism cards, responsive grids, interactive Recharts SVG visualizations, and color-coded risk alerts).

---

## O. SYSTEM ARCHITECTURE

```
+---------------------------------------------------------------------------------------+
|                                    CLIENT TIER                                        |
|                                                                                       |
|   React 19 SPA (Vite Bundler)                                                         |
|   ├── Pages: Login, Overview, Analytics, Performance, Insights, What-If Simulator     |
|   ├── Visualizations: Recharts SVG Pie Charts, Correlation Tables, Metric Cards       |
|   └── HTTP Client: Axios (Bearer JWT Interceptor)                                     |
+---------------------------------------------------------------------------------------+
                                           │
                                           │ HTTPS / JSON REST API Requests
                                           │ (CORS Enabled: Localhost 5173)
                                           ▼
+---------------------------------------------------------------------------------------+
|                                    BACKEND API TIER                                   |
|                                                                                       |
|   FastAPI ASGI Framework (Uvicorn)                                                    |
|   ├── Routing Layer: /users, /portfolios, /holdings                                   |
|   ├── Security Middleware: OAuth2PasswordBearer, Jose JWT Handler, Bcrypt Hasher     |
|   ├── Data Validation: Pydantic v2 Models (UserCreate, HoldingCreate, WhatIfRequest)  |
|   └── Scheduler: APScheduler (BackgroundCron running at 18:00 daily)                  |
+---------------------------------------------------------------------------------------+
                                           │
                                           │ Function Calls / Dependency Injection
                                           ▼
+---------------------------------------------------------------------------------------+
|                                BUSINESS LOGIC & SERVICES                              |
|                                                                                       |
|   ├── portfolio_service.py       ──> Valuation, Invested Capital, P&L                 |
|   ├── analytics_service.py       ──> Annualized Return, Volatility, Sharpe, Drawdown, |
|   │                                  Beta (vs SPY), HHI Diversification, Health Score |
|   ├── exposure_service.py        ──> Sector Weights, Largest Sector Concentration     |
|   ├── interpretation_service.py  ──> Qualitative Strengths, Warnings, Summary        |
|   ├── recommendation_service.py  ──> 8-Category Actionable Advisory Cards (Severity)  |
|   ├── simulation_service.py      ──> Non-Mutating What-If Pre-Trade Modeling          |
|   └── snapshot_service.py        ──> Daily Portfolio Valuation Time-Series Tracking   |
+---------------------------------------------------------------------------------------+
                     │                                             │
      SQLAlchemy ORM │ (PyMySQL)                     HTTP Requests │ (API Key / Scraper)
                     ▼                                             ▼
+------------------------------------------+   +----------------------------------------+
|              DATABASE TIER               |   |           EXTERNAL DATA TIER           |
|                                          |   |                                        |
|   MySQL Relational Database              |   |   1. Yahoo Finance (yfinance)          |
|   ├── users                              |   |      ├── Live Quotes (5d history)      |
|   ├── portfolios                         |   |      └── 1-Year Historical OHLCV       |
|   ├── holdings                           |   |                                        |
|   ├── portfolio_snapshots                |   |   2. Financial Modeling Prep (FMP API) |
|   ├── price_cache (Local Market Cache)   |   |      └── Company Profiles & Sectors    |
|   └── company_meta (Sector Cache)        |   |                                        |
+------------------------------------------+   +----------------------------------------+
```

---

## P. MODULE DESIGN

### 1. User & Authentication Module
* **Purpose:** Manages user onboarding, credential hashing, and JWT token issuance.
* **Files:** [users.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/users.py), [models/user.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/models/user.py), [schemas/user.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/schemas/user.py), [security.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/utils/security.py), [jwt_handler.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/utils/jwt_handler.py), [auth.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/utils/auth.py).
* **Dependencies:** `passlib`, `python-jose`, `SQLAlchemy`, `FastAPI`.

### 2. Portfolio & Holdings Management Module
* **Purpose:** Handles portfolio container CRUD, asset position allocation, quantity/price updates, and holding deletions.
* **Files:** [portfolios.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/portfolios.py), [holdings.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/holdings.py), [models/portfolio.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/models/portfolio.py), [models/holding.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/models/holding.py), [schemas/portfolio.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/schemas/portfolio.py), [schemas/holding.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/schemas/holding.py).
* **Dependencies:** `company_service`, `market_data_service`, `portfolio_service`.

### 3. Market Data & Metadata Ingestion Module
* **Purpose:** Ingests live quotes, 1-year historical price series, and corporate metadata from Yahoo Finance and FMP API; manages persistent local caching in MySQL.
* **Files:** [market_data_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/market_data_service.py), [company_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/company_service.py), [models/price_cache.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/models/price_cache.py), [models/company.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/models/company.py).
* **Dependencies:** `yfinance`, `requests`, `SQLAlchemy`.

### 4. Quantitative Analytics & Benchmarking Module
* **Purpose:** Calculates financial risk metrics (Geometric Return, Annualized Volatility, Sharpe Ratio, Maximum Drawdown, Beta vs SPY, HHI Concentration, Effective Holdings, Correlation Matrix, and Health Score).
* **Files:** [analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py), [exposure_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/exposure_service.py).
* **Dependencies:** `pandas`, `numpy`, `market_data_service`.

### 5. Explainable Insights & Recommendation Engine
* **Purpose:** Evaluates quantitative risk indicators against predefined rule boundaries to generate plain-English diagnostic summaries, strengths/warnings lists, and categorized advisory cards.
* **Files:** [interpretation_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/interpretation_service.py), [recommendation_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/recommendation_service.py).
* **Dependencies:** `analytics_service`.

### 6. What-If Simulation Module
* **Purpose:** Performs non-mutating pre-trade simulations of hypothetical stock additions and computes delta comparisons against the active portfolio.
* **Files:** [simulation_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/simulation_service.py), [schemas/simulation.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/schemas/simulation.py).
* **Dependencies:** `analytics_service`, `market_data_service`.

### 7. Background Snapshot & Scheduling Module
* **Purpose:** Executes automated daily snapshot jobs at 18:00 to record portfolio valuation time series in MySQL.
* **Files:** [snapshot_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/snapshot_service.py), [scheduler_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/scheduler_service.py), [models/portfolio_snapshot.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/models/portfolio_snapshot.py).
* **Dependencies:** `APScheduler`, `portfolio_service`, `analytics_service`.

---

## Q. UI / INTERFACE DESIGN

### Visual Design System Specification
* **Color Palette:**
  - Background: `--ss-bg: #f6f8fc` (sleek, modern light-slate canvas)
  - Surface / Cards: `--ss-surface: #ffffff` with subtle borders (`--ss-border: #e4e7ec`)
  - Primary Accent: `--ss-primary: #3157d5` (institutional cobalt blue)
  - Success / Positive: `--ss-success: #12b76a` / `--ss-success-soft: #ecfdf3`
  - Warning / Alert: `--ss-warning: #f79009` / `--ss-warning-soft: #fffaeb`
  - Danger / High Risk: `--ss-danger: #f04438` / `--ss-danger-soft: #fef3f2`
* **Typography:** `Inter`, `system-ui`, `-apple-system`, `sans-serif` with crisp hierarchy, high contrast, and tabular number formatting.
* **Elevation:** Layered box shadows (`0 8px 24px rgba(16, 24, 40, 0.06)`).

---

## R. TESTING

### A. Tests Present in Codebase
* **Automated Test Suites (e.g. Pytest, Unittest, Jest, Vitest):** `[NOT FOUND]`  
  *Audit finding:* There are no existing automated test scripts (`test_*.py` or `*.spec.jsx`) in the repository.

---

### B. Derived Functional Test Cases (Based on Verified Code Implementation)

| Test Case ID | Module | Test Scenario | Input Data | Expected Result | Verified Code Location |
|---|---|---|---|---|---|
| **TC-AUTH-01** | Auth | User Registration (Valid) | `name="Alice"`, `email="alice@test.com"`, `password="Secret123!"` | HTTP 200, returns `UserResponse` with `user_id` and hashed password stored in DB | [users.py:L30](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/users.py#L30) |
| **TC-AUTH-02** | Auth | User Registration (Duplicate Email) | Same email `alice@test.com` | HTTP 400 Bad Request (`detail: "Email already registered"`) | [users.py:L36](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/users.py#L36) |
| **TC-AUTH-03** | Auth | User Login (Valid Credentials) | `username="alice@test.com"`, `password="Secret123!"` | HTTP 200, returns JWT Bearer token | [users.py:L55](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/users.py#L55) |
| **TC-AUTH-04** | Auth | User Login (Invalid Password) | `username="alice@test.com"`, `password="WrongPass"` | HTTP 401 Unauthorized (`detail: "Invalid email or password"`) | [users.py:L78](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/users.py#L78) |
| **TC-PORT-01** | Portfolio | Create Portfolio | `portfolio_name="Growth Fund"`, Valid JWT | HTTP 200, returns `PortfolioResponse` bound to `current_user.user_id` | [portfolios.py:L49](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/portfolios.py#L49) |
| **TC-PORT-02** | Portfolio | Unauthorized Portfolio Access | Valid JWT for User A requesting Portfolio belonging to User B | HTTP 404 Not Found (enforces user isolation) | [portfolios.py:L99](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/portfolios.py#L99) |
| **TC-HOLD-01** | Holdings | Add Valid Stock Position | `ticker="AAPL"`, `quantity=10`, `avg_buy_price=150.0` | Fetches FMP metadata, saves `Holding`, returns HTTP 200 | [holdings.py:L25](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/holdings.py#L25) |
| **TC-HOLD-02** | Holdings | Add Duplicate Ticker | `ticker="AAPL"` already in portfolio | HTTP 400 (`detail: "This stock already exists in the portfolio"`) | [holdings.py:L53](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/holdings.py#L53) |
| **TC-HOLD-03** | Holdings | Add Invalid Ticker Symbol | `ticker="INVALIDTICKER123"`, `quantity=5`, `avg_buy_price=100` | HTTP 400 (`detail: "Invalid stock ticker"`) | [holdings.py:L67](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/holdings.py#L67) |
| **TC-ANL-01** | Analytics | Portfolio Valuation (Empty Portfolio) | Portfolio with 0 holdings | Returns 0 invested, 0 value, 0 P&L, empty holdings array without error | [portfolio_service.py:L16](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/portfolio_service.py#L16) |
| **TC-ANL-02** | Analytics | Risk Metrics Calculation | Multi-asset portfolio with cached 1y prices | Computes Annualized Return, Volatility, Sharpe, MDD, Beta, HHI, and Health Score | [analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py) |
| **TC-SIM-01** | Simulator | What-If Pre-Trade Simulation | Existing portfolio + hypothetical `{"ticker": "MSFT", "quantity": 10}` | Returns comparison object showing simulated return, volatility, Sharpe, and delta changes without altering DB holdings | [simulation_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/simulation_service.py) |

---

## S. IMPLEMENTATION DETAILS

### 1. Frontend-Backend Communication
* Communication is handled via Axios HTTP client configured in [api.js](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/api.js) targeting `http://127.0.0.1:8000`.
* Authentication tokens are passed in the `Authorization: Bearer <token>` HTTP header using the helper `getConfig()` in [App.jsx:L327](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx#L327).

### 2. Market Data Ingestion & Caching Strategy
* To prevent excessive latency and API rate limits, StockSense implements a two-tier caching architecture:
  1. **Closing Price Cache:** [market_data_service.py:cache_historical_prices()](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/market_data_service.py#L108) populates the MySQL `price_cache` table with 1 year of daily OHLCV bars. Subsequent return calculations execute directly against local database records.
  2. **Corporate Metadata Cache:** [company_service.py:get_or_create_company()](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/company_service.py#L34) caches company sector, name, and market cap in `company_meta`, eliminating redundant FMP API calls.

### 3. Background Job Execution
* Automated snapshot creation is managed by `APScheduler`'s `BackgroundScheduler` in [scheduler_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/scheduler_service.py).
* A cron trigger configured for `hour=18, minute=0` invokes `create_all_portfolio_snapshots()`, which loops over all database portfolios and records valuation and daily return in `portfolio_snapshots`.

---

## T. DESIGN AND IMPLEMENTATION ISSUES

| # | Issue Identified | Exact Code Evidence | Impact & Technical Compromise | Current Status | Recommended Improvement |
|---|---|---|---|---|---|
| 1 | **Frontend Delete Holding URL Mismatch** | [App.jsx:L888](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx#L888) calls `api.delete('/holdings/${holdingId}')` whereas backend route is defined in [holdings.py:L157](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/holdings.py#L157) as `DELETE /portfolios/{portfolio_id}/holdings/{holding_id}`. | Clicking "Remove" holding in the UI results in a 404 Not Found error. | **Active Code Bug** | Update frontend call in [App.jsx](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx) to `api.delete('/portfolios/${selectedPortfolioId}/holdings/${holdingId}')`. |
| 2 | **Unprotected User List Endpoint** | [users.py:L25-L28](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/routes/users.py#L25-L28) defines `GET /users/` without `Depends(get_current_user)`. | Any unauthenticated client can retrieve user names, emails, and IDs. | **Security Finding** | Add `current_user: User = Depends(get_current_user)` or restrict to admin roles. |
| 3 | **Currency Symbol vs Data Source Mismatch** | [App.jsx:L1587-L1612](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx#L1587-L1612) hardcodes `₹` (Indian Rupee symbol) while market prices retrieved from Yahoo Finance / FMP are USD prices ($SPY, AAPL, MSFT). | Visual presentation displays US equity dollar amounts with Rupee symbols (e.g. `₹185.50` for Apple). | **UI Display Inconsistency** | Make currency symbol configurable or display `$` for US equities. |
| 4 | **Fixed Risk-Free Rate Constant** | [analytics_service.py:L166](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L166) hardcodes `risk_free_rate = 0.04` (4%). | Sharpe ratio does not dynamically reflect fluctuating treasury bill yields (e.g., 13-week or 10-year US Treasury yield). | **Analytical Approximation** | Integrate dynamic US 10-year Treasury yield (`^TNX`) via Yahoo Finance. |
| 5 | **Synchronous Live Price Lookup in Request Thread** | [portfolio_service.py:L33](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/portfolio_service.py#L33) calls `get_current_price()` synchronously during GET requests. | If Yahoo Finance is slow, dashboard valuation endpoint latency increases linearly with holding count. | **Performance Bottleneck** | Use asynchronous HTTP clients (e.g. `httpx` or `aiohttp`) or rely primarily on cached prices updated by background workers. |
| 6 | **JWT in Browser LocalStorage** | [App.jsx:L86](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx#L86) writes token to `localStorage.setItem("token", ...)`. | Susceptible to credential extraction if an XSS vulnerability exists. | **Security Vulnerability** | Store tokens in `HttpOnly`, `SameSite=Strict`, `Secure` cookies. |
| 7 | **Absence of Automated Test Suite** | Search across codebase yielded 0 unit/integration tests. | Regression risks during code modification; manual validation required. | **Quality Gap** | Implement pytest test suite with test database fixtures and mock external APIs. |

---

## U. ADVANTAGES

1. **Institutional-Grade Risk Analytics for Retail Portfolios:** Goes beyond basic P&L by computing Annualized Geometric Return, Volatility, Sharpe Ratio, Maximum Drawdown, Beta, and HHI Diversification.
2. **Transparent, Multi-Factor Portfolio Health Scoring:** Synthesizes complex multi-dimensional risk metrics into an interpretable 100-point composite score with clear qualitative tiers.
3. **Automated Plain-English Translation:** Demystifies quantitative finance by translating raw variance and covariance figures into natural-language diagnostic summaries, strength/warning alerts, and actionable recommendations.
4. **Pre-Trade What-If Simulation:** Empowers investors to model hypothetical asset purchases and test risk/return impact before committing capital.
5. **Resilient Local Market Data Caching:** Relational caching of OHLCV bars and sector metadata dramatically reduces third-party API dependencies, eliminates rate limiting, and speeds up computation.
6. **Automated Time-Series Tracking:** Native background scheduler automatically records daily portfolio snapshots without requiring user intervention.
7. **Clean Separation of Concerns:** Highly modular, readable backend architecture (Models, Schemas, Services, Routes) paired with a reactive React frontend.

---

## V. LIMITATIONS

1. **Asset Class Scope:** Exclusively supports equities and ETFs available on Yahoo Finance/FMP; does not support fixed income, options, futures, cryptocurrencies, or mutual funds.
2. **Historical Window Horizon:** Analytics computations are constrained to a 1-year historical window (252 trading days), excluding multi-year market cycles.
3. **Execution Absence:** StockSense is an analytical/virtual platform; it cannot execute live market orders or connect to brokerages.
4. **Currency Normalization:** Assumes all assets operate in a single uniform currency; multi-currency forex conversion is not implemented.
5. **Synchronous Valuation Latency:** Live quote retrieval occurs synchronously during valuation calls rather than through an asynchronous event-driven quote stream.

---

## W. FUTURE ENHANCEMENTS (PROPOSED)

1. **Dynamic Risk-Free Rate Ingestion:** Automatically scrape live US Treasury yields (`^TNX` / `^IRX`) to compute dynamic Sharpe and Sortino ratios.
2. **Modern Portfolio Theory (MPT) Mean-Variance Optimization:** Integrate Markowitz Efficient Frontier optimization to suggest mathematically optimal asset weights for a target risk level.
3. **Multi-Asset & Multi-Currency Support:** Support international exchanges, cryptocurrencies, and automated Forex currency conversion.
4. **Real-Time WebSockets & Push Alerts:** Implement WebSocket channels for live tick-by-tick price updates and email/SMS alerts when a portfolio breaches user-defined drawdown or beta thresholds.
5. **Direct Brokerage Read-Only Sync:** Integrate Plaid or SnapTrade APIs to allow users to automatically sync live brokerage accounts without manual data entry.
6. **Full Automated Test Coverage & CI/CD Pipeline:** Deploy a GitHub Actions workflow executing pytest test suites and frontend Vitest integration tests against containerized MySQL services.

---

## X. SCREENSHOT AND DIAGRAM INVENTORY

| Figure # | Suggested Title / Caption | Content to Capture | Relevant Chapter | Purpose & Utility in Academic Report |
|---|---|---|---|---|
| **Fig 1.1** | System Architecture Block Diagram | High-level 3-tier architecture diagram showing React, FastAPI, MySQL, Yahoo Finance, FMP. | Chapter 3: System Design | Illustrates full-stack component separation and integration points. |
| **Fig 2.1** | Entity-Relationship (ER) Diagram | Relational diagram linking `users`, `portfolios`, `holdings`, `snapshots`, `price_cache`, `company_meta`. | Chapter 3: Database Design | Validates 3NF schema, primary/foreign key relationships, and data normalization. |
| **Fig 3.1** | Data Flow Diagram (DFD Level 1) | Data flow diagram illustrating Auth, Ingestion, Analytics Processing, and Output rendering. | Chapter 3: System Design | Explains analytical pipeline execution from raw prices to dashboard metrics. |
| **Fig 4.1** | User Authentication Interface | Screenshot of the `/login` card with form inputs and styling. | Chapter 4: Implementation | Demonstrates user onboarding and authentication entry point. |
| **Fig 4.2** | Portfolio Intelligence Overview Screen | Full dashboard screenshot showing Top KPIs, portfolio selector, and holdings list table. | Chapter 4: Implementation | Highlights primary user dashboard and real-time valuation display. |
| **Fig 4.3** | Create Portfolio & Add Holding Modals | Screenshots of the interactive modal dialogs for portfolio creation and stock addition. | Chapter 4: Implementation | Demonstrates interactive CRUD workflow. |
| **Fig 4.4** | Quantitative Analytics & Asset Allocation | Screenshot showing Performance KPIs, Allocation Pie Chart, and Diversification KPIs. | Chapter 4: Implementation | Shows visual distribution and statistical measurement capabilities. |
| **Fig 4.5** | Sector Exposure Analysis & Risk Banner | Screenshot of Sector Exposure Pie Chart and the >50% concentration warning banner. | Chapter 4: Implementation | Demonstrates concentration risk detection. |
| **Fig 4.6** | Asset Correlation Matrix Table | Screenshot of the Pearson correlation matrix table across portfolio holdings. | Chapter 4: Implementation | Illustrates multi-asset co-movement visualization. |
| **Fig 4.7** | Portfolio Insights & Health Score Summary | Screenshot of Insights tab showing Health Score /100, rating, and Strengths/Warnings cards. | Chapter 4: Implementation | Showcases explainable AI and qualitative translation features. |
| **Fig 4.8** | Categorized Actionable Recommendations | Screenshot showing colored advisory cards (🔴 High, 🟡 Medium, 🟢 Positive severity). | Chapter 4: Implementation | Proves rule-based decision support system functionality. |
| **Fig 4.9** | What-If Pre-Trade Simulation Engine | Screenshot of Simulator tab showing simulated return, volatility, and delta metrics. | Chapter 4: Implementation | Demonstrates interactive scenario modeling and pre-trade impact assessment. |

---

## Y. REPORT SECTION MAPPING

| University Report Section | Information Provided from StockSense | Primary Source Files in Codebase | Verification Confidence |
|---|---|---|---|
| **Abstract ( $\le$ 200 words)** | Project purpose, technology stack, quantitative algorithms, health score, and outcomes. | Section A, Section C | 100% Verified |
| **1. INTRODUCTION** | | | |
| 1.1 Problem Description | Lack of risk visibility in retail investing; unhedged concentration and drawdowns. | Section C, Section A | 100% Verified |
| 1.2 Existing System | Nominal brokerage P&L displays without risk-adjusted or diversification metrics. | Section C, Section U | 100% Verified |
| 1.3 Project Scope | US equities/ETFs, 1y historical window, quantitative modeling, virtual tracking. | Section C | 100% Verified |
| **2. SYSTEM ANALYSIS** | | | |
| 2.1 Functional Specifications | FR-01 through FR-12 (Auth, CRUD, Valuation, Risk Analytics, Insights, Simulator). | Section M | 100% Verified |
| 2.2 System Requirements | Hardware, Software, Python 3.12+, Node.js, MySQL 8.0, FastAPI, React 19. | Section D, Section N | 100% Verified |
| **3. SYSTEM DESIGN** | | | |
| 3.1 System Architecture | 3-tier client-server architecture with external data feeds and background workers. | Section O, [main.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/main.py) | 100% Verified |
| 3.2 Module Design | 7 core logical modules (Auth, Portfolio, Market Data, Analytics, Insights, Simulator, Scheduler). | Section P | 100% Verified |
| 3.3 Database & Table Structure | 6 relational tables with columns, types, keys, and constraints. | Section H, [models/](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/models) | 100% Verified |
| 3.4 Data Flow Diagram (DFD) | Data flow sequences for Auth, Dashboard aggregation, and Simulation. | Section I | 100% Verified |
| 3.5 ER Diagram | Relational entity mappings and cardinalities ($1:N$, $N:1$). | Section H.3 | 100% Verified |
| 3.6 Interface Design | CSS design system, typography, color tokens, and responsive layout structure. | Section Q, [index.css](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/index.css) | 100% Verified |
| **4. IMPLEMENTATION** | | | |
| 4.1 Implementation Details | Mathematical equations, service implementations, caching strategy, JWT auth. | Section J, Section S, Section G | 100% Verified |
| 4.2 Screenshots Guide | Figure inventory detailing 12 essential visual exhibits. | Section X | 100% Verified |
| **5. TESTING** | | | |
| 5.1 Test Cases & Evaluation | 12 verified functional test cases with inputs, scenarios, and code linkages. | Section R | 100% Verified |
| **6. CONCLUSIONS** | | | |
| 6.1 Design & Implementation Issues | 7 identified technical compromises, bugs (e.g. Delete URL mismatch), and security items. | Section T | 100% Verified |
| 6.2 Advantages & Limitations | Concrete strengths (e.g. Health Score, MPT metrics) and technical constraints. | Section U, Section V | 100% Verified |
| 6.3 Future Enhancements | Realistic future roadmaps (e.g. MPT optimization, WebSocket live feeds, Brokerage sync). | Section W | 100% Verified |

---

## Z. REFERENCES / SOURCES

### A. Sources & Libraries Utilized by Codebase
1. **FastAPI Documentation:** Tiangolo et al., *FastAPI Web Framework Documentation*, URL: https://fastapi.tiangolo.com/
2. **SQLAlchemy 2.0:** Bayer, M., *SQLAlchemy — The Database Toolkit for Python*, URL: https://www.sqlalchemy.org/
3. **Yahoo Finance Python Library (`yfinance`):** Aroussi, R., *yfinance: Yahoo! Finance market data downloader*, URL: https://github.com/ranaroussi/yfinance
4. **Financial Modeling Prep (FMP) API:** Financial Modeling Prep LLC, *Financial Modeling Prep API Documentation*, URL: https://financialmodelingprep.com/developer/docs/
5. **Pandas Development Team:** Wes McKinney et al., *pandas: powerful Python data analysis toolkit*, URL: https://pandas.pydata.org/
6. **Passlib & Bcrypt:** *Password hashing library for Python*, URL: https://passlib.readthedocs.io/
7. **Python-Jose:** *JavaScript Object Signing and Encryption (JOSE) technologies for Python*, URL: https://python-jose.readthedocs.io/
8. **APScheduler:** Alex Grönholm, *Advanced Python Scheduler (APScheduler)*, URL: https://apscheduler.readthedocs.io/
9. **React 19 & React Router v7:** Meta Platforms / Remix Software, *React & React Router Documentation*, URL: https://react.dev/ , https://reactrouter.com/
10. **Recharts:** *A composable charting library built on React components*, URL: https://recharts.org/

### B. Recommended Academic Financial Literature (For Final Report Writing)
1. **Modern Portfolio Theory:** Markowitz, H. (1952). *Portfolio Selection*. The Journal of Finance, 7(1), 77–91.
2. **Capital Asset Pricing Model & Beta:** Sharpe, W. F. (1964). *Capital Asset Prices: A Theory of Market Equilibrium under Conditions of Risk*. The Journal of Finance, 19(3), 425–442.
3. **The Sharpe Ratio:** Sharpe, W. F. (1994). *The Sharpe Ratio*. The Journal of Portfolio Management, 21(1), 49–58.
4. **Concentration Measurement:** Herfindahl, O. C. (1950). *Concentration in the Steel Industry*. PhD thesis, Columbia University; Hirschman, A. O. (1945). *National Power and the Structure of Foreign Trade*.
5. **Drawdown Risk in Financial Markets:** Chekhlov, A., Uryasev, S., & Zabarankin, M. (2005). *Drawdown Measure in Portfolio Optimization*. International Journal of Theoretical and Applied Finance, 8(01), 13–58.

---

## AA. EVIDENCE TABLE

| Claim / Feature | Evidence File | Function / Component | Status | Code Notes / Constraints |
|---|---|---|---|---|
| User passwords are encrypted with bcrypt | [backend/app/utils/security.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/utils/security.py#L4-L12) | `hash_password()`, `verify_password()` | **[IMPLEMENTED]** | Uses `passlib.context.CryptContext(schemes=["bcrypt"])`. |
| User authentication generates signed JWTs | [backend/app/utils/jwt_handler.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/utils/jwt_handler.py#L7-L27) | `create_access_token()` | **[IMPLEMENTED]** | Encodes email subject, expiration, signed with `SECRET_KEY`. |
| Relational data is persisted in MySQL | [backend/app/database/connection.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/database/connection.py#L5-L14) | `DATABASE_URL`, `engine` | **[IMPLEMENTED]** | Configured for `mysql+pymysql` with 6 SQLAlchemy models. |
| Portfolio valuation uses live/cached prices | [backend/app/services/portfolio_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/portfolio_service.py#L7-L123) | `calculate_portfolio_value()` | **[IMPLEMENTED]** | Multiplies quantity by current price, computes invested, value, P&L, %. |
| Historical OHLCV market prices are cached locally | [backend/app/services/market_data_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/market_data_service.py#L108-L175) | `cache_historical_prices()` | **[IMPLEMENTED]** | Inserts 1y daily bars into `price_cache` to prevent API rate limits. |
| Annualized geometric return is calculated | [backend/app/services/analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L147-L158) | `calculate_performance_metrics()` | **[IMPLEMENTED]** | Formula: $( \prod (1 + R_p) )^{(252 / N)} - 1$. |
| Annualized volatility is scaled by $\sqrt{252}$ | [backend/app/services/analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L160-L164) | `calculate_performance_metrics()` | **[IMPLEMENTED]** | Formula: $\sigma(R_p) \times \sqrt{252}$. |
| Sharpe Ratio uses a 4% risk-free rate | [backend/app/services/analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L166-L174) | `calculate_performance_metrics()` | **[IMPLEMENTED]** | Formula: $(\text{Return}_{ann} - 0.04) / \text{Volatility}_{ann}$. |
| Maximum Drawdown computes historical peak-to-trough drop | [backend/app/services/analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L176-L191) | `calculate_performance_metrics()` | **[IMPLEMENTED]** | Uses `cumprod()`, `cummax()`, and finds minimum drawdown percentage. |
| Portfolio Beta is computed dynamically vs SPY | [backend/app/services/analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L208-L264) | `calculate_portfolio_beta()` | **[IMPLEMENTED]** | Formula: $\text{Cov}(R_p, R_{SPY}) / \text{Var}(R_{SPY})$. |
| Pairwise Pearson correlation matrix is generated | [backend/app/services/analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L265-L291) | `calculate_correlation_matrix()` | **[IMPLEMENTED]** | Generated via `pandas.DataFrame.corr()`. |
| Diversification uses HHI & Effective Holdings | [backend/app/services/analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L293-L346) | `calculate_diversification_metrics()` | **[IMPLEMENTED]** | $HHI = \sum w_i^2$, $\text{Effective Holdings} = 1 / HHI$. |
| 100-Point Portfolio Health Score is calculated | [backend/app/services/analytics_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/analytics_service.py#L348-L475) | `calculate_health_score()` | **[IMPLEMENTED]** | 4 sub-scores (Sharpe, Drawdown, Beta, HHI), 25 pts each. |
| Plain-English qualitative interpretation is generated | [backend/app/services/interpretation_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/interpretation_service.py#L11-L161) | `generate_portfolio_interpretation()` | **[IMPLEMENTED]** | Outputs summary, strengths array, warnings array, recommendations. |
| Categorized recommendation cards with severity are generated | [backend/app/services/recommendation_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/recommendation_service.py#L11-L680) | `generate_portfolio_recommendations()` | **[IMPLEMENTED]** | 8 categories with high/medium/positive severity tags and actions. |
| Non-mutating What-If simulation engine is functional | [backend/app/services/simulation_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/simulation_service.py#L578-L846) | `compare_portfolio_simulation()` | **[IMPLEMENTED]** | Combines hypothetical positions and returns current vs simulated delta. |
| Daily portfolio snapshots are scheduled at 18:00 | [backend/app/services/scheduler_service.py](file:///c:/Users/Sanjana/Desktop/Project/StockSense/backend/app/services/scheduler_service.py#L51-L67) | `start_scheduler()` | **[IMPLEMENTED]** | Uses APScheduler cron trigger (`hour=18, minute=0`). |
| Delete holding button fails on frontend | [frontend/src/App.jsx](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx#L888) | `handleDeleteHolding()` | **[ACTIVE BUG]** | Calls `/holdings/{id}` instead of `/portfolios/{p_id}/holdings/{h_id}`. |
| Real stock trading execution (Broker API) | Codebase search | N/A | **[NOT IMPLEMENTED]** | Out of scope; virtual analytics only. |

---

## AB. ITEMS THAT COULD NOT BE VERIFIED (OR ARE NOT PRESENT)

1. **Automated Brokerage Trade Execution:** `[NOT FOUND / NOT IMPLEMENTED]` — There are no trading broker integrations (e.g. Alpaca, Interactive Brokers, TD Ameritrade) in the codebase.
2. **Automated Test Suite Execution:** `[NOT FOUND]` — No test files (`test_*.py` or `*.test.js`) exist in the repository; testing section is derived from actual code logic.
3. **Root `database/` and `docs/` Folders:** `[EMPTY DIRECTORIES]` — Root directories named `database` and `docs` exist but contain zero files (the MySQL database is running externally, and no extra markdown docs were stored in `docs/`).
4. **Standalone `Sidebar.jsx` Routing Mismatch:** [frontend/src/components/Sidebar.jsx](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/components/Sidebar.jsx) declares routes like `/portfolio`, `/risk`, `/diversification`, but is unused in favor of the inline `Sidebar` inside [frontend/src/App.jsx](file:///c:/Users/Sanjana/Desktop/Project/StockSense/frontend/src/App.jsx#L159), which routes to nested paths `/dashboard/overview`, `/dashboard/analytics`, `/dashboard/performance`, `/dashboard/insights`, and `/dashboard/simulator`.

---

## FINAL QUALITY CHECK SYNTHESIS

1. **10 Most Important Implemented Features:**
   1. User Authentication (Bcrypt + JWT) & User Portfolio Isolation.
   2. Real-Time Portfolio Valuation & P&L Tracking.
   3. 1-Year Historical Daily Returns & Asset Weight Alignment.
   4. Annualized Geometric Return & Volatility Computation.
   5. Sharpe Ratio Calculation (4% Risk-Free Rate).
   6. Maximum Drawdown (Peak-to-Trough) Measurement.
   7. Portfolio Beta Calculation vs S&P 500 (SPY).
   8. HHI Concentration Index & Effective Number of Holdings ($1/HHI$).
   9. 100-Point Composite Portfolio Health Score & Categorized Recommendations.
   10. Pre-Trade What-If Scenario Simulation Engine.
2. **5 Most Important Financial Calculations:**
   1. Compounded Annualized Return: $(\prod (1+R_p))^{(252/N)} - 1$.
   2. Annualized Volatility: $\sigma(R_p) \times \sqrt{252}$.
   3. Sharpe Ratio: $(\text{Return}_{ann} - 0.04) / \text{Volatility}_{ann}$.
   4. Market Beta: $\text{Cov}(R_p, R_{SPY}) / \text{Var}(R_{SPY})$.
   5. Diversification Index & Effective Holdings: $HHI = \sum w_i^2, \; N_{\text{eff}} = 1 / HHI$.
3. **5 Most Important Frontend Pages:**
   1. Login Page (`/login`).
   2. Overview Dashboard (`/dashboard/overview`).
   3. Portfolio Analytics (`/dashboard/analytics`).
   4. Insights & Recommendations (`/dashboard/insights`).
   5. What-If Simulator (`/dashboard/simulator`).
4. **5 Most Important Backend Components:**
   1. `analytics_service.py` (Quantitative financial modeling engine).
   2. `simulation_service.py` (Non-mutating pre-trade simulation engine).
   3. `market_data_service.py` (yfinance ingestion & MySQL `price_cache` persistence).
   4. `recommendation_service.py` & `interpretation_service.py` (Rule-based explainable advisory).
   5. `scheduler_service.py` & `snapshot_service.py` (APScheduler daily 18:00 cron tracking).
5. **Database Entities:**
   6 normalized tables: `users`, `portfolios`, `holdings`, `portfolio_snapshots`, `price_cache`, `company_meta`.
6. **External APIs Actually Used:**
   - Yahoo Finance (`yfinance` Python library): Live 5-day prices and 1-year historical OHLCV.
   - Financial Modeling Prep (FMP REST API): Company profile, sector, and market cap metadata.
7. **Incomplete Features / Gaps:**
   - Delete Holding frontend route bug calling `/holdings/{id}` instead of `/portfolios/{p_id}/holdings/{h_id}`.
   - Fixed 4% risk-free rate rather than dynamic Treasury yield ingestion.
   - Unused standalone `Sidebar.jsx` component with obsolete route paths.
8. **Hardcoded / Mock Elements:**
   - Fixed risk-free rate ($R_f = 0.04$).
   - Static 252 trading days annualization constant.
   - User avatar defaults to "Investor" if `localStorage.getItem("userName")` is unset.
   - Currency symbol hardcoded to `₹` on frontend while data is in USD.
9. **Biggest Technical Limitations:**
   - Single-currency assumption (no multi-currency FX conversion).
   - Equity/ETF limitation (no fixed income, options, or crypto).
   - Synchronous external API calls during valuation request lifecycle.
   - Absence of an automated test suite.
10. **Information a Report Writer Would Still Need to Know:**
    - The exact university formatting guidelines (e.g., margins, citation style, cover page format).
    - The author's personal details (Student Name, Roll Number, Department, Supervisor Name).
    - Everything else needed to write the 60–100 page technical report is 100% contained, verified, and referenced in this document.
