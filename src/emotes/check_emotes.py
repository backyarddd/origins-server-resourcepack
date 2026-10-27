"""Validate the emote sprites: exactly the 20 catalog ids, each 16x16 RGBA with binary alpha.

Run: python -I check_emotes.py
"""
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent

# Emotes table in packdev/server/specs/origins-cosmetics/catalog-v2.md
EMOTE_IDS = [
    "emote_laugh", "emote_skull", "emote_cry", "emote_heart_eyes", "emote_cool",
    "emote_angry", "emote_clown", "emote_thinking", "emote_shock", "emote_sleep",
    "emote_fire", "emote_hundred", "emote_gg", "emote_w", "emote_l",
    "emote_question", "emote_exclaim", "emote_thumbs_up", "emote_sweat", "emote_party",
]


def main() -> int:
    errors: list[str] = []
    # Only PNGs are checked; other files in the folder (CREDITS.md, this script) are ignored.
    found = sorted(p.stem for p in HERE.iterdir() if p.is_file() and p.suffix.lower() == ".png")
    for missing in sorted(set(EMOTE_IDS) - set(found)):
        errors.append(f"missing: {missing}.png")
    for extra in sorted(set(found) - set(EMOTE_IDS)):
        errors.append(f"unexpected: {extra}.png")

    for emote_id in EMOTE_IDS:
        path = HERE / f"{emote_id}.png"
        if not path.is_file():
            continue
        with Image.open(path) as im:
            if im.format != "PNG":
                errors.append(f"{emote_id}: format {im.format}, expected PNG")
            if im.size != (16, 16):
                errors.append(f"{emote_id}: size {im.size}, expected (16, 16)")
            if im.mode != "RGBA":
                errors.append(f"{emote_id}: mode {im.mode}, expected RGBA")
                continue
            alphas = list(im.getchannel("A").tobytes())
        partial = sum(1 for a in alphas if a not in (0, 255))
        opaque = sum(1 for a in alphas if a == 255)
        if partial:
            errors.append(f"{emote_id}: {partial} semi-transparent pixels")
        if opaque == 0:
            errors.append(f"{emote_id}: fully transparent")

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print(f"OK: {len(EMOTE_IDS)} emotes, all 16x16 RGBA, binary alpha")
    return 0


if __name__ == "__main__":
    sys.exit(main())
