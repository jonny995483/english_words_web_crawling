import requests
from bs4 import BeautifulSoup
import json


def scrape_daum_word(word_id):
    """
    다음 영어 사전에서 특정 word_id를 가진 단어의 정보를 스크래핑합니다. (수정된 버전)

    Args:
        word_id (str): 다음 사전의 단어 고유 ID (예: 'ekw000235125' for python)

    Returns:
        dict: 단어, 발음 기호, 발음 URL, 품사별 뜻과 예문이 담긴 딕셔너리
              오류 발생 시 None을 반환합니다.
    """

    # 목표 URL
    url = f"https://dic.daum.net/word/view.do?wordid={word_id}"

    # 웹사이트가 스크래핑을 막는 것을 피하기 위해 User-Agent 헤더 추가
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # 웹 페이지 요청
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # BeautifulSoup 객체 생성
        soup = BeautifulSoup(response.text, 'html.parser')

        # 최종 데이터를 저장할 딕셔너리
        word_data = {
            'word': None,
            'pronunciation_symbol': None,
            'pronunciation_audio': {},
            'meanings': []
        }

        # --- 코드 수정 부분 ---
        # 단어, 발음, 오디오 정보가 있는 상단 영역을 먼저 선택
        word_area = soup.select_one('.card_word .wrap_tit')

        if word_area:
            # 1. 단어 추출
            word_tag = word_area.select_one('.tit_cleansch .txt_clean')
            if word_tag:
                word_data['word'] = word_tag.text.strip()

            # 2. 발음 기호 추출
            pronunciation_tag = word_area.select_one('.txt_pronounce .txt_g')
            if pronunciation_tag:
                word_data['pronunciation_symbol'] = pronunciation_tag.text.strip()

            # 3. 발음 음성 파일 URL 추출
            # 미국식 발음
            us_audio_tag = word_area.select_one('.ico_sound_us a.link_mp3')
            if us_audio_tag and us_audio_tag.has_attr('href'):
                word_data['pronunciation_audio']['us'] = us_audio_tag['href']
            # 영국식 발음
            uk_audio_tag = word_area.select_one('.ico_sound_uk a.link_mp3')
            if uk_audio_tag and uk_audio_tag.has_attr('href'):
                word_data['pronunciation_audio']['uk'] = uk_audio_tag['href']

        # 뜻, 예문 정보가 있는 메인 영역을 선택
        meaning_area = soup.select_one('.card_word .cont_cleansch')

        if meaning_area:
            # 4. 품사, 뜻, 예문 추출
            meaning_blocks = meaning_area.select('.cleanword_type.kuek_type')

            for block in meaning_blocks:
                part_of_speech_tag = block.select_one('.wrap_sign .txt_pos')
                part_of_speech = part_of_speech_tag.text.strip() if part_of_speech_tag else "품사 정보 없음"

                definitions = []
                # 각 뜻(li)을 순회
                definition_items = block.select('ul.list_mean > li')
                for item in definition_items:
                    mean_tag = item.select_one('.txt_mean')
                    if not mean_tag:
                        continue

                    definition_text = mean_tag.text.strip()

                    # 해당 뜻에 속한 예문 추출
                    examples = []
                    example_list = item.select('.list_example > li')
                    for ex_item in example_list:
                        eng_tag = ex_item.select_one('.txt_ex')
                        kor_tag = ex_item.select_one('.txt_mean')
                        if eng_tag and kor_tag:
                            examples.append({
                                'eng': eng_tag.text.strip(),
                                'kor': kor_tag.text.strip()
                            })

                    definitions.append({
                        'definition': definition_text,
                        'examples': examples
                    })

                word_data['meanings'].append({
                    'part_of_speech': part_of_speech,
                    'definitions': definitions
                })

        return word_data

    except requests.exceptions.RequestException as e:
        print(f"오류가 발생했습니다: {e}")
        return None
    except Exception as e:
        print(f"데이터를 파싱하는 중 오류가 발생했습니다: {e}")
        return None


# --- 실행 부분 ---
if __name__ == "__main__":
    # 스크래핑할 단어 ID (URL에서 확인 가능)
    # 예시: python (id: ekw000235125)
    python_word_id = 'ekw000235125'

    # 다른 단어 예시: apple (id: ekw000010398)
    apple_word_id = 'ekw000010398'

    # 함수 호출하여 데이터 추출
    print(f"--- '{python_word_id}' (python) 단어 정보 추출 중 ---")
    scraped_data_python = scrape_daum_word(python_word_id)

    if scraped_data_python:
        print(json.dumps(scraped_data_python, ensure_ascii=False, indent=2))

    print("\n" + "=" * 50 + "\n")

    print(f"--- '{apple_word_id}' (apple) 단어 정보 추출 중 ---")
    scraped_data_apple = scrape_daum_word(apple_word_id)

    if scraped_data_apple:
        print(json.dumps(scraped_data_apple, ensure_ascii=False, indent=2))