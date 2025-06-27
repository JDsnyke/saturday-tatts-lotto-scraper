#!/bin/bash

# Color definitions
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
BOLD="\033[1m"
RESET="\033[0m"

# Spinner function
spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\\'
    while kill -0 $pid 2>/dev/null; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        spinstr=$temp${spinstr%$temp}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# Error handling function
handle_error() {
    echo -e "${RED}Error: $1${RESET}" >&2
    exit 1
}

# Define the range of years
START_YEAR=1986
END_YEAR=2025

# Base URL for the results archive
BASE_URL="https://au.lottonumbers.com/saturday-lotto/results"

# Output CSV files
WINNING_NUMBERS_FILE="winning_numbers.csv"
SUPP_NUMBERS_FILE="supplementary_numbers.csv"

# Initialize CSV files with headers if they don't exist
if [ ! -f "$WINNING_NUMBERS_FILE" ]; then
    echo "Date,Winning Numbers" > "$WINNING_NUMBERS_FILE"
fi
if [ ! -f "$SUPP_NUMBERS_FILE" ]; then
    echo "Date,Supplementary Numbers" > "$SUPP_NUMBERS_FILE"
fi

# Function to check if date already exists in CSV
date_exists() {
    local date="$1"
    local file="$2"
    grep -q "^$date," "$file"
}

# Track processing statistics
TOTAL_PROCESSED=0
TOTAL_SKIPPED=0
TOTAL_ERRORS=0
SKIP_COUNT=0
SKIP_LIMIT=5

echo -e "${BLUE}${BOLD}🕷️  Starting Saturday Tatts Lotto scraper...${RESET}" >&2
echo -e "${BLUE}📊 Fetching data from au.lottonumbers.com${RESET}" >&2

for YEAR in $(seq $END_YEAR -1 $START_YEAR); do
    echo -e "${BLUE}Processing year: $YEAR${RESET}" >&2
    ARCHIVE_URL="${BASE_URL}/${YEAR}-archive"

    # Fetch the archive page
    HTML_CONTENT=$(curl -s "$ARCHIVE_URL")
    
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Warning: Could not fetch archive for year $YEAR, skipping...${RESET}" >&2
        continue
    fi

    # Extract links to individual draw pages (excluding archive links)
    DRAW_LINKS=$(echo "$HTML_CONTENT" | pup 'a[href*="/saturday-lotto/results/"] attr{href}' | grep '^/saturday-lotto/results/[0-9]' | grep -v archive | sed 's|^|https://au.lottonumbers.com|')

    # Loop through each draw link
    while IFS= read -r DRAW_URL; do
        if [ -z "$DRAW_URL" ]; then
            continue
        fi

        echo -e "${BLUE}Fetching draw: $DRAW_URL${RESET}" >&2
        
        # Fetch the draw page
        DRAW_HTML=$(curl -s "$DRAW_URL")
        
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}Warning: Could not fetch draw page, skipping...${RESET}" >&2
            ((TOTAL_ERRORS++))
            continue
        fi

        # Extract the draw date from the title
        DRAW_DATE=$(echo "$DRAW_HTML" | pup 'title text{}' | grep -o "[0-9]\+ [A-Za-z]\+ [0-9]\{4\}")

        # Convert date to YYYY-MM-DD format
        if [ -n "$DRAW_DATE" ]; then
            FORMATTED_DATE=$(date -d "$DRAW_DATE" +"%Y-%m-%d" 2>/dev/null)
            if [ -z "$FORMATTED_DATE" ]; then
                FORMATTED_DATE=$(date -j -f "%d %b %Y" "$DRAW_DATE" +"%Y-%m-%d" 2>/dev/null)
                if [ -z "$FORMATTED_DATE" ]; then
                    echo -e "${YELLOW}Warning: Invalid date format: $DRAW_DATE, skipping...${RESET}" >&2
                    ((TOTAL_ERRORS++))
                    continue
                fi
            fi
        else
            echo -e "${YELLOW}Warning: Could not extract date from: $DRAW_URL, skipping...${RESET}" >&2
            ((TOTAL_ERRORS++))
            continue
        fi

        if date_exists "$FORMATTED_DATE" "$WINNING_NUMBERS_FILE" && date_exists "$FORMATTED_DATE" "$SUPP_NUMBERS_FILE"; then
            echo -e "${YELLOW}Skipping $FORMATTED_DATE - already exists in CSV files${RESET}" >&2
            ((TOTAL_SKIPPED++))
            ((SKIP_COUNT++))
            if [ $SKIP_COUNT -ge $SKIP_LIMIT ]; then
                echo -e "${YELLOW}Reached $SKIP_LIMIT consecutive skips. Terminating early.${RESET}" >&2
                echo -e "${BLUE}💾 Results saved to:${RESET}" >&2
                echo -e "  - $WINNING_NUMBERS_FILE" >&2
                echo -e "  - $SUPP_NUMBERS_FILE" >&2
                exit 0
            fi
            continue
        fi

        ALL_NUMBERS=$(echo "$DRAW_HTML" | pup 'li.ball text{}' | paste -sd "," -)
        IFS=',' read -r -a NUMBERS_ARRAY <<< "$ALL_NUMBERS"

        if [ "${#NUMBERS_ARRAY[@]}" -lt 8 ]; then
            echo -e "${YELLOW}Warning: Insufficient numbers found for $FORMATTED_DATE (found ${#NUMBERS_ARRAY[@]} numbers), skipping...${RESET}" >&2
            ((TOTAL_ERRORS++))
            continue
        fi

        WINNING_NUMBERS=$(IFS=','; echo "${NUMBERS_ARRAY[*]:0:6}")
        SUPP_NUMBERS=$(IFS=','; echo "${NUMBERS_ARRAY[*]:6:2}")

        echo "$FORMATTED_DATE,$WINNING_NUMBERS" >> "$WINNING_NUMBERS_FILE"
        echo "$FORMATTED_DATE,$SUPP_NUMBERS" >> "$SUPP_NUMBERS_FILE"

        echo -e "${GREEN}Processed: $FORMATTED_DATE - Winning: $WINNING_NUMBERS, Supp: $SUPP_NUMBERS${RESET}" >&2
        ((TOTAL_PROCESSED++))
        SKIP_COUNT=0
        
        # Small delay to be respectful to the server
        sleep 0.2
    done <<< "$DRAW_LINKS"
done

echo -e "${GREEN}✅ Scraping completed successfully!${RESET}" >&2
echo -e "${BLUE}📊 Processing Summary:${RESET}" >&2
echo -e "  - Total draws processed: ${GREEN}$TOTAL_PROCESSED${RESET}" >&2
echo -e "  - Total draws skipped: ${YELLOW}$TOTAL_SKIPPED${RESET}" >&2
echo -e "  - Total errors: ${RED}$TOTAL_ERRORS${RESET}" >&2
echo -e "${BLUE}💾 Results saved to:${RESET}" >&2
echo -e "  - $WINNING_NUMBERS_FILE" >&2
echo -e "  - $SUPP_NUMBERS_FILE" >&2

# Return to master script
exit 0
