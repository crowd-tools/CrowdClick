import asyncio
import io
import logging

from django.conf import settings
from django.core.files.images import ImageFile
from django.utils.text import slugify
from pyppeteer import launch

from crowdclick import celery
from . import models, web3_providers

logger = logging.getLogger(__name__)


async def async_create_task_screenshot(task_id: int):
    task: models.Task = models.Task.objects.get(id=task_id)

    browser = await launch(defaultViewport={'width': 1920, 'height': 1080})
    page = await browser.newPage()
    await page.goto(task.website_link, waitUntil='networkidle0')
    buffer = await page.screenshot(fullPage=True)
    image = ImageFile(io.BytesIO(buffer), name=f'{slugify(task.website_link)}.png')
    task.website_image = image
    task.save()
    await browser.close()
    logger.info(f'Downloaded new image for Task: {task}')


@celery.app.task(bind=True)
def update_task_is_active_balance(self, tx_hash: str = '', task_id: int = 4) -> dict:
    # Could be wrapped:
    # try:
    #     ...
    # except web3.Exception as exc:
    #     # Retry in 5 minutes.
    #     self.retry(countdown=60 * 5, exc=exc)

    task = models.Task.objects.get(id=task_id)
    logger.info(f'Got task to update id: {task}')

    w3_provider: web3_providers.Web3Provider = web3_providers.web3_storage[task.chain]
    if(len(tx_hash) > 0):
        w3_provider.web3.eth.waitForTransactionReceipt(tx_hash)
    is_active, balance = w3_provider.check_balance(task)
    logger.info(f'Got Web3 response; Task: {task}, is_active: {is_active}, remaining_balance: {balance}')

    task.is_active_web3 = is_active
    task.remaining_balance = balance

    task.save()

    return {
        "task_id": task_id,
        "is_active": is_active,
        "remaining_balance": balance,
    }


@celery.app.task(bind=True)
def create_task_screenshot(self, task_id: int):
    asyncio.run(async_create_task_screenshot(task_id=task_id))


@celery.app.task(bind=True)
def push_underlying_usd_price(self):
    """
    For each client in settings, push his price to WEB3
    """
    results = []
    for chain in settings.WEB3_CONFIG.keys():
        w3_provider: web3_providers.Web3Provider = web3_providers.web3_storage[chain]
        value, result, tx_hash = w3_provider.push_underlying_usd_price()
        logger.info(f"Pushed underlying {w3_provider.currency} price {value}"
                    f" result {result} to {chain}, tx: {tx_hash}")
        results.append((value, result, tx_hash))
    return results
