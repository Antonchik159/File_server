from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os
import shutil
from typing import List

app = FastAPI()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload/")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    file_paths = []

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_paths.append(file_path)

    return RedirectResponse(url="/files/", status_code=303)


@app.get("/files/{filename}")
async def get_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}


@app.get("/files/")
async def list_files(request: Request):
    files = os.listdir(UPLOAD_DIR)
    if not files:
        return HTMLResponse("""
                            <title>Завантажені файли</title>
                            <style>
                                a {
                                    display: inline-block;
                                    margin-top: 20px;
                                    padding: 10px 20px;
                                    background-color: #333;
                                    color: white;
                                    text-decoration: none;
                                    border-radius: 5px;
                                }

                                a:hover {
                                    background-color: #555;
                                }
                            </style>
                            <center>
                                <h1>Файлів нема</h1>
                                <a href="/">Назад</a>
                            </center>
                            """)
    
    file_links = [f"/files/{file}" for file in files]
    
    return templates.TemplateResponse("file_list.html", {"request": request, "files": file_links})

@app.post("/files/delete/")
async def delete_file(filename: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return RedirectResponse(url='/files/', status_code=303)
    return {"error": "Файл не найден."}
