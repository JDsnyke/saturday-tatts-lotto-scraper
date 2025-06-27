#!/bin/bash

# Color definitions
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
BOLD="\033[1m"
RESET="\033[0m"

# CSV files
WINNING_NUMBERS_FILE="winning_numbers.csv"
SUPP_NUMBERS_FILE="supplementary_numbers.csv"
STATS_FILE="assets/lotto_stats.json"

# Create assets directory if it doesn't exist
mkdir -p assets

echo -e "${BLUE}📊 Generating lotto statistics...${RESET}"

# Check if CSV files exist
if [ ! -f "$WINNING_NUMBERS_FILE" ] || [ ! -f "$SUPP_NUMBERS_FILE" ]; then
    echo -e "${RED}Error: CSV files not found. Please run the scraper first.${RESET}"
    exit 1
fi

# Get total number of draws
TOTAL_DRAWS=$(tail -n +2 "$WINNING_NUMBERS_FILE" | wc -l)
echo -e "${GREEN}Total draws found: $TOTAL_DRAWS${RESET}"

# Get date range
FIRST_DATE=$(tail -n +2 "$WINNING_NUMBERS_FILE" | tail -1 | cut -d',' -f1)
LAST_DATE=$(head -2 "$WINNING_NUMBERS_FILE" | tail -1 | cut -d',' -f1)
echo -e "${GREEN}Date range: $FIRST_DATE to $LAST_DATE${RESET}"

# Calculate years spanned (simplified calculation)
FIRST_YEAR=$(echo "$FIRST_DATE" | cut -d'-' -f1)
LAST_YEAR=$(echo "$LAST_DATE" | cut -d'-' -f1)
YEARS_SPANNED=$((LAST_YEAR - FIRST_YEAR + 1))

# Initialize frequency arrays for numbers 1-45
declare -a WINNING_FREQ
declare -a SUPP_FREQ
for i in {1..45}; do
    WINNING_FREQ[$i]=0
    SUPP_FREQ[$i]=0
done

# Count frequencies for winning numbers
echo -e "${BLUE}Analyzing winning numbers...${RESET}"
while IFS=',' read -r date numbers; do
    if [ "$date" != "Date" ]; then  # Skip header
        IFS=',' read -r -a num_array <<< "$numbers"
        for num in "${num_array[@]}"; do
            if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -le 45 ]; then
                ((WINNING_FREQ[num]++))
            fi
        done
    fi
done < "$WINNING_NUMBERS_FILE"

# Count frequencies for supplementary numbers
echo -e "${BLUE}Analyzing supplementary numbers...${RESET}"
while IFS=',' read -r date numbers; do
    if [ "$date" != "Date" ]; then  # Skip header
        IFS=',' read -r -a num_array <<< "$numbers"
        for num in "${num_array[@]}"; do
            if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -le 45 ]; then
                ((SUPP_FREQ[num]++))
            fi
        done
    fi
done < "$SUPP_NUMBERS_FILE"

# Find most and least frequent numbers
MOST_FREQ_WINNING=1
LEAST_FREQ_WINNING=1
MOST_FREQ_SUPP=1
LEAST_FREQ_SUPP=1

for i in {2..45}; do
    if [ "${WINNING_FREQ[$i]}" -gt "${WINNING_FREQ[$MOST_FREQ_WINNING]}" ]; then
        MOST_FREQ_WINNING=$i
    fi
    if [ "${WINNING_FREQ[$i]}" -lt "${WINNING_FREQ[$LEAST_FREQ_WINNING]}" ]; then
        LEAST_FREQ_WINNING=$i
    fi
    if [ "${SUPP_FREQ[$i]}" -gt "${SUPP_FREQ[$MOST_FREQ_SUPP]}" ]; then
        MOST_FREQ_SUPP=$i
    fi
    if [ "${SUPP_FREQ[$i]}" -lt "${SUPP_FREQ[$LEAST_FREQ_SUPP]}" ]; then
        LEAST_FREQ_SUPP=$i
    fi
