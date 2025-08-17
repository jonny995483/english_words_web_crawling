import csv
import json

FILENAME = '교육부_3천단어_수정분.csv'

# cp949 인코딩으로 읽되, 오류가 발생하면 무시
with open(FILENAME, 'r', newline='', encoding='utf-8', errors='ignore') as f:
    lines = csv.reader(f)
    header = next(lines)
    print(header)

    high = []
    middle = []
    low = []
    total = []

    for line in lines:
        dict1 = {'id': line[0], header[1]: line[1], header[2]: line[2], header[3]: line[3]}
        # 변형1 있는 경우에만 추가
        if line[4]:
            dict1[header[4]] = line[4]
        # 변형2 있는 경우에만 추가
        if line[5]:
            dict1[header[5]] = line[5]

        total.append(dict1)
        #난이도 별로 나누기
        if line[3] == '초등':
            low.append(dict1)
        elif line[3] == '중고':
            middle.append(dict1)
        else:
            high.append(dict1)


# json 파일 생성
with open('english_words_low.json', 'w', encoding='UTF-8') as f:
    json.dump(low, f, ensure_ascii=False, indent=4)

with open('english_words_middle.json', 'w', encoding='UTF-8') as f:
    json.dump(middle, f, ensure_ascii=False, indent=4)

with open('english_words_high.json', 'w', encoding='UTF-8') as f:
    json.dump(high, f, ensure_ascii=False, indent=4)

with open('english_words_total.json', 'w', encoding='UTF-8') as f:
    json.dump(total, f, ensure_ascii=False, indent=4)