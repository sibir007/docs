from pathlib import Path

SITES_DIR = "./sites"

def get_sites_names() -> list[str]:
    p = Path(SITES_DIR)
    return [d.stem for d in p.iterdir() if d.is_dir() and not d.stem.startswith("_")]
