let tasks = [];


document.addEventListener(
    'DOMContentLoaded',
    loadTasks
);


async function loadTasks() {

    try {

        const response = await fetch(
            '/tasks/api/tasks/'
        );

        if (!response.ok) {
            throw new Error(
                'Failed to load tasks'
            );
        }

        tasks = await response.json();

        updateStatistics();

        renderTasks();

    } catch (error) {

        console.error(error);

        alert(
            'Unable to load tasks.'
        );
    }
}


function getCookie(name) {

    let cookieValue = null;

    if (document.cookie) {

        const cookies =
            document.cookie.split(';');

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (
                cookie.startsWith(
                    name + '='
                )
            ) {

                cookieValue =
                    decodeURIComponent(
                        cookie.substring(
                            name.length + 1
                        )
                    );

                break;
            }
        }
    }

    return cookieValue;
}


function updateStatistics() {

    const total =
        tasks.length;

    const pending =
        tasks.filter(
            task => task.status === 'pending'
        ).length;

    const progress =
        tasks.filter(
            task =>
                task.status === 'in_progress'
        ).length;

    const completed =
        tasks.filter(
            task =>
                task.status === 'completed'
        ).length;


    document.getElementById(
        'totalTasks'
    ).textContent = total;


    document.getElementById(
        'pendingTasks'
    ).textContent = pending;


    document.getElementById(
        'progressTasks'
    ).textContent = progress;


    document.getElementById(
        'completedTasks'
    ).textContent = completed;
}


function renderTasks() {

    const container =
        document.getElementById(
            'taskContainer'
        );


    const filter =
        document.getElementById(
            'filterStatus'
        ).value;


    let filteredTasks = tasks;


    if (filter !== 'all') {

        filteredTasks =
            tasks.filter(
                task =>
                    task.status === filter
            );
    }


    if (filteredTasks.length === 0) {

        container.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    📝
                </div>

                <h3>
                    No tasks found
                </h3>

                <p>
                    Create a task to get started.
                </p>

                <button
                    onclick="openAddModal()"
                >
                    + Add Task
                </button>

            </div>

        `;

        return;
    }


    container.innerHTML =
        filteredTasks.map(
            task => createTaskHTML(task)
        ).join('');
}


function createTaskHTML(task) {

    const statusText =
        task.status === 'in_progress'
            ? 'In Progress'
            : capitalize(task.status);


    const priorityText =
        capitalize(task.priority);


    return `

        <div class="task-card">

            <div class="task-top">

                <div>

                    <h3 class="task-title">
                        ${escapeHTML(task.title)}
                    </h3>

                    <p class="task-description">
                        ${
                            escapeHTML(
                                task.description ||
                                'No description'
                            )
                        }
                    </p>

                    <div class="task-meta">

                        <span
                            class="badge status-${task.status}"
                        >
                            ${statusText}
                        </span>

                        <span
                            class="badge priority-${task.priority}"
                        >
                            ${priorityText} Priority
                        </span>

                        ${
                            task.due_date
                            ? `
                                <span class="badge">
                                    📅 ${task.due_date}
                                </span>
                              `
                            : ''
                        }

                    </div>

                </div>


                <div class="task-actions">

                    <button
                        class="edit-btn"
                        onclick="editTask(${task.id})"
                    >
                        ✏️ Edit
                    </button>

                    <button
                        class="delete-btn"
                        onclick="deleteTask(${task.id})"
                    >
                        🗑 Delete
                    </button>

                </div>

            </div>

        </div>

    `;
}


function escapeHTML(value) {

    const div =
        document.createElement('div');

    div.textContent =
        value;

    return div.innerHTML;
}


function capitalize(value) {

    return value.charAt(0).toUpperCase()
        + value.slice(1);
}


function openAddModal() {

    document.getElementById(
        'modalTitle'
    ).textContent = 'Add New Task';


    document.getElementById(
        'taskId'
    ).value = '';


    document.getElementById(
        'taskForm'
    ).reset();


    document.getElementById(
        'taskStatus'
    ).value = 'pending';


    document.getElementById(
        'taskPriority'
    ).value = 'medium';


    document.getElementById(
        'taskModal'
    ).classList.add('show');
}


function closeModal() {

    document.getElementById(
        'taskModal'
    ).classList.remove('show');
}


async function saveTask(event) {

    event.preventDefault();


    const taskId =
        document.getElementById(
            'taskId'
        ).value;


    const taskData = {

        title:
            document.getElementById(
                'taskTitle'
            ).value,

        description:
            document.getElementById(
                'taskDescription'
            ).value,

        status:
            document.getElementById(
                'taskStatus'
            ).value,

        priority:
            document.getElementById(
                'taskPriority'
            ).value,

        due_date:
            document.getElementById(
                'taskDueDate'
            ).value

    };


    const isEditing =
        taskId !== '';


    const url = isEditing
        ? `/tasks/api/tasks/${taskId}/update/`
        : '/tasks/api/tasks/create/';


    const method =
        isEditing
            ? 'PUT'
            : 'POST';


    try {

        const response =
            await fetch(
                url,
                {
                    method: method,

                    headers: {
                        'Content-Type':
                            'application/json',

                        'X-CSRFToken':
                            getCookie('csrftoken')
                    },

                    body:
                        JSON.stringify(taskData)
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.message ||
                'Something went wrong'
            );
        }


        closeModal();

        await loadTasks();

        alert(
            isEditing
                ? 'Task updated successfully!'
                : 'Task added successfully!'
        );


    } catch (error) {

        console.error(error);

        alert(
            error.message
        );
    }
}


function editTask(id) {

    const task =
        tasks.find(
            task => task.id === id
        );


    if (!task) {
        return;
    }


    document.getElementById(
        'modalTitle'
    ).textContent =
        'Edit Task';


    document.getElementById(
        'taskId'
    ).value =
        task.id;


    document.getElementById(
        'taskTitle'
    ).value =
        task.title;


    document.getElementById(
        'taskDescription'
    ).value =
        task.description;


    document.getElementById(
        'taskStatus'
    ).value =
        task.status;


    document.getElementById(
        'taskPriority'
    ).value =
        task.priority;


    document.getElementById(
        'taskDueDate'
    ).value =
        task.due_date;


    document.getElementById(
        'taskModal'
    ).classList.add('show');
}


async function deleteTask(id) {

    const confirmed =
        confirm(
            'Are you sure you want to delete this task?'
        );


    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(
                `/tasks/api/tasks/${id}/delete/`,
                {
                    method: 'DELETE',

                    headers: {
                        'X-CSRFToken':
                            getCookie('csrftoken')
                    }
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.message ||
                'Unable to delete task'
            );
        }


        await loadTasks();


        alert(
            'Task deleted successfully!'
        );


    } catch (error) {

        console.error(error);

        alert(
            error.message
        );
    }
}


window.onclick = function(event) {

    const modal =
        document.getElementById(
            'taskModal'
        );


    if (event.target === modal) {

        closeModal();
    }
};
