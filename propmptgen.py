def generuj_opis_i_tagi(nazwa_pomieszczenia, styl_pomieszczenia, klimaty):
    """
    Generuje opis i tagi dla pomieszczenia, wykorzystując informacje o klimacie.
    """

    if styl_pomieszczenia not in klimaty:
        return "Nieznany styl pomieszczenia.", ""

    klimat = klimaty[styl_pomieszczenia]

    # Prompt do wygenerowania opisu (po polsku, wierszem)
    prompt_opis = f"Napisz wierszowany opis pomieszczenia o nazwie '{nazwa_pomieszczenia}' w stylu {styl_pomieszczenia}. \
    Użyj następujących elementów: {', '.join(klimat['elementy_architektoniczne'])}. \
    Opisz oświetlenie, używając: {', '.join(klimat['oświetlenie'])}. \
    Wykorzystaj materiały takie jak: {', '.join(klimat['materiały'])}. \
    Opis powinien mieć około 4-6 wersów."

    # Prompt do wygenerowania tagów (po angielsku)
    prompt_tagi = f"Wygeneruj listę tagów (oddzielonych przecinkami) opisujących pomieszczenie o nazwie '{nazwa_pomieszczenia}' w stylu {styl_pomieszczenia}. \
    Użyj następujących słów kluczowych: {klimat['opis_ogolny']}. \
          Uwzględnij też te słowa:{', '.join(klimat['elementy_architektoniczne'])}."

    # Połączenie z LM Studio i generowanie opisu
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
    completion_opis = client.chat.completions.create(
        model="model-identifier",
        messages=[
            {"role": "system", "content": "Jesteś kreatywnym poetą, który pisze wiersze o pomieszczeniach."},
            {"role": "user", "content": prompt_opis}
        ],
        temperature=0.7,
        max_tokens=200  # Dostosuj
    )
    opis = completion_opis.choices[0].message.content

    # Połączenie z LM Studio i generowanie tagów
    completion_tagi = client.chat.completions.create(
        model="model-identifier",
        messages=[
            {"role": "system", "content": "Jesteś ekspertem od tagowania obrazów. Generuj tylko tagi oddzielone przecinkami, bez dodatkowych zdań."},
            {"role": "user", "content": prompt_tagi}
        ],
        temperature=0.5,
        max_tokens=100  # Dostosuj
    )
    tagi = completion_tagi.choices[0].message.content

    return opis, tagi