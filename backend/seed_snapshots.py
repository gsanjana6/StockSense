from datetime import date, timedelta
from app.database.session import SessionLocal
from app.models.portfolio_snapshot import PortfolioSnapshot
from app.models.portfolio import Portfolio
from app.services.portfolio_service import calculate_portfolio_value

def seed_snapshots():
    db = SessionLocal()
    try:
        portfolios = db.query(Portfolio).all()
        for p in portfolios:
            val = calculate_portfolio_value(p.portfolio_id, db)
            if not val or not val.get("current_value"):
                continue
            
            current_val = float(val["current_value"])
            
            # Yesterday's snapshot (slightly lower to show a positive gain)
            yesterday = date.today() - timedelta(days=1)
            prev_snapshot = db.query(PortfolioSnapshot).filter(
                PortfolioSnapshot.portfolio_id == p.portfolio_id,
                PortfolioSnapshot.snapshot_date == yesterday
            ).first()

            if not prev_snapshot:
                db.add(PortfolioSnapshot(
                    portfolio_id=p.portfolio_id,
                    snapshot_date=yesterday,
                    total_value=round(current_val * 0.985, 2), # 1.5% less
                    daily_return=0.015
                ))

            # Today's snapshot
            today_snapshot = db.query(PortfolioSnapshot).filter(
                PortfolioSnapshot.portfolio_id == p.portfolio_id,
                PortfolioSnapshot.snapshot_date == date.today()
            ).first()

            if not today_snapshot:
                db.add(PortfolioSnapshot(
                    portfolio_id=p.portfolio_id,
                    snapshot_date=date.today(),
                    total_value=current_val,
                    daily_return=0.015
                ))

        db.commit()
        print("Successfully seeded snapshots!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_snapshots()