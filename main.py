import json
import os
import subprocess
import threading
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from starlette.responses import FileResponse
import py7zr

from algorithm.run import get_args_from_list
from settings import (__DEV_ENV__, __USER_CONFIG_FILE_NAME__,
                      __USER_DATASET_DIR__, __DB_DIR__)

app = FastAPI()
USER_CONFIG_LOCK = threading.Lock()


class DataSetting(BaseModel):
    namespace: str
    train_seq_len: int = 96
    predict_len: int


@app.post("/verify-data-settings/")
async def verify_data_settings(data_settings: DataSetting):
    user_data_path = os.path.join(__USER_DATASET_DIR__, data_settings.namespace)
    # TODO: 暂时注释
    if os.path.exists(user_data_path) and data_settings.namespace not in __DEV_ENV__.namespace_ignored:
        return {"code": 403, "message": "命名空间存在，请重新命名"}

    try:
        os.makedirs(user_data_path)
    except OSError as e:
        ...

    USER_CONFIG_LOCK.acquire()
    with open(os.path.join(user_data_path, __USER_CONFIG_FILE_NAME__), "w", encoding="utf-8") as f:
        json.dump(data_settings.dict(), fp=f, indent=4)
    USER_CONFIG_LOCK.release()
    return {"code": 200, "message": "创建命名空间成功"}


# @app.get("/clean-namespace/{namespace}")
# def clean_namespace(namespace: str):
#     user_data_path = os.path.join(__USER_DATASET_DIR__, namespace)
#     if os.path.exists(user_data_path):
#         os.removedirs(user_data_path)
#         os.rmdir(user_data_path)
#     return {"message": "OK"}

@app.get("/start-train/{namespace}")
def start_train(namespace: str):
    user_data_path = os.path.join(__USER_DATASET_DIR__, namespace)
    if not os.path.exists(user_data_path):
        return {"code": 405, "message": "namespace doesn't exists"}
    with open(os.path.join(user_data_path, __USER_CONFIG_FILE_NAME__), "r") as f:
        config_json = json.load(f)
    get_args_from_list([
        "--root_path", user_data_path,
        "--data_path", config_json["target_file"],
        "--data", namespace,
        "--seq_len", config_json["train_seq_len"],
        "--pred_len", config_json["predict_len"]
    ])
    return {"message": "training end", "code": 200}


@app.get("/list-dir/{namespace}")
def list_dir(namespace: str):
    user_data_path = os.path.join(__USER_DATASET_DIR__, namespace)
    if not os.path.exists(user_data_path):
        return {"code": 405, "message": "namespace doesn't exists"}
    res = []
    for file_item in os.listdir(user_data_path):
        res.append([file_item, os.path.getsize(os.path.join(user_data_path, file_item))])
    dir_list = dict(train_result=res, test_empty=[])
    return {"code": 200, "data": dir_list}


class DownloadFilesInfo(BaseModel):
    namespace: str
    relative_paths: List[str]


@app.post("/download-files/")
def download_files(target_files_info: DownloadFilesInfo):
    with py7zr.SevenZipFile(f"{__DB_DIR__}/{target_files_info.namespace}.7z", "w") as archive:
        for file_name in target_files_info.relative_paths:
            archive.write(os.path.join(__USER_DATASET_DIR__, target_files_info.namespace, file_name))

    return FileResponse(path=f"{__DB_DIR__}/{target_files_info.namespace}.7z",
                        filename=f"{target_files_info.namespace}.7z")


@app.post("/upload-file/")
async def get_file(file: UploadFile = File(), size=Form(), namespace: str = Form()):
    file_bytes = await file.read()
    file_name = file.filename
    if os.path.splitext(file_name)[-1] not in [".csv"]:
        return {"code": 403, "message": "文件扩展名不正确"}
    user_data_path = os.path.join(__USER_DATASET_DIR__, namespace)
    if not os.path.exists(user_data_path):
        os.makedirs(user_data_path)

    with open(os.path.join(user_data_path, file_name), "wb") as f:
        f.write(file_bytes)

    user_config = None
    USER_CONFIG_LOCK.acquire()
    with open(os.path.join(user_data_path, __USER_CONFIG_FILE_NAME__), "r", encoding="utf-8") as f:
        user_config = json.load(f)

    user_config["target_file"] = os.path.join(user_data_path, file_name)
    with open(os.path.join(user_data_path, __USER_CONFIG_FILE_NAME__), "w", encoding="utf-8") as f:
        json.dump(user_config, f, indent=4)

    USER_CONFIG_LOCK.release()
    return {"message": "保存文件成功", "code": 200}
