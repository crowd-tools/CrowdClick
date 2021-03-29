import logging

# from celery import shared_task

from . import models, celery, web3_providers

logger = logging.getLogger(__name__)


@celery.app.task
def update_task_is_active_balance(task: models.Task = None) -> models.Task:

    if not task:
        task = models.Task.objects.first()
        # TODO Remove
    print(f'Got task to update {task}, id: {task.id}')

    w3_provider: web3_providers.Web3Provider = web3_providers.web3_storage[task.chain]
    is_active, balance = w3_provider.check_balance(task)
    print(f'Got Web3 response; Task: {task}, is_active: {is_active}, balance: {balance}')

    task.is_active_web3 = is_active
    task.remaining_balance = balance

    task.save()
    return task
