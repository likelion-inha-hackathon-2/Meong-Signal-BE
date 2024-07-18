from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

import requests
import json


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
    return result['meta']['total_count'], result['documents'][0]['y'], result['documents'][0]['x'] # total_count, latitude, longitude 순서. total_count가 0이면 찾지 못한 것

def get_distance(origin_road_address, destination_road_address):
    _, o_lat, o_long = coordinate_send_request(origin_road_address)
    _, d_lat, d_long = coordinate_send_request(destination_road_address)

    url = 'https://apis-navi.kakaomobility.com/v1/directions?origin={o_long},{o_lat}&destination={d_long},{d_lat}'.format(o_long=o_long, o_lat=o_lat, d_long=d_long, d_lat=d_lat)
    headers = {
        'Authorization': 'KakaoAK {}'.format(KAKAO_KEY),  # Authorization 헤더
        'Content-Type': 'application/json'  # 필요에 따라 Content-Type 헤더 추가
    }

    result = json.loads(str(requests.get(url, headers=headers).text))
    if result["routes"][0]["result_code"] != 0: # 경로를 찾을 수 없는 경우 -> 거리 대신 -1 반환
        return -1
    return result["routes"][0]["summary"]["distance"]