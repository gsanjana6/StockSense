
import { useOutletContext } from "react-router-dom";

function Insights() {
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

      {/* OVERALL HEALTH */}
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

      {/* STRENGTHS & WARNINGS */}
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

      {/* RECOMMENDATIONS */}
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

export default Insights;
