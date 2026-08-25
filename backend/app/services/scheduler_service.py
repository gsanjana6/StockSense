from apscheduler.schedulers.background import BackgroundScheduler

from app.database.session import SessionLocal
from app.models.portfolio import Portfolio
from app.services.snapshot_service import create_portfolio_snapshot


scheduler = BackgroundScheduler()


def create_all_portfolio_snapshots():
    db = SessionLocal()

    try:
        portfolios = db.query(Portfolio).all()

        print(
            f"📸 Snapshot job started "
            f"for {len(portfolios)} portfolio(s)"
        )

        for portfolio in portfolios:
            try:
                snapshot = create_portfolio_snapshot(
                    portfolio.portfolio_id,
                    db
                )

                if snapshot:
                    print(
                        f"✅ Snapshot updated for "
                        f"portfolio {portfolio.portfolio_id}"
                    )

            except Exception as e:
                # Important because one broken portfolio
                # shouldn't stop every other portfolio
                db.rollback()

                print(
                    f"❌ Snapshot failed for portfolio "
                    f"{portfolio.portfolio_id}: {e}"
                )

        print("📸 Snapshot job completed")

    finally:
        db.close()


def start_scheduler():
    if scheduler.running:
        return

    scheduler.add_job(
        create_all_portfolio_snapshots,
        trigger="cron",
        hour=18,
        minute=0,
        id="daily_portfolio_snapshots",
        replace_existing=True
    )

    scheduler.start()

    print("⏰ StockSense scheduler started")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()

        print("🛑 StockSense scheduler stopped")