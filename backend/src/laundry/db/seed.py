"""Seed database with initial data."""

import asyncio

from sqlalchemy import select

from laundry.db.database import async_session, init_db
from laundry.models.machine import Machine


async def seed_block_e_machines() -> None:
    """Seed Block E with 16 machines (8 washers + 8 dryers)."""
    await init_db()

    machine_codes = ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2"]
    machines_to_add = []

    async with async_session() as session:
        # Check if machines already exist
        result = await session.execute(select(Machine).where(Machine.block == "E"))
        existing = result.scalars().all()
        if existing:
            print(f"Block E already has {len(existing)} machines. Skipping seed.")
            return

        # Create washers
        for code in machine_codes:
            machines_to_add.append(
                Machine(
                    code=code,
                    type="washer",
                    block="E",
                    cycle_duration_minutes=45,
                    qr_code=f"E-WASHER-{code}",
                )
            )

        # Create dryers
        for code in machine_codes:
            machines_to_add.append(
                Machine(
                    code=code,
                    type="dryer",
                    block="E",
                    cycle_duration_minutes=60,
                    qr_code=f"E-DRYER-{code}",
                )
            )

        session.add_all(machines_to_add)
        await session.commit()

        print(f"Seeded {len(machines_to_add)} machines for Block E")


if __name__ == "__main__":
    asyncio.run(seed_block_e_machines())
