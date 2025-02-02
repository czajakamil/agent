import os
import time
from clasess.tools.ToDoist import ToDoist

def main():
    """
    Example usage of ToDoist class.
    Make sure to set TODOIST_API_TOKEN in your environment variables before running.
    """
    # Initialize ToDoist with API token from environment
    todoist = ToDoist()
    
    # 1. Create a new project
    print("\n1. Creating a new project...")
    project = todoist.create_project(name="Test Project")
    project_id = project["id"]
    print(f"Created project: {project['name']} (ID: {project_id})")
    
    # 2. Create tasks in the project
    print("\n2. Creating tasks...")
    
    # Task with due date and high priority
    task1 = todoist.create_task(
        content="High priority task",
        project_id=project_id,
        priority=4,
        due_string="today at 15:00"
    )
    print(f"Created task: {task1['content']} (ID: {task1['id']})")
    
    # Task with normal priority
    task2 = todoist.create_task(
        content="Normal priority task",
        project_id=project_id,
        priority=2,
        due_string="tomorrow"
    )
    print(f"Created task: {task2['content']} (ID: {task2['id']})")
    
    # 3. List all tasks in the project
    print("\n3. Listing all tasks in the project...")
    tasks = todoist.get_tasks(project_id=project_id)
    for task in tasks:
        print(f"- {task['content']} (Due: {task.get('due', {}).get('string', 'No due date')})")
    
    # 4. Update a task
    print("\n4. Updating task...")
    updated_task = todoist.update_task(
        task_id=task1["id"],
        content="Updated high priority task",
        due_string="today at 16:00"
    )
    print(f"Updated task: {updated_task['content']} (Due: {updated_task['due']['string']})")
    
    # 5. Complete a task
    print("\n5. Completing task...")
    todoist.complete_task(task_id=task2["id"])
    print(f"Completed task: {task2['content']}")
    
    # 6. List all projects
    print("\n6. Listing all projects...")
    projects = todoist.get_projects()
    for proj in projects:
        print(f"- {proj['name']} (ID: {proj['id']})")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError occurred: {str(e)}") 