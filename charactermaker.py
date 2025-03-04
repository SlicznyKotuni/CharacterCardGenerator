import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import logging

class RPGCardGenerator:
    def __init__(self):
        self.card_size = (912, 1368)
        self.character_size = (800, 700)
        self.ui_config = {
            'weapons': {
                'positions': [(50, 300), (50, 430)],  # Adjusted positions, touching, left side
                'size': (120, 120),
                'label_offset': (40, 40),
                'font_size': 46
            },
            'armors': {
                'positions': [(742, 300), (742, 430), (742, 560)],  # Adjusted positions, touching, right side
                'size': (120, 120),
                'label_offset': (40, 40),
                'font_size': 46
            },
            'health': {
                'position': (732, 55),
                'size': (150, 150),
                'font_size': 76
            },
            'evade': {
                'position': (50, 55),  # Lewy górny róg
                'size': (150, 150),
                'font_size': 76
            },
            'name_plate': {
                'size': (600, 100),
                'position': ((912 - 600) // 2, 1050)
            },
            'name': {
                'position': (912 // 2, 1110),
                'font_size': 50,
                'max_length': 24
            },
            'languages': {
                'icon_size': (150, 150),
                'max_count': 4,
                'margin': 30,
                'position_y': 1200
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
        self.setup_logging()
        self.font = self._load_font()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('card_generator.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _load_font(self):
        font_path = os.path.join(self.assets_path['fonts'], 'PressJobs.ttf')
        try:
            return ImageFont.truetype(font_path, size=24)
        except IOError as e:
            self.logger.error(f"Failed to load font from {font_path}: {e}")
            try:
                return ImageFont.load_default()
            except IOError:
                self.logger.error("Failed to load default font.")
                raise

    def generate_from_file(self, csv_path):
        try:
            df = pd.read_csv(csv_path, sep=',')
            for _, row in df.iterrows():
                try:
                    self._validate_data(row)
                    card = self._create_card(row)
                    self._save_card(card, row['name'])
                except ValueError as e:
                    self.logger.error(f"Data validation error for {row['name']}: {e}")
                except Exception as e:
                    self.logger.exception(f"Failed to generate card for {row['name']}")
        except FileNotFoundError:
            self.logger.error(f"CSV file not found: {csv_path}")
        except pd.errors.EmptyDataError:
            self.logger.error(f"CSV file is empty: {csv_path}")
        except pd.errors.ParserError:
            self.logger.error(f"Error parsing CSV file: {csv_path}")
        except Exception as e:
            self.logger.exception(f"An unexpected error occurred while processing {csv_path}")

    def _add_text_with_glow(self, draw, position, text, font, text_color='white', glow_color='red', glow_radius=1):
        """Helper function to add text with neon glow effect"""
        # Rysowanie poświaty
        for offset_x in range(-glow_radius, glow_radius + 1):
            for offset_y in range(-glow_radius, glow_radius + 1):
                # Sprawdzamy, czy offset mieści się w okręgu, aby uzyskać bardziej okrągłą poświatę
                if offset_x**2 + offset_y**2 <= glow_radius**2:
                    draw.text(
                        (position[0] + offset_x, position[1] + offset_y),
                        text,
                        font=font,
                        fill=glow_color,
                        anchor='mm'
                    )
        
        # Rysowanie głównego tekstu
        draw.text(
            position,
            text,
            font=font,
            fill=text_color,
            anchor='mm'
        )

    def _create_card(self, data):
        try:
            background_path = os.path.join(self.assets_path['backgrounds'], f"{data['background']}.png")
            card = Image.open(background_path).convert('RGBA')
        except FileNotFoundError:
            self.logger.error(f"Background image not found: {data['background']}")
            return None
        except Exception as e:
            self.logger.error(f"Error opening background image: {data['background']}")
            return None

        card = self._add_character(card, data['image'])
        card = self._add_combat_elements(card, data)
        card = self._add_name_plate(card, data)
        card = self._add_languages(card, data)
        return card

    def _add_character(self, card, character_img):
        try:
            character_path = os.path.join(self.assets_path['characters'], f"{character_img}.png")
            character = Image.open(character_path).convert('RGBA')
        except FileNotFoundError:
            self.logger.error(f"Character image not found: {character_img}")
            return card
        except Exception as e:
            self.logger.error(f"Error opening character image: {character_img}: {e}")
            return card

        character_pos = (
            (self.card_size[0] - self.character_size[0]) // 2 - 20,
            50
        )

        # Tworzenie maski z gradientem
        mask = Image.new('L', character.size, 0)
        draw = ImageDraw.Draw(mask)
        
        # Główny prostokąt z pełną nieprzezroczystością
        width, height = character.size
        margin = 100  # Szerokość obszaru gradientu
        
        # Rysowanie środkowego obszaru z pełną nieprzezroczystością
        draw.rectangle((margin, margin, width-margin, height-margin), fill=255)
        
        # Gradientowe krawędzie
        for i in range(margin):
            # Obliczanie wartości alpha dla danego piksela gradientu (0-255)
            alpha = int(255 * (i / margin))
            
            # Górna krawędź
            draw.rectangle((margin, i, width-margin, i+1), fill=alpha)
            # Dolna krawędź
            draw.rectangle((margin, height-i-1, width-margin, height-i), fill=alpha)
            # Lewa krawędź
            draw.rectangle((i, margin, i+1, height-margin), fill=alpha)
            # Prawa krawędź
            draw.rectangle((width-i-1, margin, width-i, height-margin), fill=alpha)
        
        # Dodanie rozmycia dla płynniejszego przejścia
        mask = mask.filter(ImageFilter.GaussianBlur(radius=15))
        
        # Zastosowanie maski do kanału alfa postaci
        character.putalpha(mask)
        
        # Nałożenie postaci na kartę
        card.alpha_composite(character, character_pos)
        return card

    def _add_combat_elements(self, card, data):
        card = self._add_weapons(card, data)
        card = self._add_armors(card, data)
        card = self._add_health(card, data)
        card = self._add_evade(card, data)
        return card

    def _add_weapons(self, card, data):
        for i in range(1, 3):
            weapon_image_key = f'weapon_{i}_image'
            weapon_value_key = f'weapon_{i}'
            if pd.notna(data.get(weapon_image_key)) and pd.notna(data.get(weapon_value_key)):
                card = self._add_weapon(
                    card,
                    data[weapon_image_key],
                    data[weapon_value_key],
                    self.ui_config['weapons']['positions'][i - 1]
                )
        return card

    def _add_armors(self, card, data):
        for i in range(1, 4):
            armor_image_key = f'armor_{i}_image'
            armor_value_key = f'armor_{i}'
            if pd.notna(data.get(armor_image_key)) and pd.notna(data.get(armor_value_key)):
                card = self._add_armor(
                    card,
                    data[armor_image_key],
                    data[armor_value_key],
                    self.ui_config['armors']['positions'][i - 1]
                )
        return card

    def _add_weapon(self, card, img_name, value, position):
        try:
            weapon_path = os.path.join(self.assets_path['weapons'], f"{img_name}.png")
            weapon_img = Image.open(weapon_path).convert("RGBA")
            weapon_img = weapon_img.resize(self.ui_config['weapons']['size'])

            draw = ImageDraw.Draw(weapon_img)
            font = self.font.font_variant(size=self.ui_config['weapons']['font_size'])
            
            # Obliczamy centrum ikony
            center_x = self.ui_config['weapons']['size'][0] // 2
            center_y = self.ui_config['weapons']['size'][1] // 2
            
            # Dodajemy półprzezroczyste tło pod tekstem
            bbox = draw.textbbox((0, 0), str(value), font=font, anchor='mm')
            padding = 8
            background_size = (
                bbox[2] - bbox[0] + padding * 2,
                bbox[3] - bbox[1] + padding * 2
            )
            background = Image.new('RGBA', weapon_img.size, (0, 0, 0, 0))
            background_draw = ImageDraw.Draw(background)
            
            # Rysujemy okrągłe tło
            circle_radius = max(background_size) // 2
            background_draw.ellipse(
                (center_x - circle_radius, center_y - circle_radius,
                 center_x + circle_radius, center_y + circle_radius),
                fill=(0, 0, 0, 160)
            )
            
            # Nakładamy tło na broń
            weapon_img = Image.alpha_composite(weapon_img, background)
            draw = ImageDraw.Draw(weapon_img)
            
            # Dodajemy tekst z poświatą
            self._add_text_with_glow(
                draw,
                (center_x, center_y),
                str(value),
                font,
                text_color='white',
                glow_color='red',
                glow_radius=1
            )

            card.alpha_composite(weapon_img, position)
        except FileNotFoundError:
            self.logger.error(f"Weapon image not found: {img_name}")
        except Exception as e:
            self.logger.error(f"Error adding weapon {img_name}: {e}")
        return card

    def _add_armor(self, card, img_name, value, position):
        try:
            armor_path = os.path.join(self.assets_path['armors'], f"{img_name}.png")
            armor_img = Image.open(armor_path).convert("RGBA")
            armor_img = armor_img.resize(self.ui_config['armors']['size'])

            draw = ImageDraw.Draw(armor_img)
            font = self.font.font_variant(size=self.ui_config['armors']['font_size'])
            
            # Obliczamy centrum ikony
            center_x = self.ui_config['armors']['size'][0] // 2
            center_y = self.ui_config['armors']['size'][1] // 2
            
            # Dodajemy półprzezroczyste tło pod tekstem
            bbox = draw.textbbox((0, 0), str(value), font=font, anchor='mm')
            padding = 8
            background_size = (
                bbox[2] - bbox[0] + padding * 2,
                bbox[3] - bbox[1] + padding * 2
            )
            background = Image.new('RGBA', armor_img.size, (0, 0, 0, 0))
            background_draw = ImageDraw.Draw(background)
            
            # Rysujemy okrągłe tło
            circle_radius = max(background_size) // 2
            background_draw.ellipse(
                (center_x - circle_radius, center_y - circle_radius,
                 center_x + circle_radius, center_y + circle_radius),
                fill=(0, 0, 0, 160)
            )
            
            # Nakładamy tło na pancerz
            armor_img = Image.alpha_composite(armor_img, background)
            draw = ImageDraw.Draw(armor_img)
            
            # Dodajemy tekst z poświatą
            self._add_text_with_glow(
                draw,
                (center_x, center_y),
                str(value),
                font,
                text_color='white',
                glow_color='red',
                glow_radius=1
            )

            card.alpha_composite(armor_img, position)
        except FileNotFoundError:
            self.logger.error(f"Armor image not found: {img_name}")
        except Exception as e:
            self.logger.error(f"Error adding armor {img_name}: {e}")
        return card

    def _add_health(self, card, data):
        try:
            health_icon_path = os.path.join(self.assets_path['ui'], 'health_icon.png')
            health_icon = Image.open(health_icon_path).convert("RGBA")
            health_icon = health_icon.resize(self.ui_config['health']['size'])
            
            # Obliczamy centrum ikony zdrowia
            center_x = self.ui_config['health']['size'][0] // 2
            center_y = self.ui_config['health']['size'][1] // 2
            
            draw = ImageDraw.Draw(health_icon)
            font = self.font.font_variant(size=self.ui_config['health']['font_size'])
            
            # Dodajemy tekst z poświatą na ikonie zdrowia
# Dodajemy tekst z poświatą na ikonie zdrowia
            self._add_text_with_glow(
                draw,
                (center_x, center_y),
                str(data['health']),
                font,
                text_color='white',
                glow_color='red',
                glow_radius=1
            )
            
            card.alpha_composite(health_icon, self.ui_config['health']['position'])
        except FileNotFoundError:
            self.logger.error("Health icon not found.")
        except Exception as e:
            self.logger.error(f"Error adding health: {e}")
        return card

    def _add_evade(self, card, data):
        try:
            evade_icon_path = os.path.join(self.assets_path['ui'], 'evade.png')
            evade_icon = Image.open(evade_icon_path).convert("RGBA")
            evade_icon = evade_icon.resize(self.ui_config['evade']['size'])
            
            # Obliczamy centrum ikony uniku
            center_x = self.ui_config['evade']['size'][0] // 2
            center_y = self.ui_config['evade']['size'][1] // 2
            
            draw = ImageDraw.Draw(evade_icon)
            font = self.font.font_variant(size=self.ui_config['evade']['font_size'])
            
            # Dodajemy tekst z poświatą na ikonie uniku
            self._add_text_with_glow(
                draw,
                (center_x, center_y),
                str(data['evade']),
                font,
                text_color='white',
                glow_color='red',
                glow_radius=1
            )
            
            card.alpha_composite(evade_icon, self.ui_config['evade']['position'])
        except FileNotFoundError:
            self.logger.error("Evade icon not found.")
        except Exception as e:
            self.logger.error(f"Error adding evade: {e}")
        return card

    def _add_name_plate(self, card, data):
        try:
            plate_path = os.path.join(self.assets_path['ui'], 'name_plate.png')
            plate = Image.open(plate_path).convert("RGBA")
            plate = plate.resize(self.ui_config['name_plate']['size'])
            card.alpha_composite(plate, self.ui_config['name_plate']['position'])

            draw = ImageDraw.Draw(card)
            text = data['name']
            font = self.font.font_variant(size=self.ui_config['name']['font_size'])
            
            # Dodajemy tekst z poświatą dla imienia
            self._add_text_with_glow(
                draw,
                self.ui_config['name']['position'],
                text,
                font,
                text_color='white',
                glow_color='red',
                glow_radius=2  # Większy promień poświaty dla imienia
            )

        except FileNotFoundError:
            self.logger.error("Name plate image not found.")
        except Exception as e:
            self.logger.error(f"Error adding name plate: {e}")
        return card

    def _add_languages(self, card, data):
        languages = [data.get(f'language_{i}') for i in range(1, 6) if pd.notna(data.get(f'language_{i}'))]
        num_langs = min(len(languages), self.ui_config['languages']['max_count'])

        if num_langs == 0:
            return card

        total_width = (num_langs * self.ui_config['languages']['icon_size'][0] +
                       (num_langs - 1) * self.ui_config['languages']['margin'])
        start_x = (self.card_size[0] - total_width) // 2

        for i in range(num_langs):
            try:
                lang_img_path = os.path.join(self.assets_path['languages'], f"{languages[i]}.png")
                lang_img = Image.open(lang_img_path).convert("RGBA").resize(self.ui_config['languages']['icon_size'])
                x = start_x + i * (self.ui_config['languages']['icon_size'][0] + self.ui_config['languages']['margin'])
                position = (x, self.ui_config['languages']['position_y'])
                card.alpha_composite(lang_img, position)
            except FileNotFoundError:
                self.logger.error(f"Language image not found: {languages[i]}")
            except Exception as e:
                self.logger.error(f"Error adding language {languages[i]}: {e}")
        return card

    def _save_card(self, card, name):
        try:
            os.makedirs(self.assets_path['output'], exist_ok=True)
            output_path = os.path.join(self.assets_path['output'], f"{name}.png")
            
            # Sprawdź, czy plik już istnieje
            if os.path.exists(output_path):
                # Znajdź dostępny numer dla nowej nazwy pliku
                index = 1
                while True:
                    new_output_path = os.path.join(self.assets_path['output'], f"{name}_{index}.png")
                    if not os.path.exists(new_output_path):
                        output_path = new_output_path
                        break
                    index += 1
            
            card.save(output_path)
            self.logger.info(f"Saved card: {output_path}")
        except Exception as e:
            self.logger.error(f"Error saving card {name}: {e}")

    def _validate_data(self, data):
        required_fields = [
            'name', 'background', 'image', 'health',
            'weapon_1_image', 'weapon_1',
            'armor_1_image', 'armor_1',
            'evade'
        ]

        for field in required_fields:
            if pd.isna(data.get(field)):
                raise ValueError(f"Missing required field: {field}")

        if not isinstance(data['health'], (int, float)):
            raise ValueError("Health value must be a number")
            
        if not isinstance(data['evade'], (int, float)):
            raise ValueError("Evade value must be a number")

        for i in range(1, 3):
            weapon_value_key = f'weapon_{i}'
            if pd.notna(data.get(weapon_value_key)) and not isinstance(data[weapon_value_key], (int, float)):
                raise ValueError(f"Weapon {i} value must be a number")

        for i in range(1, 4):
            armor_value_key = f'armor_{i}'
            if pd.notna(data.get(armor_value_key)) and not isinstance(data[armor_value_key], (int, float)):
                raise ValueError(f"Armor {i} value must be a number")

if __name__ == "__main__":
    generator = RPGCardGenerator()
    try:
        generator.generate_from_file('characters.csv')
    except Exception as e:
        generator.logger.exception("Unhandled exception during card generation:")