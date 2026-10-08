from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

# Store tasks in memory
tasks = []
next_id = 1

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Cloud To-Do</title>

    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: Arial, sans-serif;
            background: #f4f7fb;
            color: #1f2937;
            min-height: 100vh;
            padding: 40px 20px;
        }

        .container {
            max-width: 650px;
            margin: auto;
        }

        .header {
            text-align: center;
            margin-bottom: 25px;
        }

        .header h1 {
            font-size: 32px;
            margin-bottom: 8px;
        }

        .header p {
            color: #6b7280;
        }

        .card {
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        }

        .add-form {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
        }

        .add-form input {
            flex: 1;
            padding: 13px;
            border: 1px solid #d1d5db;
            border-radius: 10px;
            font-size: 15px;
            outline: none;
        }

        .add-form input:focus {
            border-color: #6366f1;
        }

        button {
            border: none;
            cursor: pointer;
            border-radius: 9px;
            padding: 10px 15px;
            font-size: 14px;
        }

        .add-btn {
            background: #6366f1;
            color: white;
            font-weight: bold;
        }

        .add-btn:hover {
            background: #4f46e5;
        }

        .stats {
            display: flex;
            justify-content: space-between;
            background: #f9fafb;
            padding: 14px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }

        .stat strong {
            display: block;
            font-size: 20px;
        }

        .stat span {
            color: #6b7280;
            font-size: 12px;
        }

        .task {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 5px;
            border-bottom: 1px solid #e5e7eb;
        }

        .task:last-child {
            border-bottom: none;
        }

        .task-name {
            flex: 1;
            font-size: 15px;
        }

        .completed {
            text-decoration: line-through;
            color: #9ca3af;
        }

        .complete-btn {
            background: #dcfce7;
            color: #166534;
        }

        .undo-btn {
            background: #fef3c7;
            color: #92400e;
        }

        .delete-btn {
            background: #fee2e2;
            color: #991b1b;
        }

        .empty {
            text-align: center;
            padding: 30px 10px;
            color: #9ca3af;
        }

        .clear {
            text-align: right;
            margin-top: 20px;
        }

        .clear-btn {
            background: #111827;
            color: white;
        }

        .footer {
            text-align: center;
            margin-top: 20px;
            color: #9ca3af;
            font-size: 13px;
        }

        @media (max-width: 500px) {
            .add-form {
                flex-direction: column;
            }

            .task {
                flex-wrap: wrap;
            }
        }
    </style>
</head>

<body>

<div class="container">

    <div class="header">
        <h1>☁️ My Cloud To-Do</h1>
        <p>A simple task manager running on AWS EC2</p>
    </div>

    <div class="card">

        <form class="add-form" method="POST" action="/add">
            <input
                type="text"
                name="task"
                placeholder="Enter a new task..."
                required
                maxlength="100"
            >
            <button class="add-btn" type="submit">+ Add</button>
        </form>

        <div class="stats">
            <div class="stat">
                <strong>{{ total }}</strong>
                <span>Total</span>
            </div>

            <div class="stat">
                <strong>{{ completed }}</strong>
                <span>Completed</span>
            </div>

            <div class="stat">
                <strong>{{ pending }}</strong>
                <span>Pending</span>
            </div>
        </div>

        {% if tasks %}

            {% for task in tasks %}

            <div class="task">

                {% if task.completed %}
                    <span class="task-name completed">
                        {{ task.name }}
                    </span>

                    <form method="POST" action="/toggle/{{ task.id }}">
                        <button class="undo-btn" type="submit">
                            Undo
                        </button>
                    </form>

                {% else %}
                    <span class="task-name">
                        {{ task.name }}
                    </span>

                    <form method="POST" action="/toggle/{{ task.id }}">
                        <button class="complete-btn" type="submit">
                            Complete
                        </button>
                    </form>

                {% endif %}

                <form method="POST" action="/delete/{{ task.id }}">
                    <button class="delete-btn" type="submit">
                        Delete
                    </button>
                </form>

            </div>

            {% endfor %}

            <div class="clear">
                <form method="POST" action="/clear">
                    <button class="clear-btn" type="submit">
                        Clear Completed
                    </button>
                </form>
            </div>

        {% else %}

            <div class="empty">
                <p>No tasks yet.</p>
                <p>Add your first task above! ✨</p>
            </div>

        {% endif %}

    </div>

    <div class="footer">
        Running with Python + Flask on AWS EC2
    </div>

</div>

</body>
</html>
"""


@app.route("/")
def home():
    completed = sum(1 for task in tasks if task["completed"])
    total = len(tasks)
    pending = total - completed

    return render_template_string(
        HTML,
        tasks=tasks,
        total=total,
        completed=completed,
        pending=pending
    )


@app.route("/add", methods=["POST"])
def add_task():
    global next_id

    task_name = request.form.get("task", "").strip()

    if task_name:
        tasks.append({
            "id": next_id,
            "name": task_name,
            "completed": False
        })

        next_id += 1

    return redirect("/")


@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            break

    return redirect("/")


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    global tasks

    tasks = [
        task for task in tasks
        if task["id"] != task_id
    ]

    return redirect("/")


@app.route("/clear", methods=["POST"])
def clear_completed():
    global tasks

    tasks = [
        task for task in tasks
        if not task["completed"]
    ]

    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)