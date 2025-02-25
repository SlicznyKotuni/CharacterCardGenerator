import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import logging

class RPGCardGenerator:
    def __init__(self):
        self.card_size = (912, 1368)  # Corrected: width, height
        self.character_size = (800, 700) # Adjusted Character Size
        
        self.ui_config = {
            'weapons': {
                'positions': [(50, 350), (50, 450)],  # Adjusted positions, touching
                'size': (100, 100),
                'label_offset': (50, 50)  # Center text within the square
            },
            'armors': {
                'positions': [(762, 350), (762, 480), (762, 610)],  # Adjusted positions
                'size': (100, 100),
                'label_offset': (50, 50)  # Center text within the square
            },
            'health': {
                'position': (762, 50),  # Adjusted Position
                'size': (100, 100),
                'font_size': 32
            },
            'name_plate': {
                'size': (600, 100),
                'position': ((912 - 600) // 2, 1200)  # Centered horizontally, adjusted Y
            },
            'name': {
                'position': (912 // 2, 1240),  # Centered horizontally, adjusted Y
                'font_size': 60,
                'max_length': 24
            },
            'languages': {
                'icon_size': (80, 80),
                'max_count': 4,
                'margin': 30,
                'position_y': 1300 # Adjusted Y
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

        self._setup_logging()  # Initialize logger
        self.font = self._load_font()

    def _load_font(self):
        """Loads the font, handling potential errors."""
        font_path = os.path.join(self.assets_path['fonts'], 'PressJobs.ttf')
        try:
            return ImageFont.truetype(font_path, size=24)
        except IOError as e:
            self.logger.error(f"Failed to load font from {font_path}: {e}")
            # Fallback to a default font if available, or re-raise
            try:
                return ImageFont.load_default()
            except IOError:
                self.logger.error("Failed to load default font.")
                raise  # Re-raise the exception if no font available

    def generate_from_file(self, csv_path):
        """Generates character cards from a CSV file."""
        try:
            df = pd.read_csv(csv_path, sep=';')
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

    def _create_card(self,  data):
        """Creates the character card image."""
        try:
            background_path = os.path.join(self.assets_path['backgrounds'], f"{data['background']}.png")
            card = Image.open(background_path).convert('RGBA')
        except FileNotFoundError:
            self.logger.error(f"Background image not found: {data['background']}")
            return None # or raise exception
        except Exception as e:
             self.logger.error(f"Error opening background image: {data['background']}")
             return None

        card = self._add_character(card, data['image'])
        card = self._add_combat_elements(card, data)
        card = self._add_name_plate(card, data)
        card = self._add_languages(card, data)
        
        return card

    def _add_character(self, card, character_img):
        """Adds the character image to the card."""
        try:
            character_path = os.path.join(self.assets_path['characters'], f"{character_img}.png")
            character = Image.open(character_path).convert('RGBA')
        except FileNotFoundError:
            self.logger.error(f"Character image not found: {character_img}")
            return card
        except Exception as e:
            self.logger.error(f"Error opening character image: {character_img}: {e}")
            return card

        # Adjust vertical position to move the character up and give more space at the bottom
        character_pos = (
            (self.card_size[0] - self.character_size[0]) // 2,
            20 # Adjusted value, smaller = higher
        )
        card.alpha_composite(character, character_pos)
        return card

    def _add_combat_elements(self, card, data):
        """Adds weapons, armor, and health to the card."""
        card = self._add_weapons(card, data)
        card = self._add_armors(card, data)
        card = self._add_health(card, data)
        return card

    def _add_weapons(self, card, data):
        """Adds weapon images and values to the card."""
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
        """Adds armor images and values to the card."""
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
    
    def _add_health(self, card, data):
        """Adds the health icon and value to the card."""
        try:
            health_icon_path = os.path.join(self.assets_path['ui'], 'health_icon.png')
            health_icon = Image.open(health_icon_path).convert("RGBA")
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
        except FileNotFoundError:
            self.logger.error("Health icon not found.")
        except Exception as e:
            self.logger.error(f"Error adding health: {e}")
        return card

    def _add_weapon(self, card, img_name, value, position):
        """Adds a weapon image and its value to the card."""
        try:
            weapon_path = os.path.join(self.assets_path['weapons'], f"{img_name}.png")
            weapon_img = Image.open(weapon_path).convert("RGBA") # Ensure RGBA
            weapon_img = weapon_img.resize(self.ui_config['weapons']['size'])

            draw = ImageDraw.Draw(weapon_img)
            text_position = (
                self.ui_config['weapons']['label_offset'][0],
                self.ui_config['weapons']['label_offset'][1]
            )

            # Load a bold font (or use the existing one if a bold version isn't available)
            bold_font_path = os.path.join(self.assets_path['fonts'], 'PressJobs-Bold.ttf')  # Example
            try:
                bold_font = ImageFont.truetype(bold_font_path, size=24)  # Same size as before
            except IOError:
                self.logger.warning("Bold font not found, using regular font.")
                bold_font = self.font  # Use the regular font as a fallback

            draw.text(
                text_position,
                str(value),
                font=bold_font,
                fill='white',
                anchor='mm'  # Center the text
            )

            card.alpha_composite(weapon_img, position)
        except FileNotFoundError:
            self.logger.error(f"Weapon image not found: {img_name}")
        except Exception as e:
            self.logger.error(f"Error adding weapon {img_name}: {e}")
        return card

    def _add_armor(self, card, img_name, value, position):
        """Adds an armor image and its value to the card."""
        try:
            armor_path = os.path.join(self.assets_path['armors'], f"{img_name}.png")
            armor_img = Image.open(armor_path).convert("RGBA") # Ensure RGBA
            armor_img = armor_img.resize(self.ui_config['armors']['size'])

            draw = ImageDraw.Draw(armor_img)
            text_position = self.ui_config['armors']['label_offset']

            # Load a bold font (or use the existing one if a bold version isn't available)
            bold_font_path = os.path.join(self.assets_path['fonts'], 'PressJobs-Bold.ttf')  # Example
            try:
                bold_font = ImageFont.truetype(bold_font_path, size=24)  # Same size as before
            except IOError:
                self.logger.warning("Bold font not found, using regular font.")
                bold_font = self.font  # Use the regular font as a fallback

            draw.text(
                text_position,
                str(value),
                font=bold_font,
                fill='white',
                anchor='mm'  # Center the text
            )

            card.alpha_composite(armor_img, position)
        except FileNotFoundError:
            self.logger.error(f"Armor image not found: {img_name}")
        except Exception as e:
            self.logger.error(f"Error adding armor {img_name}: {e}")
        return card

    def _add_name_plate(self, card, data):
        """Adds the name plate and character's name to the card."""
        try:
            plate_path = os.path.join(self.assets_path['ui'], 'name_plate.png')
            plate = Image.open(plate_path).convert("RGBA")  # Ensure RGBA
            plate = plate.resize(self.ui_config['name_plate']['size'])
            card.alpha_composite(plate, self.ui_config['name_plate']['position'])

            draw = ImageDraw.Draw(card)
            text = data['name']
            font = self.font.font_variant(size=self.ui_config['name']['font_size'])
            text_width, text_height = draw.textsize(text, font=font) # Removed deprecated call

            # Stroke effect (crude, but functional)
            stroke_color = 'black'  # Or another suitable color
            x, y = self.ui_config['name']['position']
            offset = 2  # Stroke width

            # Draw the text multiple times with an offset to create the stroke effect
            for i in range(-offset, offset + 1):
                for j in range(-offset, offset + 1):
                    draw.text((x + i, y + j), text, font=font, fill=stroke_color, anchor='mm')

            # Draw the main text in white
            draw.text(self.ui_config['name']['position'], text, font=font, fill='white', anchor='mm')

        except FileNotFoundError:
            self.logger.error("Name plate image not found.")
        except Exception as e:
            self.logger.error(f"Error adding name plate: {e}")
        return card

    def _add_languages(self, card, data):
        """Adds language icons to the card."""
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
        """Saves the generated card to the output folder."""
        try:
            os.makedirs(self.assets_path['output'], exist_ok=True)
            output_path = os.path.join(self.assets_path['output'], f"{name}.png")
            card.save(output_path)
            self.logger.info(f"Saved card: {output_path}")
        except Exception as e:
            self.logger.error(f"Error saving card {name}: {e}")

    def _validate_data(self, data):
        """Validates the input data."""
        required_fields = [
            'name', 'background', 'image', 'health',
            'weapon_1_image', 'weapon_1',
            'armor_1_image', 'armor_1'
        ]
        
        for field in required_fields:
            if pd.isna(data.get(field)):  # Use .get() to avoid KeyError
                raise ValueError(f"Missing required field: {field}")
                
        if not isinstance(data['health'], (int, float)):
            raise ValueError("Health value must be a number")
            
        for i in range(1, 3):
            weapon_value_key = f'weapon_{i}'
            if pd.notna(data.get(weapon_value_key)) and not isinstance(data[weapon_value_key], (int, float)):
                raise ValueError(f"Weapon {i} value must be a number")
                
        for i in range(1, 4):
            armor_value_key = f'armor_{i}'
            if pd.notna(data.get(armor_value_key)) and not isinstance(data[armor_value_key], (int, float)):
                raise ValueError(f"Armor {i} value must be a number")

    def _setup_logging(self):
        """Configures the logging system."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('card_generator.log', encoding='utf-8'),  # Added encoding
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)


if __name__ == "__main__":
    generator = RPGCardGenerator()

    # Example CSV (semicolon-separated):
    # name;background;image;health;weapon_1_image;weapon_1;weapon_2_image;weapon_2;armor_1_image;armor_1;armor_2_image;armor_2;armor_3_image;armor_3;language_1;language_2;language_3;language_4;language_5
    # Gromthar;dungeon;warrior;150;sword_icon;12;axe_icon;8;plate_icon;15;helm_icon;5;boots_icon;3;Drakonii;Urghish;Eldritch;Shadowtongue;
    
    try:
        generator.generate_from_file('list.csv')
    except Exception as e:
        generator.logger.exception("Unhandled exception during card generation:")