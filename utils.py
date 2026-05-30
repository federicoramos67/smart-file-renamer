from pathlib import Path


def list_files(folder: Path) -> list[Path]:
    return sorted(
        [path for path in folder.iterdir() if path.is_file()],
        key=lambda path: path.name.lower(),
    )


def format_file_size(size_in_bytes: int) -> str:
    units = ("B", "KB", "MB", "GB", "TB")
    size = float(size_in_bytes)

    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024

    return f"{size_in_bytes} B"
