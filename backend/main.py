# 进入venv虚拟环境
# terminial-> venv/Scripts/activate.bat
import uvicorn
import time
from fastapi import FastAPI, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from zipfile import ZipFile
from utils import tools
from models import model
from pathlib import Path
from io import BytesIO
from task import task_oi
import pandas as pd

app = FastAPI()

origins = [
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def root():
    # df = pd.read_csv('~/desktop/metadata_prone_to_supine_t1_2017_04_18.csv')
    # column = df['participant_id']
    # print(type(column))
    # print(column[0])
    return "Welcome to segmentation backend"


@app.get('/api/cases')
async def get_cases_name(background_tasks: BackgroundTasks):
    # tools.save()
    background_tasks.add_task(tools.save)
    folder_path = tools.IMPORT_FOLDER_PATH
    CASE_NAMES = tools.get_all_folder_names(folder_path)
    print(CASE_NAMES)
    filename = "mask.json"
    res = {}
    res["names"] = CASE_NAMES
    res["details"] = []
    for subdirectory in CASE_NAMES:
        # is_exist = check_file_exist(directory, filename)
        is_exist = tools.check_mask_json_file(tools.EXPORT_FOLDER_PATH, subdirectory, filename)
        res["details"].append({"name": subdirectory, "masked": is_exist})
    return res


@app.get('/api/case/')
async def send_nrrd_case(name: str = Query(None)):
    start_time = time.time()
    if name is not None:
        cwd = Path.cwd()
        tools.FOLDER_PATH = cwd / tools.EXPORT_FOLDER_PATH / name
        file_names = tools.get_all_file_names(tools.IMPORT_FOLDER_PATH, name)
        file_paths = []
        for file in file_names:
            file_paths.append(cwd / tools.IMPORT_FOLDER_PATH / name / file)

        is_exist = tools.check_mask_json_file(tools.EXPORT_FOLDER_PATH, name, "mask.json")
        if is_exist:
            file_paths.append( cwd / tools.EXPORT_FOLDER_PATH / name / "mask.json")
        with ZipFile('nrrd_files.zip', 'w') as zip_file:
            for file_path in file_paths:
                zip_file.write(file_path)
    end_time = time.time()
    run_time = end_time - start_time
    print("get files cost:{:.2f}s".format(run_time))
    return FileResponse('nrrd_files.zip', media_type='application/zip')


@app.post("/api/mask/init")
async def init_mask(mask: model.Masks):
    tools.write_data_to_json(tools.EXPORT_FOLDER_PATH, mask.caseId, mask.masks)
    return True


@app.post("/api/mask/replace")
async def replace_mask(replace_slice: model.Mask):
    tools.replace_data_to_json(tools.EXPORT_FOLDER_PATH, replace_slice.caseId, replace_slice)
    return True


@app.get("/api/mask/save")
async def save_mask(name: str, background_tasks: BackgroundTasks):
    # tools.save()
    background_tasks.add_task(task_oi.json_to_nii,name)
    return True

@app.get("/api/mask")
async def get_mask(name: str = Query(None)):
    if name is not None:
        cwd = Path.cwd()
        file_path = cwd / tools.EXPORT_FOLDER_PATH / name / "mask.json"
        cheked = tools.check_mask_json_file(tools.EXPORT_FOLDER_PATH, name, "mask.json")
        if (cheked):
            with open(file_path, mode="rb") as file:
                file_contents = file.read()
            file_object = BytesIO(file_contents)
            return StreamingResponse(file_object, media_type="application/json")
        else:
            return False


if __name__ == '__main__':
    uvicorn.run(app)
