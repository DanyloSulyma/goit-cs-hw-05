import string
import requests
import matplotlib.pyplot as plt
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

def get_text(url: str) -> str:
    """Завантажує текст із заданої URL-адреси."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Помилка при завантаженні тексту: {e}")
        return ""

def remove_punctuation(text: str) -> str:
    """Видаляє знаки пунктуації з тексту."""
    return text.translate(str.maketrans("", "", string.punctuation))

def map_function(word: str) -> tuple:
    """Крок Map: повертає пару (слово, 1)."""
    return word, 1

def shuffle_function(mapped_values: list) -> list:
    """Крок Shuffle: групує всі 1 для кожного слова."""
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()

def reduce_function(key_values: tuple) -> tuple:
    """Крок Reduce: підсумовує кількість входжень слова."""
    key, values = key_values
    return key, sum(values)

def map_reduce(text: str) -> dict:
    """Основний конвеєр MapReduce з багатопотоковістю."""
    # Попередня обробка тексту
    text = remove_punctuation(text).lower()
    words = text.split()

    if not words:
        return {}

    # Крок Map з багатопотоковістю
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    # Крок Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # Крок Reduce з багатопотоковістю
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)

def visualize_top_words(word_freq: dict, top_n: int = 10):
    """Візуалізує топ-слова з найвищою частотою використання."""
    if not word_freq:
        print("Немає даних для візуалізації.")
        return

    # Сортуємо словник за спаданням частоти і беремо топ_n
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
    words, counts = zip(*sorted_words)

    # Побудова графіка
    plt.figure(figsize=(10, 6))
    plt.barh(words, counts, color='teal')
    plt.xlabel('Частота використання')
    plt.ylabel('Слова')
    plt.title(f'Топ {top_n} найчастіше вживаних слів')
    plt.gca().invert_yaxis()  # Щоб найчастіше слово було зверху
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Приклад: текст книги "Аліса в Країні Чудес" англійською (Project Gutenberg)
    target_url = "https://www.gutenberg.org/files/11/11-0.txt"
    
    print(f"Завантаження тексту з {target_url}...")
    text_data = get_text(target_url)
    
    if text_data:
        print("Аналіз частоти слів...")
        word_frequencies = map_reduce(text_data)
        
        print("Побудова графіка...")
        visualize_top_words(word_frequencies, top_n=10)