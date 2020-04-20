import asyncpg

async def create_pool():
    return await asyncpg.create_pool()
