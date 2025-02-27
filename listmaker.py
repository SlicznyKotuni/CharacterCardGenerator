import os
import csv
import random
from pathlib import Path

# Konfiguracja
class Config:
    image_dir = "assets/characters"  # Teraz katalog z plikami .txt
    output_csv = "characters.csv"
    background_types = ["mroczny", "tech", "fantasy", "secret"]
    min_health_female = 5
    max_health_female = 75
    min_health_male = 5
    max_health_male = 95
    language_types = ["Rh'loq", "Wspólny", "Ancient_Runes", "Kristalion", "Heu'ia"]
    imiona_boy_file = "imiona_boy.txt"
    imiona_girl_file = "imiona_girl.txt"
    min_weapon_two_types = 5
    max_weapon_two_types = 10
    min_weapon_one_type = 8
    max_weapon_one_type = 12
    shield_value_min = 5
    shield_value_max = 10

def parse_character_file(txt_file_path):
    """Parsuje atrybuty postaci z pliku .txt."""
    attributes = {}
    try:
        with open(txt_file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            tags = content.split(',')  # Rozdziel tagi po przecinku
            for tag in tags:
                tag = tag.strip()
                if tag:  # Ignoruj puste tagi
                    key, value = tag.split("=", 1) if "=" in tag else (tag, "True")
                    attributes[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Warning: No attribute file found for {txt_file_path.name}")
        return None
    except ValueError as e:
        print(f"Warning: incorrect format in {txt_file_path.name}: {e}")
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

def determine_weapon_types_and_values(attributes):
    """Określa typy obrażeń broni i losuje wartości."""
    if not attributes:
        return {"weapon_1_image": "impact", "weapon_1": random.randint(8, 12),
                "weapon_2_image": "impact", "weapon_2": random.randint(8, 12)}

    weapon_tags = []
    for key, value in attributes.items():
        if "weapon" in key or key in ["sword", "axe", "dagger", "katana", "twohanded_sword", "long_sword", "battleaxe", "scimitar", "saber", "claymore", "rapier",
                                    "dart", "darts", "kunai", "spear", "polearm", "knife", "lance", "javelin", "arrow", "bow",
                                    "staff", "mace", "hammer", "fists", "martial_arts", "club", "flail", "warhammer", "quarterstaff", "baton",
                                    "shield", "heavy_shield", "kite_shield", "buckler", "tower_shield"]: #dodane nazwy broni jako pojedyncze tagi
            weapon_tags.extend(value.split(",")) if isinstance(value, str) else weapon_tags.append(key)

    slash_tags = ["sword", "axe", "dagger", "katana", "twohanded_sword", "long_sword", "battleaxe", "scimitar", "saber", "claymore", "rapier"]
    puncture_tags = ["dart", "darts", "kunai", "spear", "polearm", "sword", "knife", "rapier", "lance", "javelin", "arrow", "bow"]
    impact_tags = ["staff", "mace", "hammer", "fists", "martial_arts", "club", "flail", "warhammer", "quarterstaff", "baton"]
    shield_tags = ["shield", "heavy_shield", "kite_shield", "buckler", "tower_shield"]

    weapon_types = []
    if any(tag in weapon_tags for tag in slash_tags):
        weapon_types.append("slash")
    if any(tag in weapon_tags for tag in puncture_tags):
        weapon_types.append("puncture")
    if any(tag in weapon_tags for tag in impact_tags):
        weapon_types.append("impact")

    has_shield = any(tag in weapon_tags for tag in shield_tags)

    if len(weapon_types) == 0:
        weapon_types = ["impact"]  # Domyślny typ obrażeń

    if len(weapon_types) == 1:
        weapon_type = weapon_types[0]
        weapon_value = random.randint(Config.min_weapon_one_type, Config.max_weapon_one_type)
        return {
            "weapon_1_image": weapon_type,
            "weapon_1": weapon_value,
            "weapon_2_image": weapon_type,
            "weapon_2": weapon_value
        }
    elif len(weapon_types) >= 2:
        weapon_1_type = weapon_types[0]
        weapon_2_type = weapon_types[1]
        weapon_1_value = random.randint(Config.min_weapon_two_types, Config.max_weapon_two_types)
        weapon_2_value = random.randint(3, 8)
        
        if has_shield:
            weapon_2_type = "shield"
            weapon_2_value = random.randint(Config.shield_value_min, Config.shield_value_max)

        return {
            "weapon_1_image": weapon_1_type,
            "weapon_1": weapon_1_value,
            "weapon_2_image": weapon_2_type,
            "weapon_2": weapon_2_value
        }
    
    return {"weapon_1_image": "impact", "weapon_1": random.randint(8, 12),
                "weapon_2_image": "impact", "weapon_2": random.randint(8, 12)}

def determine_armor_types_and_values(attributes):
    """Określa typy odporności pancerza i losuje wartości."""
    armor_values = {
        "armor_1_image": {"type": "slash", "value": random.randint(3, 10)},
        "armor_2_image": {"type": "puncture", "value": random.randint(3, 10)},
        "armor_3_image": {"type": "impact", "value": random.randint(3, 10)}
    }

    if not attributes:
        return {
            "armor_1_image": "slash",
            "armor_1": armor_values["armor_1_image"]["value"],
            "armor_2_image": "puncture",
            "armor_2": armor_values["armor_2_image"]["value"],
            "armor_3_image": "impact",
            "armor_3": armor_values["armor_3_image"]["value"]
        }

    slash_armor_tags = ["heavy_armor", "plate_armor", "shoulder_armor", "chestplate", "full_plate", "scale_armor", "chainmail", "knight_armor"]
    puncture_armor_tags = ["armor", "leather_armor", "padded_armor", "studded_leather", "mail_coif", "breastplate", "brigandine"]
    impact_armor_tags = ["padded_armor", "gambeson", "heavy_armor", "plate_armor", "helm", "armored_boots", "gauntlets"]
    
    negative_armor_tags = ["naked", "clothes", "loincloth", "barefeet", "shirt", "tunic", "robe"]

    armor_tags = []
    for key, value in attributes.items():
        if "armor" in key or key in ["heavy_armor", "plate_armor", "shoulder_armor", "chestplate", "full_plate", "scale_armor", "chainmail", "knight_armor",
                                    "armor", "leather_armor", "padded_armor", "studded_leather", "mail_coif", "breastplate", "brigandine",
                                    "padded_armor", "gambeson", "helm", "armored_boots", "gauntlets", "naked", "clothes", "loincloth", "barefeet", "shirt", "tunic", "robe"]: #dodane nazwy zbroi jako pojedyncze tagi
            armor_tags.extend(value.split(",")) if isinstance(value, str) else armor_tags.append(key)

    # Modyfikatory na podstawie tagów zwiększających odporność
    for tag in armor_tags:
        if tag in slash_armor_tags:
            armor_values["armor_1_image"]["value"] += 2
        if tag in puncture_armor_tags:
            armor_values["armor_2_image"]["value"] += 2
        if tag in impact_armor_tags:
            armor_values["armor_3_image"]["value"] += 2

    # Modyfikatory obniżające odporność
    if any(tag in armor_tags for tag in negative_armor_tags):
        armor_values["armor_1_image"]["value"] = max(0, int(armor_values["armor_1_image"]["value"] * 0.7))
        armor_values["armor_2_image"]["value"] = max(0, int(armor_values["armor_2_image"]["value"] * 0.7))

    return {
        "armor_1_image": armor_values["armor_1_image"]["type"],
        "armor_1": armor_values["armor_1_image"]["value"],
        "armor_2_image": armor_values["armor_2_image"]["type"],
        "armor_2": armor_values["armor_2_image"]["value"],
        "armor_3_image": armor_values["armor_3_image"]["type"],
        "armor_3": armor_values["armor_3_image"]["value"]
    }

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

def map_to_csv_row(image_path, background, name, health, weapon_data, armor_data, languages):
    """Mapuje dane do struktury CSV"""
    return {
        "name": name,
        "background": background,
        "image": os.path.basename(image_path),
        "health": health,
        "weapon_1_image": weapon_data["weapon_1_image"],
        "weapon_1": weapon_data["weapon_1"],
        "weapon_2_image": weapon_data["weapon_2_image"],
        "weapon_2": weapon_data["weapon_2"],
        "armor_1_image": armor_data["armor_1_image"],
        "armor_1": armor_data["armor_1"],
        "armor_2_image": armor_data["armor_2_image"],
        "armor_2": armor_data["armor_2"],
        "armor_3_image": armor_data["armor_3_image"],
        "armor_3": armor_data["armor_3"],
        **{f"language_{i+1}": lang for i, lang in enumerate(languages)}
    }

# Główny proces przetwarzania
csv_header = ["name","background","image","health",
             "weapon_1_image","weapon_1","weapon_2_image","weapon_2",
             "armor_1_image","armor_1","armor_2_image","armor_2","armor_3_image","armor_3",
             "language_1","language_2","language_3","language_4"]

# Ładowanie list imion
imiona_boy = load_imiona(Config.imiona_boy_file)
imiona_girl = load_imiona(Config.imiona_girl_file)

with open(Config.output_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=csv_header, delimiter=';')
    writer.writeheader()

    for txt_path in Path(Config.image_dir).glob("*.txt"):  # Zmieniono na .txt
        print(f"Przetwarzanie: {txt_path.name}")

        try:
            # Parsowanie atrybutów z pliku
            attributes = parse_character_file(txt_path)

            # Określenie atrybutów
            background = determine_background(attributes)
            gender = determine_gender(attributes)
            name = get_name(gender)
            languages = determine_languages(attributes)
            weapon_data = determine_weapon_types_and_values(attributes)
            armor_data = determine_armor_types_and_values(attributes)
            health = determine_health(gender, attributes)
            
            csv_row = map_to_csv_row(txt_path, background, name, health, weapon_data, armor_data, languages)
            writer.writerow(csv_row)

        except Exception as e:
            print(f"Błąd przetwarzania {txt_path.name}: {str(e)}")
            # Optionally, print the traceback:
            import traceback
            traceback.print_exc()

print("Generacja CSV zakończona!")