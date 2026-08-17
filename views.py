from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils.dateparse import parse_date

from .models import Task


# ============================================================
# DASHBOARD / TASK LIST
# ============================================================

@login_required
def task_list(request):
    """
    Main TaskFlow dashboard.
    Shows only tasks belonging to the logged-in user.
    """

    tasks = Task.objects.filter(
        user=request.user
    ).order_by('-created_at')

    # -------------------------
    # Statistics
    # -------------------------

    total_tasks = tasks.count()

    pending_tasks = tasks.filter(
        status='pending'
    ).count()

    in_progress_tasks = tasks.filter(
        status='in_progress'
    ).count()

    completed_tasks = tasks.filter(
        status='completed'
    ).count()

    # -------------------------
    # Overall progress
    # -------------------------

    if total_tasks > 0:
        progress = round(
            (completed_tasks / total_tasks) * 100
        )
    else:
        progress = 0

    context = {
        'tasks': tasks,

        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,

        'progress': progress,

        'user': request.user,
    }

    return render(
        request,
        'tasks/tasks.html',
        context
    )


# ============================================================
# GET TASKS API
# ============================================================

@login_required
@require_http_methods(["GET"])
def task_api(request):
    """
    Returns all tasks of the logged-in user as JSON.
    """

    tasks = Task.objects.filter(
        user=request.user
    ).order_by('-created_at')

    data = []

    for task in tasks:

        data.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,

            'due_date': (
                task.due_date.strftime('%Y-%m-%d')
                if task.due_date
                else ''
            ),

            'created_at': (
                task.created_at.strftime('%Y-%m-%d %H:%M:%S')
                if task.created_at
                else ''
            ),

            'updated_at': (
                task.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                if task.updated_at
                else ''
            ),
        })

    return JsonResponse({
        'success': True,
        'tasks': data
    })


# ============================================================
# CREATE TASK
# ============================================================

@login_required
@require_http_methods(["POST"])
def create_task(request):
    """
    Creates a new task for the logged-in user.

    Accepts JSON data:
    {
        "title": "...",
        "description": "...",
        "status": "pending",
        "priority": "medium",
        "due_date": "2026-08-20"
    }
    """

    try:

        # --------------------------------
        # Read JSON
        # --------------------------------

        import json

        data = json.loads(
            request.body.decode('utf-8')
        )

        title = data.get('title', '').strip()
        description = data.get(
            'description',
            ''
        ).strip()

        status = data.get(
            'status',
            'pending'
        )

        priority = data.get(
            'priority',
            'medium'
        )

        due_date = data.get(
            'due_date',
            ''
        )

        # --------------------------------
        # Validate title
        # --------------------------------

        if not title:

            return JsonResponse({
                'success': False,
                'message': 'Task title is required.'
            }, status=400)

        # --------------------------------
        # Validate status
        # --------------------------------

        allowed_statuses = [
            'pending',
            'in_progress',
            'completed'
        ]

        if status not in allowed_statuses:

            status = 'pending'

        # --------------------------------
        # Validate priority
        # --------------------------------

        allowed_priorities = [
            'low',
            'medium',
            'high'
        ]

        if priority not in allowed_priorities:

            priority = 'medium'

        # --------------------------------
        # Convert date
        # --------------------------------

        parsed_due_date = None

        if due_date:

            parsed_due_date = parse_date(
                due_date
            )

        # --------------------------------
        # Create task
        # --------------------------------

        task = Task.objects.create(

            user=request.user,

            title=title,

            description=description,

            status=status,

            priority=priority,

            due_date=parsed_due_date
        )

        # --------------------------------
        # Return response
        # --------------------------------

        return JsonResponse({
            'success': True,

            'message': 'Task created successfully.',

            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,

                'due_date': (
                    task.due_date.strftime('%Y-%m-%d')
                    if task.due_date
                    else ''
                ),
            }
        })

    except Exception as e:

        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


# ============================================================
# UPDATE TASK
# ============================================================

