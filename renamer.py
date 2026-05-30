import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class RenameOptions:
    remove_special: bool = True
    spaces_to_underscores: bool = True
    add_numbering: bool = False
    add_date_prefix: bool = False
    start_number: int = 1
    padding: int = 3
    date_prefix: str | None = None


@dataclass(frozen=True)
class RenamePlanItem:
    path: Path
    old_name: str
    new_name: str
    has_duplicate: bool
    conflicts_with_existing: bool

    @property
    def is_blocked(self) -> bool:
        return self.has_duplicate or self.conflicts_with_existing

    @property
    def status(self) -> str:
        if self.has_duplicate:
            return "Duplicate target"
        if self.conflicts_with_existing:
            return "Already exists"
        if self.old_name == self.new_name:
            return "No change"
        return "Ready"


def build_rename_plan(files: list[Path], options: RenameOptions) -> list[RenamePlanItem]:
    target_names = [
        build_new_filename(file_path, options, index)
        for index, file_path in enumerate(files, start=options.start_number)
    ]
    duplicate_names = _find_duplicates(target_names)
    source_names = {file_path.name for file_path in files}

    plan = []
    for file_path, target_name in zip(files, target_names):
        has_duplicate = target_name in duplicate_names
        target_path = file_path.with_name(target_name)
        conflicts_with_existing = (
            target_name != file_path.name
            and target_path.exists()
            and target_name not in source_names
        )

        plan.append(
            RenamePlanItem(
                path=file_path,
                old_name=file_path.name,
                new_name=target_name,
                has_duplicate=has_duplicate,
                conflicts_with_existing=conflicts_with_existing,
            )
        )

    return plan


def build_new_filename(file_path: Path, options: RenameOptions, number: int) -> str:
    stem = file_path.stem.strip()
    suffix = file_path.suffix

    if options.remove_special:
        stem = remove_special_characters(stem)

    if options.spaces_to_underscores:
        stem = replace_spaces_with_underscores(stem)

    stem = normalize_separators(stem) or "file"

    parts = []
    if options.add_date_prefix:
        parts.append(options.date_prefix or date.today().isoformat())
    if options.add_numbering:
        parts.append(str(number).zfill(options.padding))
    parts.append(stem)

    return "_".join(parts) + suffix.lower()


def execute_rename_plan(plan: list[RenamePlanItem]) -> int:
    if any(item.is_blocked for item in plan):
        raise ValueError("Cannot rename while the plan contains duplicates or conflicts.")

    changed_items = [item for item in plan if item.old_name != item.new_name]
    temporary_paths = []

    for index, item in enumerate(changed_items):
        temporary_path = item.path.with_name(f".smart_renamer_tmp_{index}{item.path.suffix}")
        item.path.rename(temporary_path)
        temporary_paths.append((temporary_path, item.path.with_name(item.new_name)))

    for temporary_path, final_path in temporary_paths:
        temporary_path.rename(final_path)

    return len(changed_items)


def remove_special_characters(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9\s._-]+", "", value)
    return cleaned.strip()


def replace_spaces_with_underscores(value: str) -> str:
    return re.sub(r"\s+", "_", value.strip())


def normalize_separators(value: str) -> str:
    value = re.sub(r"[_-]{2,}", "_", value)
    value = re.sub(r"\.{2,}", ".", value)
    return value.strip(" ._-")


def _find_duplicates(names: list[str]) -> set[str]:
    seen = set()
    duplicates = set()
    for name in names:
        key = name.lower()
        if key in seen:
            duplicates.add(name)
        seen.add(key)
    return {name for name in names if name.lower() in {item.lower() for item in duplicates}}
