"""Generate QR codes for all machines."""

import asyncio
import os

import qrcode
from sqlalchemy import select

from laundry.db.database import async_session, init_db
from laundry.models.machine import Machine


async def generate_qr_codes(webapp_url: str, output_dir: str = "qr_codes") -> None:
    """Generate QR codes for all machines."""
    await init_db()

    os.makedirs(output_dir, exist_ok=True)

    async with async_session() as session:
        result = await session.execute(select(Machine))
        machines = result.scalars().all()

        for machine in machines:
            # QR code links to Mini App with machine parameter
            url = f"{webapp_url}?machine={machine.qr_code}"

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            filename = f"{machine.qr_code}.png"
            filepath = os.path.join(output_dir, filename)
            img.save(filepath)

            print(f"Generated: {filepath}")

        print(f"\nGenerated {len(machines)} QR codes in {output_dir}/")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python generate_qr.py <webapp_url>")
        print("Example: python generate_qr.py https://your-app.vercel.app")
        sys.exit(1)

    webapp_url = sys.argv[1]
    asyncio.run(generate_qr_codes(webapp_url))
