import os
import csv
from pathlib import Path
from openai import OpenAI
from PIL import Image
import torch

# Konfiguracja
class Config:
    image_dir = "characters"
    output_csv = "characters.csv"
    tag_model_path = "SmilingWolf/wd-v1-4-convnext-tagger-v2"
    llm_config = {
        "base_url": "http://localhost:1234/v1",
        "api_key": "lm-studio",
        "model": "model-identifier"
    }
    background_types = ["mroczny", "tech", "fantasy", "secret"]
    weapon_types = ["slash", "puncture", "impact"]
    min_health = 5
    max_health = 99
    min_weapon = 1
    max_weapon = 20
    min_armor = 0
    max_armor = 12

# Inicjalizacja klienta LLM
llm_client = OpenAI(base_url=Config.llm_config["base_url"], 
                   api_key=Config.llm_config["api_key"])

# Ładowanie modelu tagowania
print("Ładowanie modelu tagowania...")
tagger = torch.hub.load('SmilingWolf/wd-v1-4-convnext-tagger-v2', 'model').eval()

def determine_background(tags):
    """Określa typ tła na podstawie tagów"""
    if any(t in tags for t in ["demon", "monster", "undead"]):
        return "mroczny"
    elif any(t in tags for t in ["robot", "cyborg", "futuristic"]):
        return "tech"
    elif any(t in tags for t in ["elf", "dwarf", "knight"]):
        return "fantasy"
    return "secret"

def generate_stats_with_llm(tags, background):
    """Generuje statystyki używając lokalnego LLM"""
    prompt = f"""GENERUJ POSTAĆ RPG:
Tagi: {', '.join(tags)}
Typ tła: {background}

Wygeneruj w formacie JSON:
- "name": unikalna imię fantasy
- "weapons": lista 1-2 typów broni ({Config.weapon_types}) z wartościami obrażeń (każda 1-20)
- "armors": lista 1-3 typów pancerzy ({Config.weapon_types}) z wartościami odporności (każda 0-12)
- "languages": 2-4 wymyślone nazwy języków

Przykład:
{{
  "name": "Gromthar",
  "weapons": {{"slash": 15, "puncture": 8}},
  "armors": {{"slash": 5, "impact": 3}},
  "languages": ["Dwarvish", "Old Tongue"]
}}"""

    response = llm_client.chat.completions.create(
        model=Config.llm_config["model"],
        messages=[
            {"role": "system", "content": "Zawsze odpowiadaj w formacie JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    
    return eval(response.choices[0].message.content)

def map_to_csv_row(image_path, background, data):
    """Mapuje dane do struktury CSV"""
    health = Config.min_health + sum(data.get("armors", {}).values())
    health = min(health, Config.max_health)  # Ogranicz max HP
    
    return {
        "name": data.get("name", ""),
        "background": background,
        "image": os.path.basename(image_path),
        "health": health,
        **{f"weapon_{i+1}_image": typ for i, typ in enumerate(data.get("weapons", {}).keys())},
        **{f"weapon_{i+1}": val for i, val in enumerate(data.get("weapons", {}).values())},
        **{f"armor_{i+1}_image": typ for i, typ in enumerate(data.get("armors", {}).keys())},
        **{f"armor_{i+1}": val for i, val in enumerate(data.get("armors", {}).values())},
        **{f"language_{i+1}": lang for i, lang in enumerate(data.get("languages", []))}
    }

# Główny proces przetwarzania
csv_header = ["name","background","image","health",
             "weapon_1_image","weapon_1","weapon_2_image","weapon_2","weapon_3_image","weapon_3",
             "armor_1_image","armor_1","armor_2_image","armor_2","armor_3_image","armor_3",
             "language_1","language_2","language_3","language_4"]

with open(Config.output_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=csv_header, delimiter=';')
    writer.writeheader()

    for img_path in Path(Config.image_dir).glob("*.png"):
        print(f"Przetwarzanie: {img_path.name}")
        
        try:
            # Generowanie tagów i określenie tła
            tags = generate_tags(img_path)
            background = determine_background(tags)
            
            # Generowanie statystyk
            llm_data = generate_stats_with_llm(tags, background)
            csv_row = map_to_csv_row(img_path, background, llm_data)
            
            writer.writerow(csv_row)
        except Exception as e:
            print(f"Błąd przetwarzania {img_path.name}: {str(e)}")

print("Generacja CSV zakończona!")