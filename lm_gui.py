import tkinter as tk
from tkinter import scrolledtext, font
from openai import OpenAI

class LMStudioGUI:
    def __init__(self, master):
        self.master = master
        master.title("LM Studio Tester")

        # Konfiguracja kolorów
        self.bg_color = "#333333"  # Grafitowy
        self.text_color = "#FFFFFF"  # Biały
        self.button_color = "#555555" # Ciemniejszy grafit

        # Ustawienia czcionki
        self.font = font.Font(family="Helvetica", size=12)

        # Konfiguracja okna
        master.configure(bg=self.bg_color)

        self.client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

        # Label i pole tekstowe na prompt
        self.label = tk.Label(master, text="Wpisz zapytanie:", bg=self.bg_color, fg=self.text_color, font=self.font)
        self.label.pack(pady=5)

        self.prompt_entry = scrolledtext.ScrolledText(master, height=5, width=50, bg=self.bg_color, fg=self.text_color, insertbackground=self.text_color, font=self.font)
        self.prompt_entry.pack(padx=10, pady=5)

        # Przycisk Wyślij
        self.send_button = tk.Button(master, text="Wyślij", command=self.send_prompt, bg=self.button_color, fg=self.text_color, font=self.font, relief=tk.FLAT, padx=10, pady=5)
        self.send_button.pack(pady=5)

        # Label i pole tekstowe na odpowiedź
        self.response_label = tk.Label(master, text="Odpowiedź:", bg=self.bg_color, fg=self.text_color, font=self.font)
        self.response_label.pack(pady=5)

        self.response_text = scrolledtext.ScrolledText(master, height=10, width=50, bg=self.bg_color, fg=self.text_color, state=tk.DISABLED, font=self.font)
        self.response_text.pack(padx=10, pady=5)

        # Oczekiwana długość odpowiedzi
        self.length_label = tk.Label(master, text="Oczekiwana długość odpowiedzi (w tokenach):", bg=self.bg_color, fg=self.text_color, font=self.font)
        self.length_label.pack(pady=5)

        self.length_entry = tk.Entry(master, bg=self.bg_color, fg=self.text_color, insertbackground=self.text_color, font=self.font)
        self.length_entry.insert(0, "150")  # Domyślna długość
        self.length_entry.pack(pady=5)

    def send_prompt(self):
        prompt = self.prompt_entry.get("1.0", tk.END).strip()
        max_tokens = int(self.length_entry.get())

        try:
            completion = self.client.chat.completions.create(
                model="model-identifier",
                messages=[
                    {"role": "system", "content": "Jesteś pomocnym asystentem, który odpowiada zwięźle."},
                    {"role": "user", "content": prompt + f"\nOdpowiedz w maksymalnie {max_tokens} tokenach."}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            response = completion.choices[0].message.content
            self.response_text.configure(state=tk.NORMAL)  # Odblokuj pole tekstowe
            self.response_text.delete("1.0", tk.END)
            self.response_text.insert("1.0", response)
            self.response_text.configure(state=tk.DISABLED)  # Zablokuj pole tekstowe

        except Exception as e:
            self.response_text.configure(state=tk.NORMAL)  # Odblokuj pole tekstowe
            self.response_text.delete("1.0", tk.END)
            self.response_text.insert("1.0", f"Błąd: {e}")
            self.response_text.configure(state=tk.DISABLED)  # Zablokuj pole tekstowe

root = tk.Tk()
gui = LMStudioGUI(root)
root.mainloop()