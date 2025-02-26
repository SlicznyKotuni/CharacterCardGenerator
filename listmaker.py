import os
import csv
from pathlib import Path
from PIL import Image
import random

# Konfiguracja
class Config:
    image_dir = "assets/characters"
    output_csv = "characters.csv"
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

def parse_character_file(image_path):
    """Parses the character attribute file."""
    txt_file_path = image_path.with_suffix(".txt")  # Assuming .txt extension

    attributes = {}
    try:
        with open(txt_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                key, value = line.strip().split("=", 1)  # Split into key and value
                attributes[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Warning: No attribute file found for {image_path.name}")
        return None
    except ValueError:
         print(f"Warning: incorrect format in {image_path.name}")
         return None
    return attributes

def determine_background(attributes):
    """Określa typ tła na podstawie atrybutów."""
    if attributes and "background" in attributes:
        return attributes["background"]
    else:
        return random.choice(Config.background_types)  # Default background if not specified

def determine_gender(attributes):
    """Określa płeć na podstawie atrybutów."""
    if attributes and "gender" in attributes:
        return attributes["gender"]
    else:
        return "unknown"

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

def determine_languages(attributes):
    """Określa listę języków na podstawie atrybutów."""
    if attributes and "languages" in attributes:
        return attributes["languages"].split(",")[:4]  # Split by comma, take max 4
    else:
        return random.sample(Config.language_types, random.randint(0, min(4, len(Config.language_types))))

def determine_weapons(attributes):
    """Określa typy broni na podstawie atrybutów."""
    weapons = {}
    if attributes:
        for i, weapon_type in enumerate(Config.weapon_types):
            key = f"weapon_{weapon_type}"
            if key in attributes:
                try:
                    weapons[weapon_type] = int(attributes[key])
                except ValueError:
                    weapons[weapon_type] = random.randint(Config.min_weapon, Config.max_weapon) #default value
                    print(f"incorrect weapon value for {weapon_type}, random value was assigned")
    return weapons

def determine_armor(attributes):
    """Określa typy pancerza na podstawie atrybutów."""
    armors = {}
    if attributes:
        for i, armor_type in enumerate(Config.weapon_types):
            key = f"armor_{armor_type}"
            if key in attributes:
                try:
                    armors[armor_type] = int(attributes[key])
                except ValueError:
                    armors[armor_type] = random.randint(Config.min_armor, Config.max_armor) #default value
                    print(f"incorrect armor value for {armor_type}, random value was assigned")
    return armors

def determine_health(gender, attributes):
    """Losuje wartość życia w zależności od płci."""
    health = None
    if attributes and "health" in attributes:
        try:
            health = int(attributes["health"])
        except ValueError:
            health = None
            print(f"incorrect health value, random value was assigned")

    if health is None:
        if gender == "female":
            health = random.randint(Config.min_health_female, Config.max_health_female)
        elif gender == "male":
            health = random.randint(Config.min_health_male, Config.max_health_male)
        else:
            # Domyślny zakres, gdy płeć nie jest znana
            health = random.randint(Config.min_health_female, Config.max_health_male)

    return health

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
            # Parsowanie atrybutów z pliku
            attributes = parse_character_file(img_path)

            # Określenie atrybutów
            background = determine_background(attributes)
            gender = determine_gender(attributes)
            name = get_name(gender)
            languages = determine_languages(attributes)
            weapons = determine_weapons(attributes)
            armors = determine_armor(attributes)
            health = determine_health(gender, attributes)

            csv_row = map_to_csv_row(img_path, background, name, health, weapons, armors, languages)
            writer.writerow(csv_row)

        except Exception as e:
            print(f"Błąd przetwarzania {img_path.name}: {str(e)}")

print("Generacja CSV zakończona!")