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

    # Add all files
    repo.index.add_all()
    repo.index.write()

    # Create a tree from the current index to represent the current state
    current_tree_id = repo.index.write_tree()
    current_tree = repo.get(current_tree_id)

    # Get the HEAD commit's tree to represent the last committed state
    head_commit = repo.head.peel(pygit2.Commit)
    head_tree = head_commit.tree

    # Create a diff between the HEAD commit's tree and the current state tree
    diff = repo.diff(head_tree, current_tree)

    # Convert the diff to a string
    diff_str = diff.patch if diff.patch else ""

    return diff_str
