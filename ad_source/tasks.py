import asyncio
import io
import logging

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.files.images import ImageFile
from django.utils.module_loading import import_string
from django.utils.text import slugify
from pyppeteer import launch

from crowdclick import celery
from . import models, web3_providers

logger = logging.getLogger(__name__)

RETRY_COUNTDOWN = 20 * 1  # 20 seconds


async def async_create_task_screenshot(task_id: int):
    task: models.Task = await sync_to_async(models.Task.objects.get)(id=task_id)

    browser = await launch(defaultViewport={'width': 1920, 'height': 1080})

    try:
        page = await browser.newPage()
        await page.goto(task.website_link, waitUntil='domcontentloaded')
        buffer = await page.screenshot()
        image = ImageFile(io.BytesIO(buffer), name=f'{slugify(task.website_link)}.png')
        task.website_image = image
        await sync_to_async(task.save)()
    finally:
        await browser.close()

    logger.info(f'Downloaded new image for Task: {task}')


@celery.app.task(bind=True)
def update_task_is_active_balance(
        self,
        task_id: int,
        wait_for_tx: str = '',
        should_be_active: bool = None,
        retry: int = 0,
) -> dict:
    """
    :param self: Celery task
    :param task_id: ID of task to update
    :param wait_for_tx: If provided the task will wait for transaction to be mined first
    :param should_be_active: Expected result for retries
    :param retry: Number of retries
    """
    task = models.Task.objects.get(id=task_id)
    logger.info(f'Got task to update: {task}, wait_for_tx: {wait_for_tx}, '
                f'should_be_active: {should_be_active}, retry: {retry}')

    w3_provider: web3_providers.Web3Provider = web3_providers.web3_storage[task.chain]
    if wait_for_tx:
        logger.info(f'Waiting for TX: {wait_for_tx}')
        w3_provider.web3.eth.waitForTransactionReceipt(wait_for_tx)
    is_active, balance = w3_provider.check_balance(task)
    logger.info(f'Got Web3 response; Task: {task}, is_active: {is_active}, remaining_balance: {balance}')
    if should_be_active is not None and should_be_active != is_active and retry > 0:
        self.retry(
            kwargs={'task_id': task_id, 'should_be_active': should_be_active, 'retry': retry - 1},
            countdown=RETRY_COUNTDOWN, max_retries=10
        )

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


@celery.app.task
def update_rates(backend=settings.EXCHANGE_BACKEND, **kwargs):
    """
    Update rates and push underlying price to WEB3
    """
    backend = import_string(backend)()
    backend.update_rates(**kwargs)
    # results = []
    # for chain in settings.WEB3_CONFIG.keys():
    #     w3_provider: web3_providers.Web3Provider = web3_providers.web3_storage[chain]
    #     value, result, tx_hash = w3_provider.push_underlying_usd_price()
    #     logger.info(f"Pushed underlying {w3_provider.currency} price {value}"
    #                 f" result {result} to {chain}, tx: {tx_hash}")
    #     results.append((value, result, tx_hash))
    # return results
