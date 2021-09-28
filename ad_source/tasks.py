import asyncio
import io
import logging
import aiohttp

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.files.images import ImageFile
from django.utils.module_loading import import_string
from django.utils.text import slugify

from crowdclick import celery
from . import models, web3_providers

logger = logging.getLogger(__name__)

SCREENSHOT_MACHINE_URL = (
    f'https://api.screenshotmachine.com'
    f'?key={settings.SCREENSHOT_MACHINE_KEY}'
    f'&url={{url}}'
    f'&dimension={settings.SCREENSHOT_MACHINE_DIMENSION}'
)


async def async_create_task_screenshot(task_id: int):
    task: models.Task = await sync_to_async(models.Task.objects.get)(id=task_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(
                SCREENSHOT_MACHINE_URL.format(url=task.website_link),
        ) as response:
            buffer = await response.read()
            image = ImageFile(io.BytesIO(buffer), name=f'{slugify(task.website_link)}.png')
            task.website_image = image
            await sync_to_async(task.save)()

    logger.info(f'Downloaded new image for Task: {task}')


@celery.app.task(bind=True)
def update_task_is_active_balance(
        self,
        task_id: int,
        wait_for_tx: str = '',
        should_be_active: bool = None,
) -> dict:
    """
    :param self: Celery task
    :param task_id: ID of task to update
    :param wait_for_tx: If provided the task will wait for transaction to be mined first
    :param should_be_active: Expected result for retries
    """
    task = models.Task.objects.get(id=task_id)
    logger.info(f'Got task to update: {task}, wait_for_tx: {wait_for_tx}, '
                f'should_be_active: {should_be_active}')

    w3_provider: web3_providers.Web3Provider = web3_providers.web3_storage[task.chain]
    if wait_for_tx:
        logger.info(f'Waiting for TX: {wait_for_tx}')
        provider, *_ = w3_provider.web3
        provider.eth.wait_for_transaction_receipt(wait_for_tx)
    is_active, balance = w3_provider.check_balance(task)
    logger.info(f'Got Web3 response; Task: {task}, is_active: {is_active}, remaining_balance: {balance}')
    if should_be_active is not None and should_be_active != is_active:
        self.retry(
            countdown=settings.WEB3_RETRY_COUNTDOWN,
            max_retries=settings.WEB3_RETRY_COUNTDOWN,
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
