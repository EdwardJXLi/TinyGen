# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
from pathlib import Path
import uuid


def list_all_files(root_path: str | Path, uuid: uuid.UUID) -> list[str]:
    """
    Lists all files in the specified directory and its subdirectories.

    Parameters:
        root_path (str | Path): The root directory to start listing files from.
        uuid (uuid.UUID): The UUID that was used to name the subdirectory for the clone.

    Returns:
        list: A list of all files in the specified directory and its subdirectories.
    """
    # Construct the full path of the repository to delete
    full_path = Path(root_path, str(uuid))

    # Recursively search down and list all files
    all_files = []
    for path in full_path.rglob("*"):
        if path.is_file():
            file_path = path.relative_to(full_path)

            # Ignore if the file is in the .git directory
            if ".git" in file_path.parts:
                continue

            all_files.append(file_path.as_posix())
    return all_files


def is_safe_path(base_path: str | Path, target_path: str | Path) -> bool:
    """
    Determine if the target_path is a safe subpath of base_path using pathlib.

    Parameters:
        base_path (str | Path): The base path to check against.
        target_path (str | Path): The target path to check.

    Returns:
        bool: True if the target_path is a safe subpath of base_path, False otherwise.
    """
    base_path = Path(base_path).resolve()
    target_path = Path(target_path).resolve()

    return base_path in target_path.parents or base_path == target_path


def safe_read_file(root_path: str | Path, uuid: uuid.UUID, filename: str) -> str:
    """
    Safely read a file within a specified subfolder of the root folder using pathlib.

    Parameters:
        root_path (str | Path): The root directory where the repository is located.
        uuid (uuid.UUID): The UUID that was used to name the subdirectory for the clone.
        filename (str): The name of the file to read.

    Returns:
        str: The content of the file as a string.
    """
    full_path = Path(root_path, str(uuid), filename)
    if not is_safe_path(root_path, full_path):
        raise ValueError("Unsafe File Operation! This should not happen!")

    return full_path.read_text()


def safe_modify_file(root_path: str | Path, uuid: uuid.UUID, filename: str, content: str):
    """
    Safely modify a file within a specified subfolder of the root folder using pathlib.

    Parameters:
        root_path (str | Path): The root directory where the repository is located.
        uuid (uuid.UUID): The UUID that was used to name the subdirectory for the clone.
        filename (str): The name of the file to modify.
        content (str): The new content to write to the file.
    """
    full_path = Path(root_path, str(uuid), filename)
    if not is_safe_path(root_path, full_path):
        raise ValueError("Unsafe File Operation! This should not happen!")

    full_path.write_text(content)


def safe_delete_file(root_path: str | Path, uuid: uuid.UUID, filename: str):
    """
    Safely delete a file within a specified subfolder of the root folder using pathlib.

    Parameters:
        root_path (str | Path): The root directory where the repository is located.
        uuid (uuid.UUID): The UUID that was used to name the subdirectory for the clone.
        filename (str): The name of the file to delete.
    """
    full_path = Path(root_path, str(uuid), filename)
    if not is_safe_path(root_path, full_path):
        raise ValueError("Unsafe File Operation! This should not happen!")

    try:
        full_path.unlink()
    except FileNotFoundError:
        pass


def safe_create_file(root_path: str | Path, uuid: uuid.UUID, filename: str, content: str):
    """
    Safely create a new file within a specified subfolder of the root folder using pathlib.

    Parameters:
        root_path (str | Path): The root directory where the repository is located.
        uuid (uuid.UUID): The UUID that was used to name the subdirectory for the clone.
        filename (str): The name of the file to create.
        content (str): The content to write to the new file.
    """
    full_path = Path(root_path, str(uuid), filename)
    if not is_safe_path(root_path, full_path):
        raise ValueError("Unsafe File Operation! This should not happen!")

    full_path.write_text(content)
