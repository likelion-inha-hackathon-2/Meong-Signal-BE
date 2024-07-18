from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

import requests
import json

from account.models import User


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

# 사용자와의 거리가 2km 이내인 강아지 필터링
def finding_dogs_around_you(user_address, dogs):
    return_data = {"dogs":[]}
    for dog in dogs:
        dog_user_id = dog.user_id.id
        dog_user =  User.objects.get(id=dog_user_id) # 견주
        dog_user_address = dog_user.road_address # 견주의 위치(도로명주소)

        distance = get_distance(user_address, dog_user_address)
        if distance != -1 and distance < 2000: # 경로를 찾은 경우 and 경로가 2km 이내인 경우
            around_dog = {"id":dog.id, "name":dog.name, "road_address":dog_user.road_address, "distance":round(distance / 1000, 1), "image":dog.image.url}
            return_data["dogs"].append(around_dog)
    return return_data