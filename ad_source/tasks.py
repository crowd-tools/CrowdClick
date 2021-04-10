import logging

# from celery import shared_task

from . import models, celery, web3_providers

logger = logging.getLogger(__name__)


@celery.app.task
def update_task_is_active_balance(task_id: int = 4) -> dict:

    task = models.Task.objects.get(id=task_id)
    logger.info(f'Got task to update id: {task}')

    w3_provider: web3_providers.Web3Provider = web3_providers.web3_storage[task.chain]
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