@login_required
@require_http_methods(["POST", "PUT"])
def task_update(request, task_id):
    """
    Updates an existing task.

    The task must belong to the logged-in user.
    """

    task = get_object_or_404(
        Task,
        id=task_id,
        user=request.user
    )

    try:

        import json

        data = json.loads(
            request.body.decode('utf-8')
        )

        # --------------------------------
        # Title
        # --------------------------------

        if 'title' in data:

            title = data.get(
                'title',
                ''
            ).strip()

            if not title:

                return JsonResponse({
                    'success': False,
                    'message': 'Task title is required.'
                }, status=400)

            task.title = title

        # --------------------------------
        # Description
        # --------------------------------

        if 'description' in data:

            task.description = data.get(
                'description',
                ''
            ).strip()

        # --------------------------------
        # Status
        # --------------------------------

        if 'status' in data:

            allowed_statuses = [
                'pending',
                'in_progress',
                'completed'
            ]

            if data['status'] in allowed_statuses:

                task.status = data['status']

        # --------------------------------
        # Priority
        # --------------------------------

        if 'priority' in data:

            allowed_priorities = [
                'low',
                'medium',
                'high'
            ]

            if data['priority'] in allowed_priorities:

                task.priority = data['priority']

        # --------------------------------
        # Due date
        # --------------------------------

        if 'due_date' in data:

            due_date = data.get(
                'due_date'
            )

            if due_date:

                task.due_date = parse_date(
                    due_date
                )

            else:

                task.due_date = None

        # --------------------------------
        # Save
        # --------------------------------

        task.save()

        return JsonResponse({

            'success': True,

            'message': 'Task updated successfully.',

            'task': {

                'id': task.id,

                'title': task.title,

                'description': task.description,

                'status': task.status,

                'priority': task.priority,

                'due_date': (
                    task.due_date.strftime('%Y-%m-%d')
                    if task.due_date
                    else ''
                )
            }
        })

    except Exception as e:

        return JsonResponse({

            'success': False,

            'message': str(e)

        }, status=400)


# ============================================================
# DELETE TASK
# ============================================================

@login_required
@require_http_methods(["DELETE"])
def task_delete(request, task_id):
    """
    Deletes a task belonging to the logged-in user.
    """

    task = get_object_or_404(
        Task,
        id=task_id,
        user=request.user
    )

    task.delete()

    return JsonResponse({

        'success': True,

        'message': 'Task deleted successfully.'
    })


# ============================================================
# OPTIONAL: SINGLE TASK API
# ============================================================

@login_required
@require_http_methods(["GET"])
def task_detail(request, task_id):
    """
    Returns one task as JSON.
    """

    task = get_object_or_404(
        Task,
        id=task_id,
        user=request.user
    )

    return JsonResponse({

        'success': True,

        'task': {

            'id': task.id,

            'title': task.title,

            'description': task.description,

            'status': task.status,

            'priority': task.priority,

            'due_date': (
                task.due_date.strftime('%Y-%m-%d')
                if task.due_date
                else ''
            ),

            'created_at': (
                task.created_at.strftime(
                    '%Y-%m-%d %H:%M:%S'
                )
                if task.created_at
                else ''
            ),

            'updated_at': (
                task.updated_at.strftime(
                    '%Y-%m-%d %H:%M:%S'
                )
                if task.updated_at
                else ''
            )
        }
    })


# ============================================================
# SEARCH TASKS
# ============================================================

@login_required
@require_http_methods(["GET"])
def search_tasks(request):
    """
    Search tasks by title or description.

    Example:
    /tasks/api/search/?q=django
    """

    query = request.GET.get(
        'q',
        ''
    ).strip()

    tasks = Task.objects.filter(
        user=request.user
    )

    if query:

        tasks = tasks.filter(

            Q(title__icontains=query) |

            Q(description__icontains=query)
        )

    data = []

    for task in tasks.order_by('-created_at'):

        data.append({

            'id': task.id,

            'title': task.title,

            'description': task.description,

            'status': task.status,

            'priority': task.priority,

            'due_date': (
                task.due_date.strftime('%Y-%m-%d')
                if task.due_date
                else ''
            )
        })

    return JsonResponse({

        'success': True,

        'tasks': data
    })