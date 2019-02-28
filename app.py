import time
from typing import Callable
import asyncio

import sentry_sdk
from aiohttp import web
from sentry_sdk import capture_exception
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from checks.dp import DPCheck
from checks.fs import FSKafkaCheck, get_fs_messages, FSCheck
from checks.lrs import LrsKafkaCheck, LrsResponseCheck, create_lrs
from settings import settings

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment='healthcheck-stage',
    integrations=[AioHttpIntegration()]
)


async def run_check(f: Callable, **kwargs):
    try:
        return await f(**kwargs)
    except Exception as e:
        capture_exception(e)
        return False


async def healthcheck(_):
    start = int(time.time() * 1000)
    lrs_response, lrs_response_status = await create_lrs(
        settings.LRS_SERVER_URL, settings.LRS_AUTH, settings.UNTI_ID, settings.LRS_CULTURE_VALUE
    )

    await asyncio.sleep(5)

    fs_messages = await get_fs_messages(start)

    result = {
        'lrs': await run_check(
            LrsResponseCheck().check, lrs_response=lrs_response, lrs_response_status=lrs_response_status
        ),
        'lrs-kafka': await run_check(LrsKafkaCheck().check, start=start, lrs_response=lrs_response),
        'fs': await run_check(
            FSCheck(
                settings.FS_SERVER_URL, settings.FS_SERVER_TOKEN, settings.LRS_CULTURE_VALUE
            ).check, fs_messages=fs_messages
        ),
        'fs-kafka': await run_check(FSKafkaCheck().check, fs_messages=fs_messages),
        'dp': await run_check(DPCheck().check, fs_messages=fs_messages)
    }

    status = 200 if all(result.values()) else 500
    return web.json_response(result, status=status)


def init_func(argv):
    app = web.Application()
    app.add_routes([web.get('/healthcheck', healthcheck)])
    return app
