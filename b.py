import spacy
import re
import hashlib

nlp = spacy.load("ja_core_news_trf") #ja_core_news_mdもいいらしい

def generate_hash(text, length=4):
    return hashlib.md5(text.encode()).hexdigest()[:length]

def anonymize_name(name, name_hash):
    return f"{name[0]}**{name_hash}"

def anonymize_email(email):
    username, domain = email.split('@')
    return f"{username[0]}{'*' * (len(username) - 1)}@{domain}"

def anonymize_phone(phone):
    digits = re.sub(r'\D', '', phone)
    return f"{'*' * (len(digits) - 4)}{digits[-4:]}"

def anonymize_text(text):
    name_dict = {}

    lines = text.split('\n')
    anonymized_lines = []
    
    for line in lines:
        doc = nlp(line)
        anonymized_line = line

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                if ent.text not in name_dict:
                    name_hash = generate_hash(ent.text)
                    name_dict[ent.text] = name_hash
                else:
                    name_hash = name_dict[ent.text]
                
                anonymized_name = anonymize_name(ent.text, name_hash)
                anonymized_line = anonymized_line.replace(ent.text, anonymized_name)

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        anonymized_line = re.sub(email_pattern, lambda m: anonymize_email(m.group()), anonymized_line)

        phone_pattern = r'(\+81|0)\d{1,4}[-\s]?\d{1,4}[-\s]?\d{4}'
        anonymized_line = re.sub(phone_pattern, lambda m: anonymize_phone(m.group()), anonymized_line)

        anonymized_lines.append(anonymized_line)

    return '\n'.join(anonymized_lines)

sample_text = """
山田太郎さんの連絡先は、メールアドレスがtaro.yamada@example.com、
株式会社テクノロジーの田中社長も、この会議に参加する予定です。
山田太郎さんと田中社長は旧知の仲です。田中二郎さんも参加予定です。
山田二郎は某大手会社の社長だと聞きました。
"""

anonymized_text = anonymize_text(sample_text)
print("匿名化されたテキスト:")
print(anonymized_text)