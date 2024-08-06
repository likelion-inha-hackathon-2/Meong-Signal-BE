from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

import requests
import json
import datetime


BASE_DIR = Path(__file__).resolve().parent.parent

secret_file = BASE_DIR / 'secrets.json'

with open(secret_file) as file:
    secrets = json.loads(file.read())

def get_secret(setting,secrets_dict = secrets):
    try:
        return secrets_dict[setting]
    except KeyError:
        error_msg = f'Set the {setting} environment variable'
        raise ImproperlyConfigured(error_msg)

KAKAO_KEY = get_secret('KAKAO_KEY') 

def coordinate_send_request(road_address): # 도로명 주소 기반 위, 경도 찾기
    url = 'https://dapi.kakao.com/v2/local/search/address?query={address}'.format(address=road_address)  # 요청을 보낼 API의 URL
    headers = {
        'Authorization': 'KakaoAK {}'.format(KAKAO_KEY),  # Authorization 헤더
        'Content-Type': 'application/json'  # 필요에 따라 Content-Type 헤더 추가
    }

    result = json.loads(str(requests.get(url, headers=headers).text))
    return result

def get_calories(distance_km, weight_kg=60, speed_kmh=4): # 사용자 60kg 가정, speed는 km/h단위, distance는 km단위
    # 걷기(시속 4km) 기준 MET 값
    MET_walking = 3.5
    # 속도에 따라 MET 값 조정 (단순 예시, 실제 값은 활동 강도에 따라 다를 수 있음)
    METs = MET_walking * (speed_kmh / 4)
    # 시간 계산 (시간 = 거리 / 속도)
    time_hours = distance_km / speed_kmh
    # 칼로리 소모 계산
    calories_burned = METs * weight_kg * time_hours
    return calories_burned

def get_start_of_week(): # 이번 주 월요일 계산
    # 현재 날짜
    now = datetime.date.today()
    # 현재 날짜에서 요일을 뺀다 (월요일이 0, 일요일이 6)
    start_of_week = now - datetime.timedelta(days=now.weekday())
    return start_of_week