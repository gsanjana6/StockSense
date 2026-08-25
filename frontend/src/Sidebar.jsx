import { NavLink, useNavigate } from "react-router-dom";

function Sidebar() {
  const navigate = useNavigate();
  const userName = localStorage.getItem("userName") || "Investor";

  const navigation = [
    { label: "Overview", path: "/dashboard/overview", icon: "⌂" },
    { label: "Portfolio Analytics", path: "/dashboard/analytics", icon: "◈" },
    { label: "Performance", path: "/dashboard/performance", icon: "↗" },
    { label: "Insights", path: "/dashboard/insights", icon: "✦" },
    { label: "What-If Simulator", path: "/dashboard/simulator", icon: "◇" },
  ];

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("selectedPortfolioId");
    navigate("/login");
  };

  return (
    <aside className="ss-sidebar">
      <div className="ss-brand">
        <div className="ss-brand-mark">S</div>
        <div>
          <div className="ss-brand-name">StockSense</div>
          <div className="ss-brand-subtitle">Portfolio Intelligence</div>
        </div>
      </div>

      <div className="ss-user">
        <div className="ss-user-avatar">
          {userName.charAt(0).toUpperCase()}
        </div>
        <div className="ss-user-info">
          <span className="ss-user-hello">Hello,</span>
          <span className="ss-user-name">{userName}</span>
        </div>
      </div>

      <nav className="ss-navigation">
        <div className="ss-nav-label">Main</div>

        {navigation.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `ss-nav-item ${isActive ? "ss-nav-item-active" : ""}`
            }
          >
            <span className="ss-nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="ss-sidebar-footer">
        <div className="ss-footer-badge">
          <span className="ss-footer-dot" />
          Analytics engine online
        </div>

        <button className="ss-logout-button" onClick={logout}>
          <span className="ss-nav-icon">⏻</span>
          <span>Log out</span>
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
