from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

import requests
import json
import os
from random import randint
from django.utils.timezone import now
import math
from account.models import User
from haversine import haversine


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

def get_distance_v2(origin_address, destination_road_address):
    o_lat, o_long = origin_address["latitude"], origin_address["longitude"]
    _, d_lat, d_long = coordinate_send_request(destination_road_address)

    url = 'https://apis-navi.kakaomobility.com/v1/directions?origin={o_long},{o_lat}&destination={d_long},{d_lat}'.format(o_long=o_long, o_lat=o_lat, d_long=d_long, d_lat=d_lat)
    headers = {
        'Authorization': 'KakaoAK {}'.format(KAKAO_KEY),  # Authorization 헤더
        'Content-Type': 'application/json'  # 필요에 따라 Content-Type 헤더 추가
    }

    result = json.loads(str(requests.get(url, headers=headers).text))
    if result["routes"][0]["result_code"] != 0: # 경로를 찾을 수 없는 경우 -> 거리 대신 -1 반환
        print("경로 찾기 실패")
        return -1
    print("경로 찾기 성공")
    print("거리:", result["routes"][0]["summary"]["distance"])
    print("result:", result["routes"][0]["summary"])
    return result["routes"][0]["summary"]["distance"]


# 사용자와의 거리가 2km 이내인 강아지 필터링
def finding_dogs_around_you(lat1, lon1, dogs):
    return_data = {"dogs":[], "count":0}

    for dog in dogs:
        dog_user_id = dog.user_id.id
        dog_user =  User.objects.get(id=dog_user_id) # 견주
        dog_user_address = dog_user.road_address # 견주의 위치(도로명주소)

        total_count, lat2, lon2 = coordinate_send_request(dog_user_address)
        if total_count == 0:
            print("위,경도 탐색 실패")
            break
        point1 = (float(lat1), float(lon1))
        point2 = (float(lat2), float(lon2))
    

        distance = haversine(point1, point2)
        
        if distance <= 2: # 경로를 찾은 경우 and 경로가 2km 이내인 경우
            around_dog = {"id":dog.id, "name":dog.name, "road_address":dog_user.road_address, "distance":float(f"{distance:.{1}f}"), "image":dog.image.url, "status":dog.status}
            return_data["dogs"].append(around_dog)
            return_data["count"] += 1
 
    return return_data

