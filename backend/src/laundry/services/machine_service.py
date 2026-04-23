"""Machine service - business logic for machine operations."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from laundry.db.database import async_session
from laundry.models.machine import Machine
from laundry.models.session import LaundrySession


class MachineService:
    """Service for machine-related operations."""

    @staticmethod
    async def get_all_with_status() -> list[dict]:
        """Get all machines with their current session status."""
        async with async_session() as session:
            result = await session.execute(
                select(Machine).options(
                    selectinload(Machine.sessions).selectinload(LaundrySession.user)
                )
            )
            machines = result.scalars().all()

            response = []
            for machine in machines:
                active_session = next(
                    (s for s in machine.sessions if s.ended_at is None), None
                )
                response.append(
                    {
                        "id": machine.id,
                        "code": machine.code,
                        "type": machine.type,
                        "block": machine.block,
                        "cycle_duration_minutes": machine.cycle_duration_minutes,
                        "qr_code": machine.qr_code,
                        "current_session": (
                            {
                                "id": active_session.id,
                                "user_id": active_session.user_id,
                                "machine_id": active_session.machine_id,
                                "started_at": active_session.started_at,
                                "expected_end_at": active_session.expected_end_at,
                                "ended_at": active_session.ended_at,
                                "message": active_session.message,
                                "username": (
                                    active_session.user.username
                                    if active_session.user
                                    else None
                                ),
                            }
                            if active_session
                            else None
                        ),
                    }
                )
            return response

    @staticmethod
    async def get_by_id(machine_id: int) -> dict | None:
        """Get a single machine by ID."""
        async with async_session() as session:
            result = await session.execute(
                select(Machine)
                .where(Machine.id == machine_id)
                .options(
                    selectinload(Machine.sessions).selectinload(LaundrySession.user)
                )
            )
            machine = result.scalar_one_or_none()
            if not machine:
                return None

            active_session = next(
                (s for s in machine.sessions if s.ended_at is None), None
            )
            return {
                "id": machine.id,
                "code": machine.code,
                "type": machine.type,
                "block": machine.block,
                "cycle_duration_minutes": machine.cycle_duration_minutes,
                "qr_code": machine.qr_code,
                "current_session": (
                    {
                        "id": active_session.id,
                        "user_id": active_session.user_id,
                        "machine_id": active_session.machine_id,
                        "started_at": active_session.started_at,
                        "expected_end_at": active_session.expected_end_at,
                        "ended_at": active_session.ended_at,
                        "message": active_session.message,
                        "username": (
                            active_session.user.username
                            if active_session.user
                            else None
                        ),
                    }
                    if active_session
                    else None
                ),
            }
