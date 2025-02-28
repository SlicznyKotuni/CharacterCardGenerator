import os
import random
import csv
from collections import defaultdict

# Ścieżki do katalogów i plików
CHARACTERS_DIR = "assets/characters"
GIRL_NAMES_FILE = "imiona_girl.txt"
BOY_NAMES_FILE = "imiona_boy.txt"
OUTPUT_CSV = "characters.csv"

# Definicje tagów dla teł (background)
BACKGROUNDS = {
    "fantasy": ["fantasy", "elf", "elven", "kobold"],
    "mroczny": ["knight", "necromancy", "dark", "evil", "demon", "horns"],
    "forest": ["animal", "beast", "catboy", "catgirl", "monster"],
    "tech": ["ancient", "technology", "sci-fi", "futuristic"],
    "magic": ["magic", "wizard", "spells", "casts"],
    "secret": []  # Domyślne tło dla niepasujących tagów
}

# Definicje tagów dla języków
LANGUAGES = {
    "Rh'lo": ["ancient", "older", "runes", "rune", "magic"],
    "Common": ["knight", "elven", "elf", "magic", "fantasy", "rpg"],
    "Ancient_Runes": ["magic", "wizard", "necromancy", "dragon", "demon", "monster"],
    "Kristalion": ["animal", "animalistic", "beast", "feline", "catgirl", "catboy", "anthropomorphic"],
"Durmali": ["dwarw", "runes", "rune", "wild", "tribal", "tribe", "primitive"],
"Fae'lin": ["fae", "ferry", "ferrytail", "butterfly", "butterfly_wings", "princes"],
"Kyo'ren": ["twisted", "alien", "abomination", "creature", "hommoculus", "tentacle", "tentacles", "mutated", "mutant"],
"Mijero": ["asian", "korean", "chinese", "japanese", "ninja", "geisha"],
"Nekrothol": ["wise", "other_space", "nebula", "cosmic", "dead"],
    "Heu'ia": ["secret", "egyptian", "inka", "dark", "ancient"]
}

# Tagi dla typów obrażeń (broń)
WEAPON_TAGS = {
    "slash": ["sword", "axe", "dagger", "katana", "twohanded_sword", "long_sword", "battleaxe", "scimitar", "saber", "claymore", "rapier"],
    "puncture": ["dart", "darts", "kunai", "spear", "polearm", "sword", "knife", "rapier", "lance", "javelin", "arrow", "bow"],
    "impact": ["staff", "mace", "hammer", "fists", "martial_arts", "club", "flail", "warhammer", "quarterstaff", "baton"]
}

# Tagi dla tarcz
SHIELD_TAGS = ["shield", "heavy_shield", "kite_shield", "buckler", "tower_shield"]

# Tagi dla pancerza (odporności)
ARMOR_TAGS = {
    "slash": ["heavy_armor", "plate_armor", "shoulder_armor", "chestplate", "full_plate", "scale_armor", "chainmail", "knight_armor"],
    "puncture": ["armor", "leather_armor", "padded_armor", "studded_leather", "mail_coif", "breastplate", "brigandine"],
    "impact": ["padded_armor", "gambeson", "heavy_armor", "plate_armor", "helm", "armored_boots", "gauntlets"]
}

# Tagi obniżające odporność pancerza
LOW_ARMOR_TAGS = ["naked", "clothes", "loincloth", "barefeet", "shirt", "tunic", "robe"]

# Tagi modyfikujące zdrowie
HEALTH_POSITIVE_TAGS = ["muscular", "strong", "tall"]
HEALTH_NEGATIVE_TAGS = ["petite", "skinny", "small", "little", "fragile"]

