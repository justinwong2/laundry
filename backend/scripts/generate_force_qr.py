"""Generate force-release QR codes for all machines.

These QR codes use Telegram deep links that open the Mini App
with a force-release action pre-selected.

Usage:
    python scripts/generate_force_qr.py <bot_username>

Example:
    python scripts/generate_force_qr.py Sheares_Laundry_Bot

Output:
    qr_codes/force/E-WASHER-A1.png
    qr_codes/force/E-WASHER-A2.png
    ...
"""

import os
import sys

import qrcode

# Hardcoded machine configuration (matches seed.py)
BLOCKS = ["A", "B", "C", "D", "E"]
MACHINE_CODES = ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2"]
MACHINE_TYPES = ["washer", "dryer"]


def generate_all_qr_codes(bot_username: str, output_dir: str = "qr_codes/force") -> None:
    """Generate force-release QR codes for all 80 machines."""
    os.makedirs(output_dir, exist_ok=True)

    count = 0
    for block in BLOCKS:
        for machine_type in MACHINE_TYPES:
            type_upper = machine_type.upper()
            for code in MACHINE_CODES:
                # QR code format matches seed.py: "{block}-{TYPE}-{code}"
                qr_code_value = f"{block}-{type_upper}-{code}"

                # Telegram deep link format for Mini Apps
                url = f"https://t.me/{bot_username}/laundry?startapp=force_{qr_code_value}"

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(url)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")

                filename = f"{qr_code_value}.png"
                filepath = os.path.join(output_dir, filename)
                img.save(filepath)

                print(f"Generated: {filepath}")
                count += 1

    print(f"\nGenerated {count} force-release QR codes in {output_dir}/")
    print(f"  - {len(BLOCKS)} blocks × {len(MACHINE_TYPES)} types × {len(MACHINE_CODES)} codes = {count} machines")
    print("\nThese QR codes can be printed and attached to physical machines.")
    print("When scanned, they open Telegram and launch the Mini App with force-release UI.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_force_qr.py <bot_username>")
        print("Example: python scripts/generate_force_qr.py Sheares_Laundry_Bot")
        sys.exit(1)

    bot_username = sys.argv[1]
    generate_all_qr_codes(bot_username)
