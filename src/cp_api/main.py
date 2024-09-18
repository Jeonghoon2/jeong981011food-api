from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pickle
import datetime
import os
import pandas as pd

app = FastAPI()

origins = [
    "http://localhost",
    # "https://"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allowcredentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"Hello":"n00"}

def get_path():
    file_dir = __file__
    dir = os.path.dirname(file_dir)
    return dir

# 음식 이름과 시간을 csv로 저장 -> /code/data/food.csv
@app.get("/food")
def food(name: str):
    
    # 현재 시간을 구하고 파싱
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    # 현재 시간과 입력된 음식을 저장
    f_csv = os.path.join(get_path(), "code","data")

    # f_csv 폴더가 없다면 생성 있다면 pass
    if not os.path.exists(f_csv):
        os.makedirs(f_csv)

    # csv 파일 경로 설정
    csv_file_path = os.path.join(f_csv, "food.csv")

    # f_csv 폴더에 food.csv 파일이 없다면 생성 있다면 데이터를 추가
    if not os.path.exists(csv_file_path):
        df = pd.DataFrame(columns=["food", "time"])
    else:
        df = pd.read_csv(csv_file_path)

    # 새 데이터 추가
    new_data = pd.DataFrame([[name, formatted_time]], columns=["food", "time"])
    df = pd.concat([df, new_data], ignore_index=True)

    # CSV 파일 저장
    df.to_csv(csv_file_path, index=False)


    return {"food":name, "time":formatted_time}