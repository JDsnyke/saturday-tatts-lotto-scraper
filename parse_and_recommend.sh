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

# Function to clean CSV files automatically
clean_csv_files() {
    local winning_file="$1"
    local supp_file="$2"
    
    echo -e "${BLUE}🧹 Auto-cleaning CSV files before analysis...${RESET}"
    
    # Clean winning numbers file
    if [ -f "$winning_file" ]; then
        local temp_file="${winning_file}.tmp"
        # Remove lines that start with "Processed:" and keep only valid data lines
        grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2},[0-9,]+$' "$winning_file" > "$temp_file"
        local original_lines=$(wc -l < "$winning_file")
        local cleaned_lines=$(wc -l < "$temp_file")
        local removed_lines=$((original_lines - cleaned_lines))
        
        if [ $removed_lines -gt 0 ]; then
            mv "$temp_file" "$winning_file"
            echo -e "${YELLOW}✓ Cleaned $winning_file: removed $removed_lines corrupted lines${RESET}"
        else
            rm -f "$temp_file"
        fi
    fi
    
    # Clean supplementary numbers file
    if [ -f "$supp_file" ]; then
        local temp_file="${supp_file}.tmp"
        # Remove lines that start with "Processed:" and keep only valid data lines
        grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2},[0-9,]+$' "$supp_file" > "$temp_file"
        local original_lines=$(wc -l < "$supp_file")
        local cleaned_lines=$(wc -l < "$temp_file")
        local removed_lines=$((original_lines - cleaned_lines))
        
        if [ $removed_lines -gt 0 ]; then
            mv "$temp_file" "$supp_file"
            echo -e "${YELLOW}✓ Cleaned $supp_file: removed $removed_lines corrupted lines${RESET}"
        else
            rm -f "$temp_file"
        fi
    fi
}

# Parse and Recommend Lotto Entries
# This script analyzes winning_numbers.csv and recommends 10 unique entries

WINNING_FILE="winning_numbers.csv"
SUPP_FILE="supplementary_numbers.csv"

if [ ! -f "$WINNING_FILE" ]; then
    echo -e "${RED}Error: $WINNING_FILE not found. Please run the scraper first.${RESET}"
    exit 1
fi

# Auto-clean CSV files before processing
clean_csv_files "$WINNING_FILE" "$SUPP_FILE"

echo -e "${BLUE}Analyzing past results to recommend 10 unique entries with highest probability numbers...${RESET}"