# Funkcja do wczytywania imion
def load_names(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# Funkcja do wczytywania tagów z pliku postaci
def load_tags(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [tag.strip() for tag in f.read().split(",") if tag.strip()]

# Funkcja do określania płci na podstawie tagów
def determine_gender(tags):
    if "1girl" in tags:
        return "girl"
    elif "1boy" in tags:
        return "boy"
    return random.choice(["girl", "boy"])  # Domyślna płeć, jeśli brak tagów

# Funkcja do losowania imienia na podstawie płci
def get_random_name(gender, girl_names, boy_names):
    if gender == "girl":
        return random.choice(girl_names)
    return random.choice(boy_names)

# Funkcja do określania tła na podstawie tagów
def determine_background(tags):
    for background, bg_tags in BACKGROUNDS.items():
        if any(tag in tags for tag in bg_tags):
            return background
    return "secret"  # Domyślne tło

# Funkcja do losowania zdrowia
def calculate_health(gender, tags):
    if gender == "boy":
        base_health = random.randint(15, 90)
    else:
        base_health = random.randint(10, 70)
    
    # Modyfikatory zdrowia
    for tag in tags:
        if tag in HEALTH_POSITIVE_TAGS:
            base_health += 5
        elif tag in HEALTH_NEGATIVE_TAGS:
            base_health -= 5
    
    # Ograniczenie zdrowia do rozsądnych wartości
    return max(10, min(base_health, 90))

# Funkcja do określania typów obrażeń na podstawie tagów
def determine_damage_types(tags):
    damage_types = set()
    for damage_type, weapon_tags in WEAPON_TAGS.items():
        if any(tag in tags for tag in weapon_tags):
            damage_types.add(damage_type)
    return list(damage_types) if damage_types else ["impact"]

# Funkcja do określania broni i tarcz
def determine_weapons(tags):
    damage_types = determine_damage_types(tags)
    has_shield = any(tag in tags for tag in SHIELD_TAGS)
    
    if has_shield:
        weapon_1_image = damage_types[0] if damage_types else "impact"
        weapon_2_image = "shield"
        weapon_1_value = random.randint(5, 10)
        weapon_2_value = random.randint(5, 10)  # Wartość dla tarczy
    else:
        if len(damage_types) >= 2:
            weapon_1_image = damage_types[0]
            weapon_2_image = damage_types[1]
            weapon_1_value = random.randint(5, 10)
            weapon_2_value = random.randint(3, 8)
        else:
            weapon_1_image = damage_types[0]
            weapon_2_image = damage_types[0]
            weapon_1_value = random.randint(8, 12)
            weapon_2_value = weapon_1_value
    
    return weapon_1_image, weapon_1_value, weapon_2_image, weapon_2_value, "impact", random.randint(3, 8)

# Funkcja do określania pancerza
def determine_armor(tags):
    armor_values = {
        "slash": random.randint(3, 10),
        "puncture": random.randint(3, 10),
        "impact": random.randint(3, 10)
    }
    
    # Modyfikatory pancerza
    for tag in tags:
        for armor_type, armor_tags in ARMOR_TAGS.items():
            if tag in armor_tags:
                armor_values[armor_type] += 2
    
    # Obniżenie odporności dla tagów wskazujących na brak pancerza
    if any(tag in tags for tag in LOW_ARMOR_TAGS):
        armor_values["slash"] = int(armor_values["slash"] * 0.7)
        armor_values["puncture"] = int(armor_values["puncture"] * 0.7)
    
    return armor_values["slash"], armor_values["puncture"], armor_values["impact"]

# Funkcja do obliczania evade
def calculate_evade(armor_sum):
    if 30 <= armor_sum <= 36:
        return 0
    elif 27 <= armor_sum <= 29:
        return 1
    elif 24 <= armor_sum <= 26:
        return 2
    elif 18 <= armor_sum <= 23:
        return 3
    elif 14 <= armor_sum <= 18:
        return 4
    elif 8 <= armor_sum <= 13:
        return 5
    elif 3 <= armor_sum <= 7:
        return 6
    return 0

# Funkcja do określania języków
def determine_languages(tags):
    possible_languages = set()
    for lang, lang_tags in LANGUAGES.items():
        if any(tag in tags for tag in lang_tags):
            possible_languages.add(lang)
    
    if not possible_languages:
        possible_languages.add("Common")  # Domyślny język
    
    num_languages = min(random.randint(1, 4), len(possible_languages))
    return random.sample(list(possible_languages), num_languages)

# Główna funkcja
def main():
    girl_names = load_names(GIRL_NAMES_FILE)
    boy_names = load_names(BOY_NAMES_FILE)
    
    characters = []
    
    # Wczytywanie tagów dla każdej postaci
    for file_name in os.listdir(CHARACTERS_DIR):
        if file_name.endswith(".txt"):
            file_path = os.path.join(CHARACTERS_DIR, file_name)
            tags = load_tags(file_path)
            image_name = file_name.replace(".txt", "")
            
            # Określanie płci i imienia
            gender = determine_gender(tags)
            name = get_random_name(gender, girl_names, boy_names)
            
            # Określanie tła
            background = determine_background(tags)
            
            # Obliczanie zdrowia
            health = calculate_health(gender, tags)
            
            # Określanie broni
            weapon_1_image, weapon_1, weapon_2_image, weapon_2, weapon_3_image, weapon_3 = determine_weapons(tags)
            
            # Określanie pancerza
            armor_1, armor_2, armor_3 = determine_armor(tags)
            armor_sum = armor_1 + armor_2 + armor_3
            evade = calculate_evade(armor_sum)
            
            # Określanie języków
            languages = determine_languages(tags)
            languages.extend([""] * (4 - len(languages)))  # Wypełnienie pustymi wartościami
            
            # Tworzenie rekordu postaci
            character = [
                name, background, image_name, health,
                weapon_1_image, weapon_1, weapon_2_image, weapon_2, weapon_3_image, weapon_3,
                "slash", armor_1, "puncture", armor_2, "impact", armor_3,
                evade, languages[0], languages[1], languages[2], languages[3]
            ]
            characters.append(character)
    
    # Zapisywanie do pliku CSV
    headers = [
        "name", "background", "image", "health",
        "weapon_1_image", "weapon_1", "weapon_2_image", "weapon_2", "weapon_3_image", "weapon_3",
        "armor_1_image", "armor_1", "armor_2_image", "armor_2", "armor_3_image", "armor_3",
        "evade", "language_1", "language_2", "language_3", "language_4"
    ]
    
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(characters)

if __name__ == "__main__":
    main()