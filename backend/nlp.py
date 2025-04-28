import spacy, json, rapidfuzz, dateparser
from langdetect import detect
from pathlib import Path
from typing import Optional

# large spaCy models (downloaded automatically)
nlp_fr = spacy.load("fr_core_news_lg")
nlp_en = spacy.load("en_core_web_lg")

SPECIALTIES = json.loads(Path(__file__).with_name("specialty_map.json").read_text())

def normalize_specialty(text: str) -> Optional[str]:
    low = text.lower()
    for syn, canon in SPECIALTIES.items():
        if syn in low:
            return canon
    choices = list(set(SPECIALTIES.values()))
    best = rapidfuzz.process.extractOne(low, choices, score_cutoff=80)
    return best[0] if best else None

def parse_dt(text: str, lang: str):
    settings = {"PREFER_DATES_FROM":"future", "TIMEZONE":"Europe/Paris"}
    return dateparser.parse(text, settings=settings, languages=[lang])

def extract(text: str):
    lang = "fr" if detect(text) == "fr" else "en"
    doc  = nlp_fr(text) if lang == "fr" else nlp_en(text)

    specialty = normalize_specialty(text)
    location  = next((e.text for e in doc.ents if e.label_ in ("GPE","LOC")), None)

    date_str  = " ".join(e.text for e in doc.ents if e.label_ in ("DATE","TIME"))
    dt        = parse_dt(date_str, lang) if date_str else None

    return {
        "lang": lang,
        "specialty": specialty,
        "location": location,
        "date": dt.date().isoformat() if dt else None,
        "time": dt.time().isoformat() if dt else None
    }
