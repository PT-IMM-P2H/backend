from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import asyncio

from app.scheduler.jobs import (
    reset_daily_p2h_tracker,
    check_expiry_dates,
    retry_failed_notifications
)

logger = logging.getLogger(__name__)

# Create scheduler instance
scheduler = BackgroundScheduler()


def run_async_job(job_func):
    """
    Wrapper to run async functions in scheduler.
    """
    asyncio.run(job_func())


def start_scheduler():
    """
    Start the APScheduler with all configured jobs.
    """
    try:
        # Job 1: Reset P2H tracker daily at 5:00 AM WITA
        scheduler.add_job(
            func=lambda: run_async_job(reset_daily_p2h_tracker),
            trigger=CronTrigger(hour=5, minute=0, timezone="Asia/Makassar"),
            id="reset_p2h_tracker",
            name="Reset Daily P2H Tracker",
            replace_existing=True
        )
        logger.info("✅ Scheduled: Reset P2H Tracker at 05:00 WITA daily")
        
        # Job 2: Check expiry dates daily at 5:00 AM WITA
        scheduler.add_job(
            func=lambda: run_async_job(check_expiry_dates),
            trigger=CronTrigger(hour=5, minute=0, timezone="Asia/Makassar"),
            id="check_expiry",
            name="Check STNK/KIR Expiry",
            replace_existing=True
        )
        logger.info("✅ Scheduled: Check Expiry Dates at 05:00 WITA daily")
        
        # Job 3: Retry failed notifications every hour
        scheduler.add_job(
            func=lambda: run_async_job(retry_failed_notifications),
            trigger=CronTrigger(minute=0, timezone="Asia/Makassar"),
            id="retry_notifications",
            name="Retry Failed Notifications",
            replace_existing=True
        )
        logger.info("✅ Scheduled: Retry Failed Notifications hourly")
        
        # Start the scheduler
        scheduler.start()
        logger.info("🚀 APScheduler started successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {str(e)}")
        raise


def stop_scheduler():
    """
    Stop the scheduler.
    """
    try:
        scheduler.shutdown()
        logger.info("🛑 Scheduler stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping scheduler: {str(e)}")
