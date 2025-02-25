import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os

class RPGCardGenerator:
    def __init__(self):
        self.card_size = (1368, 912)
        self.character_size = (1216, 832)
        
        self.ui_config = {
            'weapons': {
                'positions': [(50, 400), (50, 580)],
                'size': (200, 200),
                'label_offset': (100, 170)
            },
            'armors': {
                'positions': [(1120, 400), (1120, 540), (1120, 680)],
                'size': (150, 150),
                'label_offset': (75, 125)
            },
            'health': {
                'position': (1250, 50),
                'size': (100, 100),
                'font_size': 32
            },
            'name_plate': {
                'size': (800, 120),
                'position': (284, 740)
            },
            'name': {
                'position': (684, 780),
                'font_size': 48,
                'max_length': 24
            },
            'languages': {
                'icon_size': (80, 80),
                'max_count': 4,
                'margin': 30,
                'position_y': 820
            }
        }

        self.assets_path = {
            'backgrounds': 'assets/backgrounds',
            'characters': 'assets/characters',
            'weapons': 'assets/weapons',
            'armors': 'assets/armors',
            'languages': 'assets/languages',
            'ui': 'assets/ui_elements',
            'fonts': 'assets/fonts',
            'output': 'output'
        }

        # Ładowanie czcionki
        self.font = ImageFont.truetype(
            os.path.join(self.assets_path['fonts'], 'PressJobs.ttf'), 
            size=24
        )

    def generate_from_file(self, csv_path):
        df = pd.read_csv(csv_path, sep=';')  # Zmiana separatora na średnik
        for _, row in df.iterrows():
            card = self._create_card(row)
            self._save_card(card, row['name'])

    def _create_card(self, data):
        # Baza karty
        card = Image.open(f"{self.assets_path['backgrounds']}/{data['background']}.png").convert('RGBA')
        
        # Elementy karty
        card = self._add_character(card, data['image'])
        card = self._add_combat_elements(card, data)
        card = self._add_name_plate(card, data)
        card = self._add_languages(card, data)
        
        return card

    def _add_character(self, card, character_img):
        character = Image.open(f"{self.assets_path['characters']}/{character_img}.png").convert('RGBA')
        character_pos = (
            (self.card_size[0] - self.character_size[0]) // 2,
            40
        )
        card.alpha_composite(character, character_pos)
        return card

    def _add_combat_elements(self, card, data):
        # Broń
        for i in range(1, 3):
            if pd.notna(data[f'weapon_{i}_image']):
                card = self._add_weapon(
                    card, 
                    data[f'weapon_{i}_image'], 
                    data[f'weapon_{i}'], 
                    self.ui_config['weapons']['positions'][i-1]
                )

        # Pancerz
        for i in range(1, 4):
            if pd.notna(data[f'armor_{i}_image']):
                card = self._add_armor(
                    card,
                    data[f'armor_{i}_image'],
                    data[f'armor_{i}'],
                    self.ui_config['armors']['positions'][i-1]
                )

        # Punkty życia
        health_icon = Image.open(f"{self.assets_path['ui']}/health_icon.png")
        health_icon = health_icon.resize(self.ui_config['health']['size'])
        card.alpha_composite(health_icon, self.ui_config['health']['position'])
        
        draw = ImageDraw.Draw(card)
        draw.text(
            (self.ui_config['health']['position'][0] + 50, 
             self.ui_config['health']['position'][1] + 50),
            str(data['health']),
            font=self.font.font_variant(size=self.ui_config['health']['font_size']),
            fill='white',
            anchor='mm'
        )
        
        return card

