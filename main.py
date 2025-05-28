from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone
from typing import Optional

from models import Task, get_session, init_db, select

app = FastAPI()
init_db()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def quick_sort(tasks: list[Task], ascending: bool = True) -> list[Task]:
    """Quick Sort для задач по дате создания"""
    if len(tasks) <= 1:
        return tasks
    
    pivot = tasks[0]
    less, equal, greater = [], [], []
    
    for task in tasks:
        if task.created_at < pivot.created_at:
            less.append(task)
        elif task.created_at == pivot.created_at:
            equal.append(task)
        else:
            greater.append(task)
    
    sorted_less = quick_sort(less, ascending)
    sorted_greater = quick_sort(greater, ascending)
    
    if ascending:
        return sorted_less + equal + sorted_greater
    return sorted_greater + equal + sorted_less

@app.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    sort_by_date: Optional[str] = None,  # Параметр для сортировки
    sort_by_importance: Optional[str] = None
):
    with get_session() as session:
        tasks = session.exec(select(Task)).all()
        
        # Применяем сортировку
        if sort_by_date == "asc":
            tasks = quick_sort(tasks, ascending=True)
        elif sort_by_date == "desc":
            tasks = quick_sort(tasks, ascending=False)
        elif sort_by_importance == "asc":
            tasks = sorted(tasks, key=lambda x: x.important)
        elif sort_by_importance == "desc":
            tasks = sorted(tasks, key=lambda x: x.important, reverse=True)
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "tasks": tasks,
                "timezone": timezone,
                "current_sort_date": sort_by_date,
                "current_sort_importance": sort_by_importance
            }
        )


@app.post("/add")
def add_task(name: str = Form(...), important: bool = Form(False)): 
	if not (1 <= len(name) <= 255):
		return HTMLResponse("Ошибка: имя задачи должно содержать от 1 до 255 символов", status_code=400)
	
	with get_session() as session: 
		task = Task(name=name, important=important)
		session.add(task)
		session.commit()
	return RedirectResponse("/", status_code=303)

@app.post("/toggle-important/{task_id}")
def toggle_important(task_id: int):
    with get_session() as session:
        task = session.get(Task, task_id)
        if task:
            task.important = not task.important
            session.commit()
    return RedirectResponse("/", status_code=303)


@app.post("/toggle/{task_id}")
def toggle_task(task_id: int): 
	with get_session() as session:
		task = session.get(Task, task_id)
		if task: 
			task.done = not task.done
			session.commit()
	return RedirectResponse("/", status_code=303)

@app.post("/delete/{task_id}")
def delete_task(task_id: int): 
	with get_session() as session: 
		task = session.get(Task, task_id)
		if task: 
			session.delete(task)
			session.commit()
	return RedirectResponse("/", status_code=303)