# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
from supabase import create_client, Client


class Supabase:
    def __init__(self, project_url: str, api_key: str):
        """
        Creates a Supabase class, which handles all the communication and interaction with the Supabase API.
        For TinyGen, there exists a query table that contains the following schema:

        {
            "task_id": uuid [PRIMARY KEY],
            "created_at": timestamp,
            "prompt": text,
            "repo_url": text,
            "status": text,
            "result": text
        }

        Parameters:
            project_url (str): The project URL to use for the Supabase API.
            api_key (str): The API key to use for the Supabase API.
        """
        # Initialize the Supabase API
        self.project_url: str = project_url
        self.api_key: str = api_key

        # Initialize the Supabase client
        self.client: Client = create_client(project_url, api_key)
        self.queries_table = self.client.table("queries")

    def add_query(self, task):
        """
        Adds a query to the Supabase API.

        Parameters:
            task (Task): The task object to add to the Supabase API.
        """
        # Add the query to the Supabase API
        self.queries_table.insert(
            {
                "task_id": str(task.task_id),
                "created_at": str(task.start_time),
                "prompt": task.prompt,
                "repo_url": task.repo_url,
                "status": task.status.value,
                "result": task.result
            }
        ).execute()

    def update_query(self, task):
        """
        Updates a query in the Supabase API.

        Parameters:
            task (Task): The task object to update in the Supabase API.
        """
        # Update the query in the Supabase API
        self.queries_table.update(
            {
                "status": task.status.value,
                "result": task.result
            }
        ).eq("task_id", str(task.task_id)).execute()
