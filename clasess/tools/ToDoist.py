import os
import requests
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

class ToDoist:
    """
    A class to interact with Todoist API v2 for task management.
    Documentation: https://developer.todoist.com/rest/v2/
    """
    
    BASE_URL = "https://api.todoist.com/rest/v2"
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize ToDoist with API token.
        
        Args:
            api_token (str, optional): Todoist API token. If not provided, will try to get from environment variable.
        """
        self.api_token = api_token or os.getenv("TODOIST_API_TOKEN") or os.getenv("TODOIST_API_KEY")
        if not self.api_token:
            raise ValueError("Todoist API token is required. Please provide it or set TODOIST_API_TOKEN or TODOIST_API_KEY environment variable.")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def create_task(self, content: str, due_string: Optional[str] = None, 
                    priority: Optional[int] = None, project_id: Optional[str] = None,
                    label_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a new task in Todoist.
        
        Args:
            content (str): The task content/description
            due_string (str, optional): Human readable date string (e.g., "tomorrow at 12:00")
            priority (int, optional): Task priority (1-4, where 4 is highest)
            project_id (str, optional): The project ID to add the task to
            label_ids (List[str], optional): List of label IDs to add to the task
            
        Returns:
            Dict[str, Any]: Created task data
        """
        endpoint = f"{self.BASE_URL}/tasks"
        payload: Dict[str, Any] = {"content": content}
        
        if due_string:
            payload["due_string"] = due_string
        if priority:
            payload["priority"] = priority
        if project_id:
            payload["project_id"] = project_id
        if label_ids:
            payload["label_ids"] = label_ids
            
        response = requests.post(endpoint, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_tasks(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all active tasks, optionally filtered by project.
        
        Args:
            project_id (str, optional): Project ID to filter tasks
            
        Returns:
            List[Dict[str, Any]]: List of tasks
        """
        endpoint = f"{self.BASE_URL}/tasks"
        params: Dict[str, str] = {}
        if project_id:
            params["project_id"] = project_id
            
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def update_task(self, task_id: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Update an existing task.
        
        Args:
            task_id (str): The ID of the task to update
            **kwargs: Any task properties to update (content, due_string, priority, etc.)
            
        Returns:
            Dict[str, Any]: Updated task data
        """
        endpoint = f"{self.BASE_URL}/tasks/{task_id}"
        response = requests.post(endpoint, headers=self.headers, json=kwargs)
        response.raise_for_status()
        return response.json()
    
    def complete_task(self, task_id: str) -> None:
        """
        Complete a task.
        
        Args:
            task_id (str): The ID of the task to complete
        """
        endpoint = f"{self.BASE_URL}/tasks/{task_id}/close"
        response = requests.post(endpoint, headers=self.headers)
        response.raise_for_status()
    
    def reopen_task(self, task_id: str) -> None:
        """
        Reopen a completed task.
        
        Args:
            task_id (str): The ID of the task to reopen
        """
        endpoint = f"{self.BASE_URL}/tasks/{task_id}/reopen"
        response = requests.post(endpoint, headers=self.headers)
        response.raise_for_status()
    
    def delete_task(self, task_id: str) -> None:
        """
        Delete a task.
        
        Args:
            task_id (str): The ID of the task to delete
        """
        endpoint = f"{self.BASE_URL}/tasks/{task_id}"
        response = requests.delete(endpoint, headers=self.headers)
        response.raise_for_status()
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get all projects.
        
        Returns:
            List[Dict[str, Any]]: List of projects
        """
        endpoint = f"{self.BASE_URL}/projects"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_project(self, name: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            name (str): The name of the project
            parent_id (str, optional): The ID of the parent project
            
        Returns:
            Dict[str, Any]: Created project data
        """
        endpoint = f"{self.BASE_URL}/projects"
        payload: Dict[str, Any] = {"name": name}
        if parent_id:
            payload["parent_id"] = parent_id
            
        response = requests.post(endpoint, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