# Run analysis in background for spinner
(
# Count frequency of each number (1-45) and calculate probabilities
# Using simple arrays instead of associative arrays for compatibility
freq=()
prob=()
odds=()
for i in {1..45}; do
    freq[$i]=0
    prob[$i]=0
    odds[$i]=0
done

total=0

# Count frequencies
total_draws=0
while IFS=',' read -r date n1 n2 n3 n4 n5 n6; do
    if [[ "$date" != "Date" ]]; then
        freq[$n1]=$(( ${freq[$n1]:-0} + 1 ))
        freq[$n2]=$(( ${freq[$n2]:-0} + 1 ))
        freq[$n3]=$(( ${freq[$n3]:-0} + 1 ))
        freq[$n4]=$(( ${freq[$n4]:-0} + 1 ))
        freq[$n5]=$(( ${freq[$n5]:-0} + 1 ))
        freq[$n6]=$(( ${freq[$n6]:-0} + 1 ))
        total=$((total + 6))
        total_draws=$((total_draws + 1))
    fi
done < "$WINNING_FILE"

# Calculate probabilities, odds, and create sorted list by probability
prob_list=""
for n in {1..45}; do
    if [[ ${freq[$n]:-0} -gt 0 ]]; then
        prob[$n]=$(echo "scale=6; ${freq[$n]}/$total" | bc -l 2>/dev/null || echo "0.000000")
        # Calculate odds: 1 in X chance (total draws / frequency)
        odds[$n]=$(echo "scale=0; $total/${freq[$n]}" | bc -l 2>/dev/null || echo "0")
        prob_list+="$n:${prob[$n]}"$'\n'
    else
        prob[$n]="0.000000"
        odds[$n]=0
        prob_list+="$n:0.000000"$'\n'
    fi
done

# Sort by probability (descending) and get top 30 numbers
top_numbers=($(echo "$prob_list" | sort -t: -k2,2nr | head -30 | cut -d: -f1))

# Get all past winning combinations (sorted)
past_combinations=()
while IFS=',' read -r date n1 n2 n3 n4 n5 n6; do
    if [[ "$date" != "Date" ]]; then
        sorted_combo=$(printf "%s\n" "$n1" "$n2" "$n3" "$n4" "$n5" "$n6" | sort -n | tr '\n' ',' | sed 's/,$//')
        past_combinations+=("$sorted_combo")
    fi
done < "$WINNING_FILE"

# Function to check if two combinations share more than 2 numbers
check_similarity() {
    local combo1="$1"
    local combo2="$2"
    local shared=0
    
    IFS=',' read -ra nums1 <<< "$combo1"
    IFS=',' read -ra nums2 <<< "$combo2"
    
    for n1 in "${nums1[@]}"; do
        for n2 in "${nums2[@]}"; do
            if [[ "$n1" == "$n2" ]]; then
                shared=$((shared + 1))
            fi
        done
    done
    
    [[ $shared -le 2 ]]
}

# Function to check if combination exists in past results
is_past_combination() {
    local combo="$1"
    for past in "${past_combinations[@]}"; do
        if [[ "$combo" == "$past" ]]; then
            return 0
        fi
    done
    return 1
}

# Generate unique recommendations
recommendations=()
attempts=0
max_attempts=1000

while [[ ${#recommendations[@]} -lt 10 && $attempts -lt $max_attempts ]]; do
    attempts=$((attempts + 1))
    
    # Create a new combination using weighted selection from top numbers
    new_combo=()
    used_indices=()
    
    # Select 6 unique numbers from top 30, weighted by probability
    for i in {1..6}; do
        while true; do
            # Weighted random selection from top 30
            rand=$((RANDOM % 100))
            if [[ $rand -lt 40 ]]; then
                # 40% chance to pick from top 10
                idx=$((RANDOM % 10))
            elif [[ $rand -lt 70 ]]; then
                # 30% chance to pick from 11-20
                idx=$((10 + RANDOM % 10))
            else
                # 30% chance to pick from 21-30
                idx=$((20 + RANDOM % 10))
            fi
            
            # Check if this index is already used
            used=false
            for used_idx in "${used_indices[@]}"; do
                if [[ $used_idx -eq $idx ]]; then
                    used=true
                    break
                fi
            done
            
            if [[ "$used" == "false" ]]; then
                used_indices+=($idx)
                new_combo+=(${top_numbers[$idx]})
                break
            fi
        done
    done
    
    # Sort the combination
    sorted_combo=$(printf "%s\n" "${new_combo[@]}" | sort -n | tr '\n' ',' | sed 's/,$//')
    
    # Check if it's a past combination
    if is_past_combination "$sorted_combo"; then
        continue
    fi
    
    # Check similarity with existing recommendations
    too_similar=false
    for existing in "${recommendations[@]}"; do
        if ! check_similarity "$sorted_combo" "$existing"; then
            too_similar=true
            break
        fi
    done
    
    if [[ "$too_similar" == "false" ]]; then
        recommendations+=("$sorted_combo")
    fi
done

# Print recommendations with odds and percentages
echo ""
echo -e "${BLUE}${BOLD}🎯 LOTTERY NUMBER RECOMMENDATIONS${RESET}"
echo -e "${BLUE}===============================================${RESET}"
echo ""

# Print table header
printf "%-3s | %-2s | %-2s | %-2s | %-2s | %-2s | %-2s | %-15s | %-10s\n" "No." "N1" "N2" "N3" "N4" "N5" "N6" "Avg Odds" "Avg %"
echo "-----|----|----|----|----|----|----|---------------|----------"

for i in "${!recommendations[@]}"; do
    IFS=',' read -ra nums <<< "${recommendations[$i]}"
    
    # Calculate average odds and percentage for this combination
    total_odds=0
    total_percent=0
    valid_numbers=0
    
    for n in "${nums[@]}"; do
        if [[ ${odds[$n]:-0} -gt 0 ]]; then
            total_odds=$((total_odds + ${odds[$n]}))
            prob_percent=$(echo "scale=2; ${prob[$n]} * 100" | bc -l 2>/dev/null || echo "0.00")
            total_percent=$(echo "scale=2; $total_percent + $prob_percent" | bc -l 2>/dev/null || echo "0.00")
            valid_numbers=$((valid_numbers + 1))
        fi
    done
    
    if [[ $valid_numbers -gt 0 ]]; then
        avg_odds=$(echo "scale=0; $total_odds / $valid_numbers" | bc -l 2>/dev/null || echo "0")
        avg_percent=$(echo "scale=2; $total_percent / $valid_numbers" | bc -l 2>/dev/null || echo "0.00")
    else
        avg_odds=0
        avg_percent="0.00"
    fi
    
    # Print the row with numbers in columns
    printf "%-3s | %-2s | %-2s | %-2s | %-2s | %-2s | %-2s | %-15s | %-10s\n" \
        "$((i+1))" \
        "${nums[0]}" \
        "${nums[1]}" \
        "${nums[2]}" \
        "${nums[3]}" \
        "${nums[4]}" \
        "${nums[5]}" \
        "1 in $avg_odds" \
        "$avg_percent%"
done

echo ""
echo -e "${GREEN}📊 ANALYSIS SUMMARY:${RESET}"
echo -e "  • Total draws processed: ${BLUE}$total_draws${RESET}"
echo -e "  • Generated ${BLUE}${#recommendations[@]}${RESET} unique recommendations after ${BLUE}$attempts${RESET} attempts"
echo -e "  • Each entry uses the most probable numbers based on historical analysis"
echo -e "  • No entry duplicates past winning combinations"
echo -e "  • No entry shares more than 2 numbers with other recommendations"
echo -e "  • Average odds and percentages shown for each combination"
echo ""
) &

# Wait for spinner to finish
wait $!

echo -e "${GREEN}Analysis completed successfully!${RESET}" 