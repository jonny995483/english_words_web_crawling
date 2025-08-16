import time
import random
import requests
from bs4 import BeautifulSoup

base_url = 'https://dic.daum.net/word/view.do?wordid=ekw'
word_id = 0
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
words_data = []

file_path = "C:\Users\jonny995483\Desktop"

session = requests.Session()
session.headers.update(headers)


def getWordData(word_id):
    try:
        response = session.get(f'{base_url}{word_id:09d}')

        if response.status_code == 200:
            # --- 성공 시 파싱 로직 (기존과 동일) ---
            word_data = {}
            soup = BeautifulSoup(response.text, 'html.parser')

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
            # --- 실패 시 True 대신 상태 코드를 반환하도록 수정 ---
            print(f"ID {word_id}: 오류 발생 (Status Code: {response.status_code})")
            return response.status_code  # 예: 404, 403

    except requests.exceptions.RequestException as e:
        print(f"ID {word_id}: 네트워크 오류 발생 ({e})")
        return 999  # 네트워크 오류를 위한 임의의 코드


# --- 메인 루프 ---
while True:
    word_id += 1

    result = getWordData(word_id)

    # --- 반환값의 타입을 확인하여 성공/실패를 구분 ---
    if isinstance(result, dict):  # 성공: 결과가 딕셔너리 타입일 때
        words_data.append(result)
        print(f"ID {word_id}: '{result['영단어']}' 수집 성공")
        sleep_time = random.uniform(0.3, 0.5)

    else:  # 실패: 결과가 숫자(상태 코드)일 때
        # 404 오류는 재시도하지 않고 그냥 건너뜀
        if result == 404:
            print(f"ID {word_id}: 페이지 없음 (404 Not Found). 건너뜁니다.")
            sleep_time = 0.1  # 없는 페이지는 빠르게 건너뛰기
        # 403 같은 다른 오류는 재시도
        else:
            print(f"ID {word_id}: 재시도합니다.")
            sleep_time = random.uniform(1, 1.5)
            word_id -= 1

    if word_id >= 500:
        break

    print(f"  ... {sleep_time:.2f}초 대기 ...")
    time.sleep(sleep_time)

print("\n--- 최종 수집 결과 ---")
print(words_data)