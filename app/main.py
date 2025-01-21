from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Form
from app.routers import tasks, auth

app = FastAPI()


app.include_router(tasks.router)
app.include_router(auth.router)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


tasks = [
    {"id": 1, "title": "Купить молоко", "description": "Купить молоко в магазине"},
    {"id": 2, "title": "Сделать домашку", "description": "Выполнить задание по FastAPI"},
]




@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})



@app.get("/about")
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.post("/tasks/")
def create_task(title: str = Form(...), description: str = Form(...)):
    new_task = {"id": len(tasks) + 1, "title": title, "description": description}
    tasks.append(new_task)
    return {"message": "Task created", "task": new_task}