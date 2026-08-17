from django.urls import path
from . import views


urlpatterns = [

    # Dashboard
    path(
        '',
        views.task_list,
        name='task_list'
    ),

    # Get all tasks
    path(
        'api/tasks/',
        views.task_api,
        name='task_api'
    ),

    # Create task
    path(
        'api/tasks/create/',
        views.create_task,
        name='create_task'
    ),

    # Update task
    path(
        'api/tasks/<int:task_id>/update/',
        views.task_update,
        name='update_task'
    ),

    # Delete task
    path(
        'api/tasks/<int:task_id>/delete/',
        views.task_delete,
        name='delete_task'
    ),

    # Single task
    path(
        'api/tasks/<int:task_id>/',
        views.task_detail,
        name='task_detail'
    ),

    # Search
    path(
        'api/search/',
        views.search_tasks,
        name='search_tasks'
    ),
]