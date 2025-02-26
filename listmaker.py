import os
import csv
from pathlib import Path
from PIL import Image
import torch
import random

# Konfiguracja
class Config:
    image_dir = "characters"
    output_csv = "characters.csv"
    tag_model_path = "SmilingWolf/wd-v1-4-convnext-tagger-v2"
    background_types = ["mroczny", "tech", "fantasy", "secret"]
    weapon_types = ["slash", "puncture", "impact"]
    min_health_female = 5
    max_health_female = 75
    min_health_male = 5
    max_health_male = 95
    min_weapon = 1
    max_weapon = 20
    min_armor = 0
    max_armor = 12
    language_types = ["Rh'loq", "Wspólny", "Ancient_Runes", "Kristalion", "Heu'ia"]
    imiona_boy_file = "imiona_boy.txt"
    imiona_girl_file = "imiona_girl.txt"

# Ładowanie modelu tagowania
print("Ładowanie modelu tagowania...")
tagger = torch.hub.load('SmilingWolf/wd-v1-4-convnext-tagger-v2', 'model').eval()

def generate_tags(image_path):
    """Generuje tagi dla obrazu używając modelu tagowania."""
    try:
        img = Image.open(image_path)
        with torch.no_grad():
            x = tagger.preprocess(img).unsqueeze(0)
            tags = tagger.model(x)
            probs, labels = tags.float().cpu().sort(descending=True)
            
            # Pobierz tagi z prawdopodobieństwem powyżej progu (np. 0.5)
            threshold = 0.5
            selected_tags = [label for prob, label in zip(probs[0], labels[0]) if prob > threshold]
            
            return selected_tags
    except Exception as e:
        print(f"Błąd podczas generowania tagów: {e}")
        return []

def determine_background(tags):
    """Określa typ tła na podstawie tagów"""
    if any(t in tags for t in ["demon", "monster", "undead"]):
        return "mroczny"
    elif any(t in tags for t in ["robot", "cyborg", "futuristic"]):
        return "tech"
    elif any(t in tags for t in ["elf", "dwarf", "knight"]):
        return "fantasy"
    return "secret"

def determine_gender(tags):
    """Określa płeć na podstawie tagów."""
    if any(t in tags for t in ["1girl", "female_focus"]):
        return "female"
    elif any(t in tags for t in ["1boy", "male_focus"]):
        return "male"
    else:
        return "unknown"  # Domyślna płeć, gdy nie można rozpoznać

def load_imiona(file_path):
    """Ładuje listę imion z pliku."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f]
    except FileNotFoundError:
        print(f"Plik z imionami nie znaleziony: {file_path}")
        return []

def get_name(gender):
    """Pobiera losowe imię z odpowiedniej listy."""
    if gender == "female":
        return random.choice(imiona_girl)
    elif gender == "male":
        return random.choice(imiona_boy)
    else:
        # Jeśli płeć nierozpoznana, można wybrać losowo z obu list
        return random.choice(imiona_girl + imiona_boy)

def determine_languages(tags):
    """Określa listę języków na podstawie tagów."""
    languages = []
    if any(t in tags for t in ["ancient", "old"]):
        languages.append("Rh'loq")
    if any(t in tags for t in ["elf", "dwarf", "human"]):
        languages.append("Wspólny")
    if any(t in tags for t in ["magic", "witch", "wizard"]):
        languages.append("Ancient_Runes")
    if any(t in tags for t in ["animal", "robot", "cyborg"]):
        languages.append("Kristalion")
    if any(t in tags for t in ["technology", "nature"]):
        languages.append("Heu'ia")
    return languages[:4]  # Maksymalnie 4 języki

def determine_weapons(tags):
    """Określa typy broni na podstawie tagów."""
    weapons = {}
    if any(t in tags for t in ["knife", "sword", "blade"]):
        weapons["slash"] = random.randint(Config.min_weapon, Config.max_weapon)
        weapons["puncture"] = random.randint(Config.min_weapon, Config.max_weapon)
    elif any(t in tags for t in ["fist", "bare_hands"]):
        weapons["impact"] = random.randint(Config.min_weapon, Config.max_weapon)
    # Dodaj więcej warunków na podstawie tagów i typów broni
    return weapons

def determine_armor(tags):
    """Określa typy pancerza na podstawie tagów."""
    armors = {}
    if any(t in tags for t in ["armor", "plate"]):
        armors["slash"] = random.randint(Config.min_armor, Config.max_armor)
        armors["impact"] = random.randint(Config.min_armor, Config.max_armor)
        armors["puncture"] = random.randint(Config.min_armor, Config.max_armor)
    elif any(t in tags for t in ["robe", "cloth"]):
        armors["magic"] = random.randint(Config.min_armor, Config.max_armor)
    # Dodaj więcej warunków na podstawie tagów i typów pancerza
    return armors

def determine_health(gender):
    """Losuje wartość życia w zależności od płci."""
    if gender == "female":
        return random.randint(Config.min_health_female, Config.max_health_female)
    elif gender == "male":
        return random.randint(Config.min_health_male, Config.max_health_male)
    else:
        # Domyślny zakres, gdy płeć nie jest znana
        return random.randint(Config.min_health_female, Config.max_health_male)

def map_to_csv_row(image_path, background, name, health, weapons, armors, languages):
    """Mapuje dane do struktury CSV"""
    return {
        "name": name,
        "background": background,
        "image": os.path.basename(image_path),
        "health": health,
        **{f"weapon_{i+1}_image": typ for i, typ in enumerate(weapons.keys())},
        **{f"weapon_{i+1}": val for i, val in enumerate(weapons.values())},
        **{f"armor_{i+1}_image": typ for i, typ in enumerate(armors.keys())},
        **{f"armor_{i+1}": val for i, val in enumerate(armors.values())},
        **{f"language_{i+1}": lang for i, lang in enumerate(languages)}
    }

# Główny proces przetwarzania
csv_header = ["name","background","image","health",
             "weapon_1_image","weapon_1","weapon_2_image","weapon_2","weapon_3_image","weapon_3",
             "armor_1_image","armor_1","armor_2_image","armor_2","armor_3_image","armor_3",
             "language_1","language_2","language_3","language_4"]

# Ładowanie list imion
imiona_boy = load_imiona(Config.imiona_boy_file)
imiona_girl = load_imiona(Config.imiona_girl_file)

with open(Config.output_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=csv_header, delimiter=';')
    writer.writeheader()

    for img_path in Path(Config.image_dir).glob("*.png"):
        print(f"Przetwarzanie: {img_path.name}")

        try:
            # Generowanie tagów i określenie tła
            tags = generate_tags(img_path)
            background = determine_background(tags)
            gender = determine_gender(tags)
            name = get_name(gender)
            languages = determine_languages(tags)
            weapons = determine_weapons(tags)
            armors = determine_armor(tags)
            health = determine_health(gender)

            csv_row = map_to_csv_row(img_path, background, name, health, weapons, armors, languages)
            writer.writerow(csv_row)

        except Exception as e:
            print(f"Błąd przetwarzania {img_path.name}: {str(e)}")

print("Generacja CSV zakończona!")