#!/bin/bash

# Color definitions
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "${BLUE}${BOLD}🧹 Cleaning corrupted CSV files...${RESET}"

# Function to clean a CSV file
clean_csv_file() {
    local file="$1"
    local temp_file="${file}.tmp"
    
    if [ ! -f "$file" ]; then
        echo -e "${YELLOW}Warning: $file does not exist${RESET}"
        return
    fi
    
    echo -e "${BLUE}Cleaning $file...${RESET}"
    
    # Remove lines that start with "Processed:" and keep only valid data lines
    # Valid lines should match date format YYYY-MM-DD followed by comma and numbers
    grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2},[0-9,]+$' "$file" > "$temp_file"
    
    # Count lines before and after
    local original_lines=$(wc -l < "$file")
    local cleaned_lines=$(wc -l < "$temp_file")
    local removed_lines=$((original_lines - cleaned_lines))
    
    # Replace original file with cleaned version
    mv "$temp_file" "$file"
    
    echo -e "${GREEN}✓ Cleaned $file:${RESET}"
    echo -e "  - Original lines: $original_lines"
    echo -e "  - Cleaned lines: $cleaned_lines"
    echo -e "  - Removed corrupted lines: $removed_lines"
}

# Clean both CSV files
clean_csv_file "winning_numbers.csv"
clean_csv_file "supplementary_numbers.csv"

echo -e "${GREEN}✅ CSV cleaning completed!${RESET}" 