done

# Find numbers that have never appeared
NEVER_WINNING=""
NEVER_SUPP=""
for i in {1..45}; do
    if [ "${WINNING_FREQ[$i]}" -eq 0 ]; then
        NEVER_WINNING="$NEVER_WINNING $i"
    fi
    if [ "${SUPP_FREQ[$i]}" -eq 0 ]; then
        NEVER_SUPP="$NEVER_SUPP $i"
    fi
done

# Create frequency arrays for JSON
WINNING_FREQ_JSON=""
SUPP_FREQ_JSON=""
for i in {1..45}; do
    if [ $i -eq 1 ]; then
        WINNING_FREQ_JSON="${WINNING_FREQ[$i]}"
        SUPP_FREQ_JSON="${SUPP_FREQ[$i]}"
    else
        WINNING_FREQ_JSON="$WINNING_FREQ_JSON,${WINNING_FREQ[$i]}"
        SUPP_FREQ_JSON="$SUPP_FREQ_JSON,${SUPP_FREQ[$i]}"
    fi
done

# Generate JSON statistics
cat > "$STATS_FILE" << EOF
{
  "lastUpdated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "summary": {
    "totalDraws": $TOTAL_DRAWS,
    "dateRange": {
      "first": "$FIRST_DATE",
      "last": "$LAST_DATE",
      "yearsSpanned": $YEARS_SPANNED
    },
    "dataPoints": {
      "winningNumbers": $(($TOTAL_DRAWS * 6)),
      "supplementaryNumbers": $(($TOTAL_DRAWS * 2))
    }
  },
  "frequencies": {
    "mostFrequent": {
      "winning": {
        "number": $MOST_FREQ_WINNING,
        "count": ${WINNING_FREQ[$MOST_FREQ_WINNING]}
      },
      "supplementary": {
        "number": $MOST_FREQ_SUPP,
        "count": ${SUPP_FREQ[$MOST_FREQ_SUPP]}
      }
    },
    "leastFrequent": {
      "winning": {
        "number": $LEAST_FREQ_WINNING,
        "count": ${WINNING_FREQ[$LEAST_FREQ_WINNING]}
      },
      "supplementary": {
        "number": $LEAST_FREQ_SUPP,
        "count": ${SUPP_FREQ[$LEAST_FREQ_SUPP]}
      }
    }
  },
  "neverAppeared": {
    "winning": [${NEVER_WINNING// /,}],
    "supplementary": [${NEVER_SUPP// /,}]
  },
  "allFrequencies": {
    "winning": [$WINNING_FREQ_JSON],
    "supplementary": [$SUPP_FREQ_JSON]
  }
}
EOF

echo -e "${GREEN}✅ Statistics generated successfully!${RESET}"
echo -e "${BLUE}📊 Key Statistics:${RESET}"
echo -e "  - Total draws: ${GREEN}$TOTAL_DRAWS${RESET}"
echo -e "  - Date range: ${GREEN}$FIRST_DATE to $LAST_DATE${RESET}"
echo -e "  - Years spanned: ${GREEN}$YEARS_SPANNED${RESET}"
echo -e "  - Most frequent winning number: ${GREEN}$MOST_FREQ_WINNING${RESET} (${WINNING_FREQ[$MOST_FREQ_WINNING]} times)"
echo -e "  - Least frequent winning number: ${GREEN}$LEAST_FREQ_WINNING${RESET} (${WINNING_FREQ[$LEAST_FREQ_WINNING]} times)"
echo -e "  - Numbers never appeared (winning): ${YELLOW}${NEVER_WINNING:-None}${RESET}"
echo -e "  - Numbers never appeared (supp): ${YELLOW}${NEVER_SUPP:-None}${RESET}"
echo -e "${BLUE}💾 Statistics saved to: $STATS_FILE${RESET}"

exit 0 