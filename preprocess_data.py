import json
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Preprocessing utilities
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    """
    Preprocess text for Elasticsearch:
    - Remove special characters.
    - Convert to lowercase.
    - Remove stop words.
    - Lemmatize words.
    """
    text = text.lower()  # Convert to lowercase
    text = re.sub(r"[^\w\s]", "", text)  # Remove special characters
    words = text.split()
    filtered_words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return " ".join(filtered_words)

def preprocess_data(input_file, output_file):
    """
    Preprocess cleaned data for Elasticsearch:
    - Clean and preprocess `content` and `title`.
    - Add an `autocomplete` field for `title`.
    """
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    processed_data = []
    for entry in data:
        content = preprocess_text(entry.get("content", ""))
        title = entry.get("title", "")
        meta_description = entry.get("meta_description", "")

        # Generate autocomplete field for the title
        autocomplete = re.sub(r"[^\w\s]", "", title.lower()).split()

        processed_data.append({
            "url": entry.get("url"),
            "content": content,
            "title": title,
            "meta_description": meta_description,
            "autocomplete": autocomplete  # Tokenized title for auto-suggest
        })

    # Save processed data
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(processed_data, file, indent=4)
    print(f"Processed data saved to {output_file}.")

if __name__ == "__main__":
    input_file = "filtered_cleaned_data.json"
    output_file = "processed_data.json"
    preprocess_data(input_file, output_file)
