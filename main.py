from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from models import Task, get_session, init_db, select

app = FastAPI()

init_db()

templates = Jinja2Templates(directory="templates")

app.mount("/static",StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def index(request: Request): 
	with get_session() as session: 
		tasks = session.exec(select(Task)).all()
	return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})


@app.post("/add")
def add_task(name: str = Form(...), important: bool = Form(False)): 
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