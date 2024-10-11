import spacy
import re
import hashlib

nlp = spacy.load("ja_core_news_sm")

# 日本語の文字かどうかを判定する関数を定義
def is_japanese(text):
    return any(re.match(r'[\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', char) for char in text)

def generate_hash(text, length=4):
    return hashlib.md5(text.encode()).hexdigest()[:length]

def anonymize_name(name, name_hash):
    # 名前の最初の1文字を残して、残りを匿名化する
    if len(name) > 1:
        return f"{name[0]}{'*' * (len(name) - 1)}{name_hash}"
    else:
        return f"{name}{name_hash}"

def anonymize_email(email):
    username, domain = email.split('@')
    return f"{username[0]}{'*' * (len(username) - 1)}@{domain}"

def anonymize_phone(phone):
    digits = re.sub(r'\D', '', phone)
    return f"{'*' * (len(digits) - 4)}{digits[-4:]}"

def is_name_candidate(token):
    return token.pos_ in ["PROPN"] and is_japanese(token.text)

def find_names(doc):
    names = []
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            names.append(ent.text)
    
    for token in doc:
        if is_name_candidate(token) and token.text not in names:
            names.append(token.text)
    
    print("検出された名前:", names)  # デバッグ用に検出された名前を表示
    
    return names

def anonymize_text(text):
    doc = nlp(text)
    name_dict = {}
    anonymized_text = text

    names = find_names(doc)
    for name in names:
        if name not in name_dict:
            name_hash = generate_hash(name)
            name_dict[name] = name_hash
        else:
            name_hash = name_dict[name]

        anonymized_name = anonymize_name(name, name_hash)
        anonymized_text = re.sub(rf'\b{re.escape(name)}\b', anonymized_name, anonymized_text)

    # メールアドレスの匿名化
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    anonymized_text = re.sub(email_pattern, lambda m: anonymize_email(m.group()), anonymized_text)

    # 電話番号の匿名化（日本の形式）
    phone_pattern = r'(\+81|0)\d{1,4}[-\s]?\d{1,4}[-\s]?\d{4}'
    anonymized_text = re.sub(phone_pattern, lambda m: anonymize_phone(m.group()), anonymized_text)

    return anonymized_text

# テスト用のサンプルテキスト
sample_text = """
山田太郎さんの連絡先は、メールアドレスがtaro.yamada@example.com、
電話番号が090-1234-5678です。また、佐藤花子さんの電話番号は03-9876-5432です。
株式会社テクノロジーの田中社長も、この会議に参加する予定です。
山田太郎さんと田中社長は旧知の仲です。田中二郎さんも参加予定です。
山田二郎さんもまた、田中社長の友で、旧友らしい。
"""

anonymized_text = anonymize_text(sample_text)
print("匿名化されたテキスト:")
print(anonymized_text)
