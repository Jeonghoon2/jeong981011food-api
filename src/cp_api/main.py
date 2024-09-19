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
    "https://localhost:8080",
    "https://food-jh-98.web.app",
    "https://food-jh-98.web.app/*",
    "https://food-jh-98.web.app/n20/",
    "https://api.samdulshop.shop/n20/",
    "https://api.samdulshop.shop/n20/*"
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

# 리팩토링 -> CSV 파일을 저장
def save_to_csv(food, time):

    # CSV Path 설정
    f_csv = os.path.join("data/n20")  # 절대 경로로 변경

    # 폴더 여부에 따라 생성
    if not os.path.exists(f_csv):
        os.makedirs(f_csv)

    # CSV FULL Path 설정
    csv_file_path = os.path.join(f_csv, "food.csv")

    # CSV 파일이 존재하지 않으면 새로 생성, 있으면 읽기
    if not os.path.exists(csv_file_path):
        df = pd.DataFrame(columns=["food", "time"])
    else:
        df = pd.read_csv(csv_file_path)

    # 새 데이터 추가 (열 이름 지정)
    new_data = pd.DataFrame([[food, time]], columns=["food", "time"])
    df = pd.concat([df, new_data], ignore_index=True)

    # CSV 파일로 저장
    df.to_csv(csv_file_path, index=False)



# 음식 이름과 시간을 csv로 저장 -> /data/food.csv
@app.get("/food")
def food(name: str):
    # 현재 시간을 구하고 파싱
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    # CSV 파일로 저장
    save_to_csv(name, formatted_time)

    try:
        connection = pymysql.connect(
            host=os.getenv("DB_IP", "localhost"),
            port=int(os.getenv("DB_PORT", "33306")),
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
