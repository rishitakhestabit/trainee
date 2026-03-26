# Todo List API

This is a simple Todo List API built using FastAPI and AWS services.

## Requirements

* Python 3.11
* pip
* boto3
* pydantic
* uvicorn

## Installation

1. Clone the repository
2. Install the requirements using `pip install -r requirements.txt`
3. Build the Docker image using `docker build -t todo-list-api .`
4. Run the Docker container using `docker run -p 8000:8000 todo-list-api`

## API Endpoints

* `GET /tasks`: Get all tasks
* `POST /tasks`: Create a new task
* `GET /tasks/{task_id}`: Get a task by ID
* `PUT /tasks/{task_id}`: Update a task
* `DELETE /tasks/{task_id}`: Delete a task
* `GET /lists`: Get all lists
* `POST /lists`: Create a new list
* `GET /lists/{list_id}`: Get a list by ID
* `PUT /lists/{list_id}`: Update a list
* `DELETE /lists/{list_id}`: Delete a list