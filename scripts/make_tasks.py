"""python scripts/make_tasks.py -> data/tasks.jsonl (deterministic; fixed seeds).

Eval: Egyptian local knowledge asked in English AND Arabic (idea of the language gap borrowed from MultiLoKo,
Meta, MIT; none of its data is used). Each task is one fact, written once per language; rows of a pair share
`metadata.pair`. The finance version of this generator is in git history (tag v0.1.0).

Fact tables below are the answer key. Sources (see data/README.md):
  CODES  - provincial codes of the 14-digit Egyptian national ID, English Wikipedia "Egyptian National Identity
           Card" (secondary source; matches the django-localflavor list); names in Arabic are the standard ones.
  AREA   - landline area codes, Wikipedia "Telephone numbers in Egypt" mirror / dubai-online (secondary).
Every ID number in a prompt is invented.
"""
import datetime as dt
import json
import pathlib
import random

OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "tasks.jsonl"

# code -> (English names accepted, Arabic names accepted); first English name is the display name
CODES = {
    "01": (["Cairo"], ["القاهرة"]), "02": (["Alexandria"], ["الإسكندرية", "اسكندرية"]),
    "03": (["Port Said"], ["بورسعيد"]), "04": (["Suez"], ["السويس"]),
    "11": (["Damietta"], ["دمياط"]), "12": (["Dakahlia", "Dakahliya"], ["الدقهلية"]),
    "13": (["Sharqia", "Sharkia", "Sharqiyah", "Al Sharqia", "El Sharqia"], ["الشرقية"]),
    "14": (["Qalyubia", "Qalyubiyya", "Qalubia", "Kalyoubia"], ["القليوبية"]),
    "15": (["Kafr El Sheikh", "Kafr El-Sheikh", "Kafr al-Sheikh", "Kafr Elsheikh"], ["كفر الشيخ"]),
    "16": (["Gharbia", "Gharbiyya", "Al Gharbia", "El Gharbia"], ["الغربية"]),
    "17": (["Monufia", "Menoufia", "Minufiyya", "Menofia"], ["المنوفية"]),
    "18": (["Beheira", "Buhayra", "El Beheira", "Al Beheira"], ["البحيرة"]),
    "19": (["Ismailia", "Ismailiyya"], ["الإسماعيلية"]),
    "21": (["Giza", "Gizeh"], ["الجيزة"]),
    "22": (["Beni Suef", "Bani Suwayf", "Beni Sweif"], ["بني سويف"]),
    "23": (["Fayoum", "Faiyum", "Fayyum", "El Fayoum"], ["الفيوم"]),
    "24": (["Minya", "Menia", "El Minya", "Al Minya"], ["المنيا"]),
    "25": (["Asyut", "Assiut", "Asyout", "Assyut"], ["أسيوط"]),
    "26": (["Sohag", "Suhag"], ["سوهاج"]),
    "27": (["Qena", "Qina"], ["قنا"]),
    "28": (["Aswan"], ["أسوان"]),
    "29": (["Luxor"], ["الأقصر"]),
    "31": (["Red Sea"], ["البحر الأحمر"]),
    "32": (["New Valley", "Al Wadi Al Gedid", "El Wadi El Gedid"], ["الوادي الجديد"]),
    "33": (["Matruh", "Matrouh", "Marsa Matruh"], ["مطروح"]),
    "34": (["North Sinai"], ["شمال سيناء"]),
    "35": (["South Sinai"], ["جنوب سيناء"]),
}
ABROAD_EN = ["outside Egypt", "abroad", "born abroad", "outside the republic", "outside the country", "outside of Egypt"]
ABROAD_AR = ["خارج مصر", "خارج الجمهورية", "بالخارج", "في الخارج", "خارج البلاد"]
# city -> (area code without leading 0, English accepted, Arabic city name)
AREA = {"Tanta": ("40", "طنطا"), "Damanhur": ("45", "دمنهور"), "Sohag": ("93", "سوهاج"), "Beni Suef": ("82", "بني سويف")}

RULE_EN = "\n\nThink it through, then end your reply with one final line in exactly this form:\nANSWER: <answer>\n"
RULE_AR = "\n\nفكّر خطوة بخطوة، ثم اختم ردك بسطر أخير بهذا الشكل بالضبط:\nANSWER: <الإجابة>\n"
SRC_ID = "English Wikipedia 'Egyptian National Identity Card', provincial codes table (secondary source)"
SRC_AREA = "Wikipedia 'Telephone numbers in Egypt' mirror and dubai-online country-code page (secondary sources)"


def names(code, lang):
    en, ar = CODES[code]
    base = en if lang == "en" else ar
    return base + ([f"{n} Governorate" for n in base] if lang == "en" else [f"محافظة {n}" for n in base])


def make_id(rng, code, born=None):
    d = born or dt.date(1960, 1, 1) + dt.timedelta(days=rng.randint(0, 365 * 50))
    century = "2" if d.year < 2000 else "3"
    return f"{century}{d:%y%m%d}{code}{rng.randint(0, 9999):04d}{rng.randint(0, 9)}", d


def pair(pid, trap, ref, src, slip, rows):
    """rows = {lang: (question, answer, grader)}; returns two task dicts."""
    out = []
    for lang in ("en", "ar"):
        q, ans, grader = rows[lang]
        out.append({"id": f"{pid}-{lang}", "prompt": q + (RULE_EN if lang == "en" else RULE_AR), "answer": ans,
                    "grader": grader, "metadata": {"domain": "Egyptian local knowledge", "trap": trap, "lang": lang,
                                                   "pair": pid, "difficulty": "hard", "source": src,
                                                   "reference": ref, "slip": slip,
                                                   "why_hard": WHY[trap]}})
    return out


