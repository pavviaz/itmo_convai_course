from fastapi import HTTPException
import aiohttp

from app.config import TIMEOUT


async def llm_request(llm_addr, pload):
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    async with aiohttp.ClientSession() as session:
        async with session.post(llm_addr, json=pload, timeout=timeout) as response:
            print(pload, flush=True)
            if response.status != 200:
                raise HTTPException(status_code=500, detail="Worker error")

            resp = await response.json()

    resp = resp["answer"]
    return resp
