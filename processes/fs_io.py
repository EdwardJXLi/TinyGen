# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
from pathlib import Path
import shutil
import pygit2
import uuid


def git_clone_repo(root_path: str | Path, uuid: uuid.UUID, github_url: str):
    """
    Clones a GitHub repository into a specified directory based on the root path and a UUID using pygit2.

    Parameters:
        root_path (str | Path): The root directory where the repository will be cloned.
        uuid (uuid.UUID): The UUID that will be used to name the subdirectory for the clone.
        github_url (str): The URL of the GitHub repository to clone.
    """
    # Construct the full path where the repository will be cloned
    full_path = Path(root_path, str(uuid))

    # Create the directory if it doesn't exist
    full_path.mkdir(parents=True, exist_ok=True)

    # Clone the repository into the specified directory
    pygit2.clone_repository(github_url, full_path)


def git_delete_repo(root_path: str | Path, uuid: uuid.UUID):
    """
    Deletes a cloned repository from the specified directory based on the root path and a UUID.

    Parameters:
        root_path (str | Path): The root directory where the repository is located.
        uuid (uuid.UUID): The UUID that was used to name the subdirectory for the clone.
    """
    # Construct the full path of the repository to delete
    full_path = Path(root_path, str(uuid))

    # Delete the directory if it exists
    if full_path.exists():
        shutil.rmtree(full_path)


def git_reset_repo(root_path: str | Path, uuid: uuid.UUID):
    """
    Resets a cloned repository back to its original state using pygit2.

    Parameters:
        root_path (str | Path): The root directory where the repository is located.
        uuid (uuid.UUID): The UUID that was used to name the subdirectory for the clone.
    """
    # Construct the full path of the repository to reset
    full_path = Path(root_path, str(uuid))

    # Open the repository
    repo = pygit2.Repository(str(full_path))

    # Reset the repository
    git_reset_flag = pygit2.GIT_RESET_HARD  # type: ignore
    repo.reset(repo.head.target, git_reset_flag)


def git_generate_diff(root_path: str | Path, uuid: uuid.UUID) -> str:
    """
    Generates a diff of the changes in a cloned repository using pygit2.

    Parameters:
        root_path (str | Path): The root directory where the repository is located.
        uuid (uuid.UUID): The UUID that was used to name the subdirectory for the clone.

    Returns:
        str: The diff of the changes in the cloned repository.
    """
    # Construct the full path of the repository to generate the diff
    full_path = Path(root_path, str(uuid))

    # Open the repository
    repo = pygit2.Repository(str(full_path))

    # Create a diff of the changes
    diff = repo.diff()

    # Return the diff as a string
    return diff.patch if diff.patch else ""


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
