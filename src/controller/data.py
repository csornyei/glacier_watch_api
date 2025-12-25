from pathlib import Path


def get_folder_contents(folder_path: Path):
    if not folder_path.exists() or not folder_path.is_dir():
        return None, 0

    contents = [item.name for item in folder_path.iterdir()]
    size = sum(f.stat().st_size for f in folder_path.glob("**/*") if f.is_file())
    return contents, size


def bytes_to_readable(size_in_bytes: int) -> str:
    """Convert bytes to a human-readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} PB"
