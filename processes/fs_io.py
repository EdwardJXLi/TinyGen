# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
from pathlib import Path
import shutil
import pygit2
import uuid


def clone_repo(root_path: str | Path, uuid: uuid.UUID, github_url: str):
    """
    Clones a GitHub repository into a specified directory based on the root path and a UUID using pygit2.

    Parameters:
        root_path (str): The root directory where the repository will be cloned.
        uuid (str): The UUID that will be used to name the subdirectory for the clone.
        github_url (str): The URL of the GitHub repository to clone.
    """
    # Construct the full path where the repository will be cloned
    full_path = Path(root_path, str(uuid))

    # Create the directory if it doesn't exist
    full_path.mkdir(parents=True, exist_ok=True)

    # Clone the repository into the specified directory
    pygit2.clone_repository(github_url, full_path)


def delete_repo(root_path: str | Path, uuid: uuid.UUID):
    """
    Deletes a cloned repository from the specified directory based on the root path and a UUID.

    Parameters:
        root_path (str): The root directory where the repository is located.
        uuid (str): The UUID that was used to name the subdirectory for the clone.
    """
    # Construct the full path of the repository to delete
    full_path = Path(root_path, str(uuid))

    # Delete the directory if it exists
    if full_path.exists():
        shutil.rmtree(full_path)


def list_all_files(root_path: str | Path, uuid: uuid.UUID):
    """
    Lists all files in the specified directory and its subdirectories.

    Parameters:
        root_path (str): The root directory to start listing files from.

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
