import os
import re

def remove_emojis(text):
    # Remove emojis and other special characters
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text)

def remove_accents(text):
    # First remove any emojis
    text = remove_emojis(text)
    
    replacements = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ý': 'y', 'ÿ': 'y',
        'ñ': 'n',
        'ç': 'c',
        # Uppercase versions
        'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A', 'Ä': 'A',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
        'Ó': 'O', 'Ò': 'O', 'Õ': 'O', 'Ô': 'O', 'Ö': 'O',
        'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'Ý': 'Y',
        'Ñ': 'N',
        'Ç': 'C',
    }
    for accented, normal in replacements.items():
        text = text.replace(accented, normal)
    return text

def clean_name(name):
    # Remove emojis first
    name = remove_emojis(name)
    # Remove all special characters including parentheses, brackets, etc.
    name = re.sub(r'[^\w\s-]', '', name)  # Keep only letters, numbers, spaces and hyphens
    # Remove multiple spaces
    name = re.sub(r'\s+', ' ', name)
    return name.strip()

def sanitize_filename(name):
    # Clean the name first
    name = clean_name(name)
    # Truncate name if too long (GSM limit)
    name = name[:15]  # Truncate to 15 chars max
    return name.strip()

def clean_phone_number(phone):
    # Keep only numbers and plus sign
    phone = ''.join(c for c in phone if c.isdigit() or c == '+')
    return phone

def parse_vcf(input_file, output_folder):
    # Try UTF-8 first, fallback to ISO-8859-1 if that fails
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except UnicodeDecodeError:
        with open(input_file, "r", encoding="iso-8859-1") as file:
            lines = file.readlines()
    
    contacts = []
    current_contact = {}
    name_count = {}  # Dictionary to keep track of how many times each name appears
    
    # First pass to collect contacts
    for line in lines:
        line = line.strip()
        if line.startswith("BEGIN:VCARD"):
            current_contact = {"N": "", "TEL": []}
        elif line.startswith("N:"):
            # Parse the name parts and reformat
            name_parts = line[2:].strip().split(';')
            if len(name_parts) >= 2:
                last_name = name_parts[0].strip()
                first_name = name_parts[1].strip()
                name = f"{first_name} {last_name}".strip()
            else:
                name = line[2:].strip()
            
            # Clean and normalize name before storing
            name = clean_name(name)
            name = remove_accents(name)
            current_contact["N"] = name
        elif line.startswith("TEL;"):
            phone = line.split(":")[-1].strip()
            current_contact["TEL"].append(clean_phone_number(phone))
        elif line.startswith("END:VCARD"):
            if current_contact["N"] and current_contact["TEL"]:
                for tel in current_contact["TEL"]:
                    contacts.append({"N": current_contact["N"], "TEL": tel})
    
    # Count occurrences of each name
    for contact in contacts:
        name = contact["N"]
        name_count[name] = name_count.get(name, 0) + 1
    
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Write individual VCF files for each contact
    current_indices = {}  # Keep track of current index for each name
    processed_count = 0
    
    for contact in contacts:
        name = contact["N"]
        # Clean the name first
        name = clean_name(name)
        name = remove_accents(name)
        
        if name_count[name] > 1:
            current_indices[name] = current_indices.get(name, 0) + 1
            display_name = f"{name[:13]} {current_indices[name]}"  # 13 chars + space + number
        else:
            display_name = name[:15]  # Truncate to 15 chars
            
        # Create a safe filename
        filename = sanitize_filename(display_name) + ".vcf"
        output_file = os.path.join(output_folder, filename)
        
        with open(output_file, "w", encoding="utf-8") as file:
            file.write("BEGIN:VCARD\n")
            file.write("VERSION:2.1\n")
            file.write(f"N:{display_name}\n")
            file.write(f"TEL;CELL;VOICE:{contact['TEL']}\n")
            file.write("END:VCARD")
        
        processed_count += 1
    
    print(f"Processed {processed_count} contacts from {os.path.basename(input_file)}")

# Example usage
input_vcf = "contacts.vcf"  # The exported file from Google Contacts
output_folder = "formatted_contacts"  # Output folder for individual VCF files

# Process the contacts.vcf file
parse_vcf(input_vcf, output_folder)
