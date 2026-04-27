"""Seed database with initial data."""

import asyncio

from sqlalchemy import select

from laundry.db.database import async_session, init_db
from laundry.models.machine import Machine
from laundry.models.powerup import Powerup

BLOCKS = ["A", "B", "C", "D", "E"]
MACHINE_CODES = ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2"]


async def seed_block_machines(block: str) -> int:
    """Seed a single block with 16 machines (8 washers + 8 dryers).

    Returns the number of machines created.
    """
    async with async_session() as session:
        # Check if machines already exist for this block
        result = await session.execute(select(Machine).where(Machine.block == block))
        existing = result.scalars().all()
        if existing:
            print(f"Block {block} already has {len(existing)} machines. Skipping.")
            return 0

        machines_to_add = []

        # Create washers
        for code in MACHINE_CODES:
            machines_to_add.append(
                Machine(
                    code=code,
                    type="washer",
                    block=block,
                    cycle_duration_minutes=30,
                    qr_code=f"{block}-WASHER-{code}",
                )
            )

        # Create dryers
        for code in MACHINE_CODES:
            machines_to_add.append(
                Machine(
                    code=code,
                    type="dryer",
                    block=block,
                    cycle_duration_minutes=30,
                    qr_code=f"{block}-DRYER-{code}",
                )
            )

        session.add_all(machines_to_add)
        await session.commit()

        print(f"Seeded {len(machines_to_add)} machines for Block {block}")
        return len(machines_to_add)


async def seed_powerups() -> int:
    """
    Seed powerup definitions.

    These are the "products" in the shop - what users can buy.
    The actual inventory (who owns what) is stored in user_powerups table.

    Returns the number of powerups created.
    """
    async with async_session() as session:
        # Check if already seeded
        result = await session.execute(select(Powerup))
        existing = result.scalars().all()
        if existing:
            print(f"Powerups already seeded ({len(existing)} found). Skipping.")
            return 0

        powerups = [
            Powerup(
                type="spam_bomb",
                name="Spam Bomb",
                description="Send 20 messages over 1 minute!",
                cost=20,
                icon="💣",
            ),
            Powerup(
                type="name_shame",
                name="Name & Shame",
                description="Post to the group chat calling them out!",
                cost=40,
                icon="📢",
            ),
        ]

        session.add_all(powerups)
        await session.commit()

        print(f"Seeded {len(powerups)} powerups")
        return len(powerups)


async def seed_all_blocks() -> None:
    """Seed all blocks (A-E) with machines."""
    await init_db()

    total = 0
    for block in BLOCKS:
        total += await seed_block_machines(block)

    print(f"\nTotal: {total} machines seeded across {len(BLOCKS)} blocks")

    # Also seed powerups
    await seed_powerups()


async def seed_block_e_machines() -> None:
    """Seed Block E only (for backwards compatibility)."""
    await init_db()
    await seed_block_machines("E")
    await seed_powerups()  # Also seed powerups


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        arg = sys.argv[1].upper()
        if arg == "ALL":
            asyncio.run(seed_all_blocks())
        elif arg in BLOCKS:
            asyncio.run(init_db())
            asyncio.run(seed_block_machines(arg))
        else:
            print("Usage: python -m laundry.db.seed [BLOCK|ALL]")
            print(f"  BLOCK: One of {BLOCKS}")
            print("  ALL: Seed all blocks")
            sys.exit(1)
    else:
        # Default: seed all blocks
        asyncio.run(seed_all_blocks())
