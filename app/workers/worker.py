from arq import cron
from arq.connections import RedisSettings
from app.core.config import settings
from app.core.database import SessionLocal
from app.modules.payments.stripe_client import StripeClient
from app.workers.tasks import send_payment_reminders, retry_failed_payments


async def startup(ctx):
    """Initialize resources for the worker."""
    ctx["session_factory"] = SessionLocal
    ctx["stripe_client"] = StripeClient(settings.STRIPE_SECRET_KEY)


async def shutdown(ctx):
    """Cleanup resources."""
    ctx.pop("session_factory", None)
    ctx.pop("stripe_client", None)


class WorkerSettings:
    functions = [send_payment_reminders, retry_failed_payments]
    cron_jobs = [
        cron(send_payment_reminders, hour=9, minute=0),  # 9am daily
        cron(retry_failed_payments, hour={6, 12, 18, 0}),  # every 6h
    ]
    # Parse redis URL
    from urllib.parse import urlparse

    u = urlparse(settings.REDIS_URL)
    redis_settings = RedisSettings(host=u.hostname, port=u.port, password=u.password)

    on_startup = startup
    on_shutdown = shutdown
