Kanban Board Project Management Tool
------------------------------------

This is a project management tool designed to facilitate project organization and task management using the Kanban methodology. It allows users to create projects, form groups of collaborators, and create multiple boards with customizable numbers of tasks. Each task can have documents attached, assignees designated, priorities specified, and tags assigned.

### Features

*   **Project Creation:** Easily create new projects to organize your tasks and collaborators.
    
*   **Collaborator Management:** Form groups of collaborators to work on projects together.
    
*   **Customizable Kanban Boards:** Create as many Kanban boards as needed for each project, with the ability to define custom columns and tasks.
    
*   **Task Management:** Add tasks to boards, assign them to collaborators, set priorities, and assign tags for easy organization.
    
*   **Document Attachment:** Attach relevant documents to tasks for reference or additional information.
    

### Installation

```python

#Clone the repository to your local machine
git clone https://github.com/voidmain69/kanban-board.git
  
#Navigate to the project directory:
cd project-directory

#Set up and activate a virtual environment (optional but recommended):
python3 -m venv venvsource venv/bin/activate

#Install Django and other dependencies:
pip install -r requirements.txt

#Set up the database:
python manage.py migrate
    
#Optionally, you can load demo data for testing purposes:
python manage.py loaddata initial\_data.json

#Create a .env file in the project directory and add your environment variables:
SECRET_KEY=your_secret_key
DEBUG=True
    
#Start the Django server:
python manage.py runserver
```

### Usage

1.  **Create a Project:**
    
    *   Use the interface to create a new project.
        
    *   Specify project details such as name, description, and collaborators.
        
2.  **Create Kanban Boards:**
    
    *   Within each project, create custom Kanban boards to organize tasks.
        
    *   Define columns based on your workflow (e.g., To Do, In Progress, Done).
        
3.  **Add Tasks:**
    
    *   Within each board, add tasks by specifying title, description, assignees, priority, and tags.
        
    *   Optionally attach relevant documents to tasks.
        
4.  **Manage Tasks:**
    
    *   Update task status.
        
    *   Edit task details, assignees, priorities, and tags as needed.
        
5.  **Collaborate:**
    
    *   Collaborators can view and interact with boards, tasks, and documents based on their permissions.
        

### Contributing

Contributions are welcome! If you have any suggestions, feature requests, or bug reports, please open an issue or submit a pull request.

### License

This project is licensed under the MIT License.

### Acknowledgements

This project was inspired by the Kanban methodology and aims to provide a user-friendly tool for project management and collaboration.