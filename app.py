import time
import random
from typing import Callable
import asyncio

import sentry_sdk
from aiohttp import web
from sentry_sdk import capture_exception
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from checks.dp import DPCheck
from checks.fs import FSKafkaCheck, get_fs_messages, FSCheck
from checks.lrs import LrsKafkaCheck, LrsResponseCheck, create_lrs
from checks.postgres import PostgresResponseCheck
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

async def db_healthcheck(_):
    result = await PostgresResponseCheck(
        settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER,  settings.DB_PASSWORD
    ).check()
    status = 200 if result else 500

    return web.Response(status=status)

async def healthcheck(_):
    
    start = int(time.time() * 1000)
    
    lrs_culture_value = { settings.LRS_CULTURE_COMPETENCE: random.randint(200,300) }

    lrs_response, lrs_response_status = await create_lrs(
        settings.LRS_SERVER_URL, settings.LRS_AUTH, settings.UNTI_ID, lrs_culture_value
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
                settings.FS_SERVER_URL, settings.FS_SERVER_TOKEN, lrs_culture_value
            ).check, fs_messages=fs_messages
        ),
        'fs-kafka': await run_check(FSKafkaCheck().check, fs_messages=fs_messages),
        'dp:': await run_check(
            DPCheck(
                settings.DP_SERVER_URL, 
                settings.DP_SERVER_TOKEN, 
                settings.UNTI_ID,
                settings.DP_COMPETENCE_UUID,
                lrs_culture_value
            ).check,
            create_entry=settings.DP_CREATE_ENTRY
        )
    }

    status = 200 if all(result.values()) else 500
    return web.json_response(result, status=status)


def init_func():
    app = web.Application()
    app.add_routes([
        web.get('/healthcheck', healthcheck),
        web.get('/healthcheck/db', db_healthcheck),
    ])
    return app
