import json
import time
import random
import requests
from bs4 import BeautifulSoup

base_url = 'https://dic.daum.net/word/view.do?wordid=ekw'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

session = requests.Session()
session.headers.update(headers)

def getWordData(word_id):
    try:
        response = session.get(f'{base_url}{word_id:09d}')
        if response.status_code == 200:
            word_data = {}
            soup = BeautifulSoup(response.text, 'html.parser')
            word_data['id'] = word_id
            level_element = soup.select_one('.tit_cleanword .txt_cleanset')
            if level_element:
                word_data['난이도'] = level_element.text.strip()
            word_data['영단어'] = soup.select_one('.txt_cleanword').text.strip()
            mean_elements = soup.select('ul.list_mean .txt_mean')
            word_data['뜻'] = [mean.text.strip() for mean in mean_elements]
            type_element = soup.select_one('.tit_sort')
            if type_element:
                word_data['품사'] = type_element.text.strip()
            changes_dict = {}
            change_items = soup.select('.list_sort li')
            for item in change_items:
                key = item.select_one('.txt_sort').text.strip()
                value_element = item.select_one('.link_word')
                if value_element:
                    value = value_element.text.strip()
                else:
                    value = item.text.replace(key, '').strip()
                changes_dict[key] = value
            if changes_dict:
                word_data['형태'] = changes_dict
            return word_data
        else:
            print(f"ID {word_id}: 오류 발생 (Status Code: {response.status_code})")
            return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"ID {word_id}: 네트워크 오류 발생 ({e})")
        return 999

# --- 메인 로직 (핵심 변경 부분) ---

# 1. 기존 데이터 로드
FILENAME = 'english_words.json'
try:
    with open(FILENAME, 'r', encoding='UTF-8') as f:
        words_data = json.load(f)
    print(f"기존 데이터 {len(words_data)}개를 불러왔습니다.")
except (FileNotFoundError, json.JSONDecodeError):
    # 파일이 없거나, 내용이 비어있거나, 깨져있으면 새로 시작
    words_data = []
    print("새로운 데이터 수집을 시작합니다.")

# 2. 시작 word_id 설정
if words_data:
    # 데이터가 있으면 마지막 id 다음부터 시작
    word_id = words_data[-1]['id']
else:
    # 데이터가 없으면 0부터 시작
    word_id = 0

print(f"ID {word_id + 1}부터 수집을 시작합니다.")

# 수집할 단어 개수 설정
WORDS_TO_CRAWL = 1000
start_word_id = word_id + 1
end_word_id = start_word_id + WORDS_TO_CRAWL -1


# --- 메인 루프 ---
while True:
    word_id += 1

    result = getWordData(word_id)

    if isinstance(result, dict):
        # 3. 파일에 바로 쓰지 않고, 리스트에 추가
        words_data.append(result)
        print(f"ID {word_id}: '{result['영단어']}' 수집 성공 ({len(words_data)}개)")
        sleep_time = random.uniform(0.3, 0.5)
    else:
        if result == 404:
            print(f"ID {word_id}: 페이지 없음 (404 Not Found). 건너뜁니다.")
            sleep_time = 0.1
        else:
            print(f"ID {word_id}: 재시도합니다.")
            sleep_time = random.uniform(1, 1.5)
            word_id -= 1

    # 4. 루프 종료 조건 변경 (예: 200개 추가 수집)
    if word_id >= end_word_id:
        print(f"{WORDS_TO_CRAWL}개 단어 수집을 시도했습니다. 프로그램을 종료합니다.")
        break

    print(f"  ... {sleep_time:.2f}초 대기 ...")
    time.sleep(sleep_time)


# 5. 모든 작업이 끝난 후, 최종 데이터를 파일에 저장
with open(FILENAME, 'w', encoding='UTF-8') as f:
    json.dump(words_data, f, ensure_ascii=False, indent=4)

print(f"\n--- 총 {len(words_data)}개의 단어 데이터를 '{FILENAME}' 파일에 저장했습니다. ---")