import asyncio
import argparse
import shlex
from enum import Enum
from typing import List

import aiohttp


class JobStatus(Enum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


async def run(command: List[str]) -> JobStatus:
    process = await asyncio.create_subprocess_exec(*command)
    await process.wait()
    if process.returncode == 0:
        return JobStatus.COMPLETED
    else:
        return JobStatus.FAILED


async def send_status(url: str, status: JobStatus) -> None:
    payload = {"status": status.value}
    async with aiohttp.ClientSession() as session:
        await session.put(url, json=payload)


async def heartbeat(url: str, period: float) -> None:
    async with aiohttp.ClientSession() as session:
        while True:
            await session.put(url)
            await asyncio.sleep(period)


async def main(
    command: List[str], tracking_server_url: str, heartbeat_period: float
) -> None:

    status_url = f"{tracking_server_url}/status"
    heartbeat_url = f"{tracking_server_url}/heartbeat"

    await send_status(status_url, JobStatus.STARTED)

    # Use asyncio.create_task to start running the heartbeat coroutine
    # immediately
    heartbeat_future = asyncio.create_task(
        heartbeat(heartbeat_url, heartbeat_period)
    )

    # Run command
    final_status = await run(command)
    await send_status(status_url, final_status)

    # Cancel heartbeat future (as it is on an infinite loop) and wait for it to
    # finish
    heartbeat_future.cancel()
    try:
        await heartbeat_future
    except asyncio.CancelledError:
        pass


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="The job command to run")
    parser.add_argument("tracking_url", help="The URL of the tracking server")
    parser.add_argument(
        "--heartbeat-period",
        type=float,
        default=1.,
        help="The period on which to send heartbeats to the tracking server "
        "(in seconds)",
    )
    args = parser.parse_args()

    command_parts = shlex.split(args.command)

    asyncio.run(main(command_parts, args.tracking_url, args.heartbeat_period))


if __name__ == "__main__":
    cli()
