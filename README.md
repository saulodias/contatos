# VCF Contact Formatter for SIM Cards

Convert Google Contacts VCF files into SIM card-compatible individual VCF files. This script handles special characters, emojis, and formats names/numbers to be compatible with most SIM cards.

## Prerequisites

- Python 3.x
- Google Contacts export file

## How to Export Contacts from Google

1. Go to [Google Contacts](https://contacts.google.com/)
2. Select the contacts you want to export
3. Click "Export"
4. Choose "vCard for Android or iOS" format
5. Save the file as `contacts.vcf`

## Usage

1. Place `contacts.vcf` in the same directory as the script
2. Run the script:
   ```bash
   python main.py
   ```
3. Find your formatted contacts in the `formatted_contacts` folder

## Features

- Removes accents and special characters
- Removes emojis and other symbols
- Truncates names to 15 characters (SIM card limit)
- Cleans phone numbers (keeps only numbers and + symbol)
- Handles duplicate names by adding numbers (e.g., "John Smith 1", "John Smith 2")
- Creates individual VCF files for easier SIM import

## Output Format

Each contact will be saved as an individual VCF file: 