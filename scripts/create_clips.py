"""Create minimal placeholder MP4 clips for local development."""

from pathlib import Path

# Minimal valid MP4 (ftyp + mdat) — browsers may not play it, but clip IDs resolve.
MINIMAL_MP4 = (
    b"\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2mp41"
    b"\x00\x00\x00\x08mdat"
)

CLIPS_DIR = Path(__file__).resolve().parent.parent / "static" / "clips"


def main() -> None:
    CLIPS_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("wave.mp4", "smile.mp4", "nod.mp4"):
        path = CLIPS_DIR / name
        if not path.exists():
            path.write_bytes(MINIMAL_MP4)
            print(f"Created {path}")


if __name__ == "__main__":
    main()
