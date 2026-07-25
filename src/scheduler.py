import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from src.batch import run_batch_screening


def scheduled_job():
    """Job executed post-market close at 17:00 ICT."""
    print("Executing scheduled post-market SET100 batch screening job...")
    run_batch_screening(max_workers=3, notify=True)


def start_scheduler():
    """Configure and start APScheduler for post-market close screening."""
    bangkok_tz = pytz.timezone("Asia/Bangkok")
    scheduler = BlockingScheduler(timezone=bangkok_tz)

    # Trigger: Monday-Friday at 17:00 ICT (Asia/Bangkok timezone)
    trigger = CronTrigger(day_of_week="mon-fri", hour=17, minute=0, timezone=bangkok_tz)
    scheduler.add_job(scheduled_job, trigger, id="set100_daily_batch")

    print("📅 APScheduler initialized: SET100 Batch Screening scheduled daily at 17:00 ICT (Mon-Fri).")
    print("Press Ctrl+C to exit scheduler.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")


if __name__ == "__main__":
    start_scheduler()