def _add_weapon(self, card, img_name, value, position):
        weapon_img = Image.open(f"{self.assets_path['weapons']}/{img_name}.png")
        weapon_img = weapon_img.resize(self.ui_config['weapons']['size'])
        
        # Dodanie wartości
        draw = ImageDraw.Draw(weapon_img)
        text_position = (
            self.ui_config['weapons']['label_offset'][0],
            self.ui_config['weapons']['label_offset'][1]
        )
        draw.text(
            text_position,
            str(value),
            font=self.font,
            fill='white',
            anchor='mm'
        )
        
        card.alpha_composite(weapon_img, position)
        return card

    def _add_armor(self, card, img_name, value, position):  
        armor_img = Image.open(f"{self.assets_path['armors']}/{img_name}.png")
        armor_img = armor_img.resize(self.ui_config['armors']['size'])
        
        # Dodanie wartości
        draw = ImageDraw.Draw(armor_img)
        draw.text(
            self.ui_config['armors']['label_offset'],
            str(value),
            font=self.font,
            fill='white',
            anchor='mm'
        )
        
        card.alpha_composite(armor_img, position)
        return card

   def _add_name_plate(self, card, data):
        print(f"Adding name plate for: {data['name']}") #DEBUG
        plate = Image.open(f"{self.assets_path['ui']}/name_plate.png")
        plate = Image.open(f"{self.assets_path['ui']}/name_plate.png")
        print(f"Original plate size: {plate.size}") #DEBUG
        print(f"Name plate size from config: {self.ui_config['name_plate']['size']}") #DEBUG
        plate = plate.resize(self.ui_config['name_plate']['size'])
        print(f"Resized plate size: {plate.size}") #DEBUG
        print(f"Card size before composite: {card.size}") #DEBUG
        print(f"Name plate position: {self.ui_config['name_plate']['position']}") #DEBUG

        card.alpha_composite(plate, self.ui_config['name_plate']['position'])
        print(f"Card size after composite: {card.size}") #DEBUG  # ADDED
        print(f"Plate size after composite: {plate.size}") #DEBUG  # ADDED
        
        draw = ImageDraw.Draw(card)
        draw.text(
            self.ui_config['name']['position'],
            data['name'],
            font=self.font.font_variant(size=self.ui_config['name']['font_size']),
            fill='white',
            anchor='mm'
        )
        
        return card

    def _add_languages(self, card, data):
        languages = [data[f'language_{i}'] for i in range(1,6) if pd.notna(data.get(f'language_{i}'))]
        num_langs = min(len(languages), self.ui_config['languages']['max_count'])
        
        if num_langs == 0:
            return card

        total_width = (num_langs * self.ui_config['languages']['icon_size'][0] + 
                     (num_langs - 1) * self.ui_config['languages']['margin'])
        start_x = (self.card_size[0] - total_width) // 2
        
        for i in range(num_langs):
            lang_img = Image.open(
                f"{self.assets_path['languages']}/{languages[i]}.png"
            ).resize(self.ui_config['languages']['icon_size'])
            
            x = start_x + i * (
                self.ui_config['languages']['icon_size'][0] + 
                self.ui_config['languages']['margin']
            )
            position = (x, self.ui_config['languages']['position_y'])
            card.alpha_composite(lang_img, position)
        
        return card

    def _save_card(self, card, name):
        """Zapisuje gotową kartę do folderu output"""
        os.makedirs(self.assets_path['output'], exist_ok=True)
        output_path = os.path.join(self.assets_path['output'], f"{name}.png")
        card.save(output_path)
        print(f"Zapisano kartę: {output_path}")

    def _load_image(self, path, size=None):
        """Bezpieczne ładowanie obrazów z obsługą błędów"""
        try:
            img = Image.open(path).convert('RGBA')
            if size:
                img = img.resize(size)
            return img
        except FileNotFoundError:
            print(f"Błąd: Nie znaleziono pliku {path}")
            return None
        except Exception as e:
            print(f"Błąd podczas ładowania obrazu {path}: {str(e)}")
            return None

    def _validate_data(self, data):
        """Sprawdza poprawność danych wejściowych"""
        required_fields = [
            'name', 'background', 'image', 'health',
            'weapon_1_image', 'weapon_1',
            'armor_1_image', 'armor_1'
        ]
        
        for field in required_fields:
            if pd.isna(data[field]):
                raise ValueError(f"Brakujące wymagane pole: {field}")
                
        if not isinstance(data['health'], (int, float)):
            raise ValueError("Wartość zdrowia musi być liczbą")
            
        for i in range(1, 3):
            if pd.notna(data[f'weapon_{i}']) and not isinstance(data[f'weapon_{i}'], (int, float)):
                raise ValueError(f"Wartość broni {i} musi być liczbą")
                
        for i in range(1, 4):
            if pd.notna(data[f'armor_{i}']) and not isinstance(data[f'armor_{i}'], (int, float)):
                raise ValueError(f"Wartość pancerza {i} musi być liczbą")

    def _setup_logging(self):
        """Konfiguracja systemu logowania"""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('card_generator.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

# Przykładowe użycie:
if __name__ == "__main__":
    generator = RPGCardGenerator()
    
    # Przykładowy CSV (rozdzielany tabulatorami):
    """
    name    background  image   health  weapon_1_image weapon_1 weapon_2_image weapon_2 armor_1_image armor_1 armor_2_image armor_2 armor_3_image armor_3 language_1 language_2 language_3 language_4 language_5
    Gromthar    dungeon warrior 150 sword_icon   12  axe_icon    8   plate_icon   15  helm_icon    5   boots_icon   3   Drakonii    Urghish Eldritch   Shadowtongue
    """
    
    generator.generate_from_file('list.csv')