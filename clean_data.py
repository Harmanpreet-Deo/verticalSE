import json
import os
import html

def sanitize_content(content):
    """
    Cleans and normalizes the content field by:
    - Stripping leading/trailing whitespace.
    - Decoding HTML entities.
    - Removing excessive spaces.
    """
    if not content:
        return None

    # Decode HTML entities
    content = html.unescape(content)

    # Normalize spaces
    content = " ".join(content.split())

    return content if content.strip() else None

def clean_and_filter_json_files(file_names, input_dir, output_file):
    """
    Cleans and filters JSON files, removing problematic entries and keeping only valid data.
    
    Args:
        file_names (list): List of JSON filenames to clean and merge.
        input_dir (str): Directory containing raw JSON files.
        output_file (str): Path to the output JSON file for cleaned data.
    """
    consolidated_data = []

    for file_name in file_names:
        try:
            file_path = os.path.join(input_dir, file_name)
            
            # Load the JSON file
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Filter and sanitize entries
            cleaned_data = []
            for entry in data:
                # Sanitize content
                content = sanitize_content(entry.get("content"))
                if not content:
                    continue  # Skip entries with invalid or empty content

                # Ensure meta_description is non-empty
                meta_description = entry.get("meta_description")
                if not meta_description or not meta_description.strip():
                    continue  # Skip if meta_description is missing or empty

                # Update entry and add to cleaned data
                cleaned_entry = {
                    "url": entry.get("url"),
                    "title": entry.get("title"),
                    "meta_description": meta_description.strip(),
                    "content": content,
                }
                cleaned_data.append(cleaned_entry)

            consolidated_data.extend(cleaned_data)

            print(f"Processed {file_name}. Valid records added: {len(cleaned_data)}")

        except Exception as e:
            print(f"Error processing {file_name}: {e}")

    # Save the cleaned and filtered data to a single file
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(consolidated_data, file, indent=4, ensure_ascii=False)
        print(f"Cleaned data saved to {output_file}. Total valid records: {len(consolidated_data)}")
    except Exception as e:
        print(f"Error saving to {output_file}: {e}")


# List of JSON files to clean and merge
file_names = [
    "unep_data.json", "climategov_data.json", 
    "epa_data.json", "nasa_data.json", 
    "eea_data.json", "ipcc_data.json"
]

# Input directory containing raw JSON files
input_dir = "./raw_data"

# Output file for cleaned and filtered data
output_file = "filtered_cleaned_data.json"

# Call the function to clean and filter data
clean_and_filter_json_files(file_names, input_dir, output_file)
