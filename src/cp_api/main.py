from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import datetime
import os
import pandas as pd
import pymysql.cursors

app = FastAPI()

# CORS 설정
origins = [
    "http://localhost",
    "https://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"Hello": "n20"}

# 도커에서 VOLUME으로 마운트된 /data 디렉터리로 경로 설정
def get_path():
    return "~/data/n20"

# 음식 이름과 시간을 csv로 저장 -> /data/food.csv
@app.get("/food")
def food(name: str):
    # 현재 시간을 구하고 파싱
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    # CSV 파일 저장을 위한 경로 설정
    f_csv = os.path.join(get_path())
    if not os.path.exists(f_csv):
        os.makedirs(f_csv)

    # CSV 파일 경로 설정
    csv_file_path = os.path.join(f_csv, "food.csv")

    # food.csv 파일이 없으면 생성, 있으면 데이터 추가
    if not os.path.exists(csv_file_path):
        df = pd.DataFrame(columns=["food", "time"])
    else:
        df = pd.read_csv(csv_file_path)

    # 새 데이터 추가
    new_data = pd.DataFrame([[name, formatted_time]], columns=["food", "time"])
    df = pd.concat([df, new_data], ignore_index=True)

    # CSV 파일 저장
    df.to_csv(csv_file_path, index=False)

    # DB 연결 및 데이터 저장
    try:
        connection = pymysql.connect(
            host='localhost',
            port=33306,
            user='food',
            password='1234',
            database='fooddb'
        )
        with connection.cursor() as cursor:
            sql = "INSERT INTO foodhistory (username, foodname, dt) VALUES (%s, %s, %s)"
            cursor.execute(sql, ('n20', name, formatted_time))
            connection.commit()
    except Exception as e:
        return {"error": str(e)}
    finally:
        connection.close()

    return {"food": name, "time": formatted_time}
