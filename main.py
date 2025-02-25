import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os

class RPGCardGenerator:
    def __init__(self):
        # Konfiguracja wymiarów
        self.card_size = (1368, 912)
        self.character_size = (1216, 832)
        self.ui_elements = {
            'weapon_slots': {
                'positions': [(50, 400), (50, 580)],
                'size': (180, 180)  # 1:1 ratio
            },
            'armor_slots': {
                'positions': [(1120, 400), (1120, 540), (1120, 680)],
                'size': (150, 150)
            },
            'health': {
                'position': (1250, 50),
                'size': (100, 100)  # 1:1
            },
            'name_plate': {
                'size': (800, 120),  # Nowy element graficzny
                'position': (284, 740)
            },
            'name': {
                'position': (684, 780),
                'max_length': 24,
                'font_size': 48
            },
            'languages': {
                'size': (80, 80),  # 1:1
                'margin': 20,
                'position_y': 820
            }
        }

        self.paths = {
            'backgrounds': 'assets/backgrounds',
            'characters': 'assets/characters',
            'weapons': 'assets/weapons',
            'armors': 'assets/armors',
            'languages': 'assets/languages',
            'ui': 'assets/ui_elements',
            'fonts': 'assets/fonts',
            'output': 'output'
        }

    def generate_from_file(self, input_file):
        df = self._load_data(input_file)
        for _, row in df.iterrows():
            card = self._create_base_card(row['background'])
            card = self._add_character(card, row['character_image'])
            card = self._add_weapons(card, row)
            card = self._add_armors(card, row)
            card = self._add_name_plate(card)
            card = self._add_ui_elements(card)
            card = self._add_text(card, row)
            card = self._add_languages(card, row)
            self._save_card(card, row['name'])

    def _add_name_plate(self, card):
        """Dodaje graficzną płytkę pod nazwę i języki"""
        plate = Image.open(os.path.join(self.paths['ui'], 'name_plate.png'))
        plate = plate.resize(self.ui_elements['name_plate']['size'])
        position = self.ui_elements['name_plate']['position']
        card.alpha_composite(plate, position)
        return card

    def _add_languages(self, card, data):
        """Dodaje ikony języków"""
        languages = data['languages'].split(',')
        total_width = (len(languages) * self.ui_elements['languages']['size'][0] + 
                      (len(languages)-1) * self.ui_elements['languages']['margin'])
        
        start_x = (self.card_size[0] - total_width) // 2
        
        for i, lang in enumerate(languages):
            lang = lang.strip()
            lang_img = Image.open(os.path.join(self.paths['languages'], f"{lang}.png"))
            lang_img = lang_img.resize(self.ui_elements['languages']['size'])
            
            x = start_x + i * (self.ui_elements['languages']['size'][0] + 
                self.ui_elements['languages']['margin'])
            position = (x, self.ui_elements['languages']['position_y'])
            
            card.alpha_composite(lang_img, position)
        return card

    def _add_weapons(self, card, data):
        """Nowe skalowanie broni"""
        for i, pos in enumerate(self.ui_elements['weapon_slots']['positions'], 1):
            weapon = Image.open(os.path.join(
                self.paths['weapons'],
                f"{data[f'weapon_{i}']}.png"
            ))
            weapon = self._smart_resize(weapon, self.ui_elements['weapon_slots']['size'])
            card.alpha_composite(weapon, pos)
        return card

    def _smart_resize(self, image, target_size):
        """Inteligentne skalowanie z zachowaniem proporcji"""
        image.thumbnail((target_size[0]*2, target_size[1]*2), Image.Resampling.LANCZOS)
        return image.crop((
            (image.width - target_size[0])//2,
            (image.height - target_size[1])//2,
            (image.width + target_size[0])//2,
            (image.height + target_size[1])//2
        ))

    # Pozostałe metody pozostają jak w poprzedniej wersji z odpowiednimi poprawkami pozycji

# Konfiguracja assetów:
"""
Wymagane pliki:
- assets/ui_elements/name_plate.png (800x120) - dekoracyjna płytka
- assets/weapons/*.png (1024x1024)
- assets/languages/*.png (1024x1024)
- assets/armors/*.png (1024x1024)
- assets/ui_elements/health_icon.png (1024x1024)

Struktura folderów:
assets/
├── languages/
│   ├── Drakonii.png
│   ├── Urghish.png
│   └── Eldritch.png
└── ui_elements/
    ├── name_plate.png
    └── health_icon.png
"""

# Przykładowe dane CSV:
"""
name,background,character_image,weapon_1,weapon_2,armor_1,armor_2,armor_3,health,languages
Gromthar,dungeon,warrior,axe,shield,chestplate,helmet,boots,150,Drakonii, Urghish, Eldritch
"""