WHY = {
    "id-code": "The 2-digit province code in the national ID is an arbitrary table; models know the layout and the "
               "birth date but guess a plausible governorate instead of recalling the code.",
    "area-code": "Landline area codes are arbitrary two-digit labels with no rule to derive them.",
}


def gov_from_id(pid, seed, code, slip_code):
    rng = random.Random(seed)
    nid, _ = make_id(rng, code)
    rows = {
        "en": (f"This is a fictional Egyptian national ID number: {nid}. In which governorate was the holder born? "
               f"Give the governorate name in English.", "|".join(names(code, "en")), "answer_set"),
        "ar": (f"هذا رقم قومي مصري وهمي: {nid}. في أي محافظة وُلد صاحبه؟ اكتب اسم المحافظة بالعربية.",
               "|".join(names(code, "ar")), "answer_set"),
    }
    return pair(pid, "id-code", f"digits 8-9 of {nid} = {code} -> {CODES[code][0][0]}", SRC_ID, CODES[slip_code][0][0], rows)


def code_from_gov(pid, code, slip_code):
    en, ar = CODES[code][0][0], CODES[code][1][0]
    rows = {
        "en": (f"In the 14-digit Egyptian national ID number, which 2-digit code marks a holder born in {en} "
               f"Governorate? Give the two digits.", code, "numeric"),
        "ar": (f"في الرقم القومي المصري المكوّن من 14 رقمًا، ما الرمز المكوّن من رقمين الذي يدل على أن صاحب الرقم "
               f"وُلد في محافظة {ar}؟ اكتب الرقمين.", code, "numeric"),
    }
    return pair(pid, "id-code", f"{en} = {code}", SRC_ID, slip_code, rows)


def count_core(pid, seed, core_codes, others):
    """How many of 5 IDs were born in Cairo, Giza or Alexandria (codes 01, 21, 02)."""
    rng = random.Random(seed)
    codes = list(core_codes) + list(others)
    rng.shuffle(codes)
    ids = [make_id(rng, c)[0] for c in codes]
    n = sum(c in ("01", "21", "02") for c in codes)
    lst = "\n".join(f"{i + 1}. {x}" for i, x in enumerate(ids))
    rows = {
        "en": (f"These are fictional Egyptian national ID numbers:\n{lst}\nHow many of the holders were born in Cairo, "
               f"Giza or Alexandria governorates? Give the number.", str(n), "numeric"),
        "ar": (f"هذه أرقام قومية مصرية وهمية:\n{lst}\nكم عدد أصحابها الذين وُلدوا في محافظات القاهرة أو الجيزة أو "
               f"الإسكندرية؟ اكتب العدد.", str(n), "numeric"),
    }
    return pair(pid, "id-code", f"province codes {codes}; Cairo=01, Giza=21, Alexandria=02 -> {n}", SRC_ID,
                str(n + 1), rows)


def abroad(pid, seed):
    rng = random.Random(seed)
    nid, _ = make_id(rng, "88")
    rows = {
        "en": (f"This is a fictional Egyptian national ID number: {nid}. Where was the holder born? Answer in a few "
               f"words.", "|".join(ABROAD_EN), "answer_set"),
        "ar": (f"هذا رقم قومي مصري وهمي: {nid}. أين وُلد صاحبه؟ أجب في بضع كلمات.", "|".join(ABROAD_AR), "answer_set"),
    }
    return pair(pid, "id-code", f"province code 88 = outside the republic ({nid})", SRC_ID, "Cairo", rows)


def area(pid, city, slip):
    code, ar = AREA[city]
    rows = {
        "en": (f"What is the landline area code of {city}, Egypt? Give the digits without the leading 0.", code, "numeric"),
        "ar": (f"ما كود الاتصال الأرضي لمدينة {ar} في مصر؟ اكتب الأرقام بدون الصفر في البداية.", code, "numeric"),
    }
    return pair(pid, "area-code", f"{city} = 0{code}", SRC_AREA, slip, rows)


def build():
    t = []
    t += gov_from_id("eg-gov-01", 101, "13", "19")   # Sharqia vs Ismailia
    t += gov_from_id("eg-gov-02", 102, "25", "26")   # Asyut vs Sohag
    t += gov_from_id("eg-gov-03", 103, "32", "33")   # New Valley vs Matruh
    t += gov_from_id("eg-gov-04", 104, "18", "16")   # Beheira vs Gharbia
    t += gov_from_id("eg-gov-05", 105, "34", "35")   # North vs South Sinai
    t += gov_from_id("eg-gov-06", 106, "22", "23")   # Beni Suef vs Fayoum
    t += code_from_gov("eg-code-01", "27", "26")     # Qena
    t += code_from_gov("eg-code-02", "23", "22")     # Fayoum
    t += count_core("eg-count-01", 201, ["01", "21"], ["14", "17", "16"])
    t += count_core("eg-count-02", 202, ["02"], ["19", "03", "04", "12"])
    t += abroad("eg-abroad-01", 301)
    for i, (city, slip) in enumerate([("Tanta", "45"), ("Damanhur", "40"), ("Sohag", "96"), ("Beni Suef", "84")], 1):
        t += area(f"eg-area-0{i}", city, slip)
    for x in t:
        assert x["answer"] not in x["prompt"] or x["grader"] == "numeric", x["id"]
    return t


if __name__ == "__main__":
    tasks = build()
    OUT.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in tasks) + "\n", encoding="utf-8")
    print(len(tasks), "rows =", len(tasks) // 2, "tasks x 2 languages")
