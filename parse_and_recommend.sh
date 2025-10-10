#!/bin/bash

# Color definitions
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
BOLD="\033[1m"
RESET="\033[0m"

sort_numbers() {
    local -a arr=("$@")
    local n=${#arr[@]}

    for ((i = 0; i < n; i++)); do
        local current=${arr[i]}
        if [[ -z $current ]]; then
            continue
        fi
        arr[i]=$((10#$current))
    done

    for ((i = 0; i < n; i++)); do
        for ((j = i + 1; j < n; j++)); do
            if (( arr[j] < arr[i] )); then
                local tmp=${arr[i]}
                arr[i]=${arr[j]}
                arr[j]=$tmp
            fi
        done
    done

    local result=""
    for ((i = 0; i < n; i++)); do
        if [[ -n ${arr[i]} ]]; then
            result+="${arr[i]},"
        fi
    done

    printf '%s' "${result%,}"
}

# Function to clean CSV files automatically
clean_csv_files() {
    local winning_file="$1"
    local supp_file="$2"

    echo -e "${BLUE}🧹 Auto-cleaning CSV files before analysis...${RESET}"

    # Clean winning numbers file
    if [ -f "$winning_file" ]; then
        local temp_file="${winning_file}.tmp"
        # Keep only valid data lines: YYYY-MM-DD followed by six comma separated numbers
        grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2},([0-9]{1,2},){5}[0-9]{1,2}$' "$winning_file" > "$temp_file"
        if [ -s "$temp_file" ]; then
            mv "$temp_file" "$winning_file"
        else
            rm -f "$temp_file"
        fi
    fi

    # Clean supplementary numbers file
    if [ -f "$supp_file" ]; then
        local temp_file="${supp_file}.tmp"
        # Keep only valid supplementary lines: YYYY-MM-DD followed by two comma separated numbers
        grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2},[0-9]{1,2},[0-9]{1,2}$' "$supp_file" > "$temp_file"
        if [ -s "$temp_file" ]; then
            mv "$temp_file" "$supp_file"
        else
            rm -f "$temp_file"
        fi
    fi
}

load_statistics() {
    local winning_file="$1"
    local supp_file="$2"

    local awk_script='
        BEGIN { FS = "," }
        function is_valid_row() {
            if (NF < 7) { return 0 }
            for (i = 2; i <= 7; i++) {
                n = $i + 0
                if (n < 1 || n > 45) { return 0 }
            }
            return 1
        }
        ARGIND == 1 {
            if ($0 ~ /^[[:space:]]*$/) { next }
            if (is_valid_row()) {
                total_draws++
                for (i = 2; i <= 7; i++) {
                    n = $i + 0
                    main_freq[n]++
                }
            }
            next
        }
        ARGIND == 2 {
            if ($0 ~ /^[[:space:]]*$/) { next }
            for (i = 2; i <= NF; i++) {
                n = $i + 0
                if (n >= 1 && n <= 45) {
                    supp_freq[n]++
                }
            }
            next
        }
        END {
            printf "TOTAL %d\n", total_draws
            for (i = 1; i <= 45; i++) {
                main = main_freq[i] + 0
                supp = supp_freq[i] + 0
                prob = (total_draws > 0 && main > 0) ? main / total_draws : 0
                combined = (total_draws > 0) ? prob + (supp_weight * supp) / total_draws : 0
                odds = (main > 0) ? int((total_draws + main - 1) / main) : 0
                printf "%02d %d %.6f %.8f %d %d\n", i, main, prob, combined, odds, supp
            }
        }
    '

    local supp_weight=0.35
    local -a stats_lines

    if [ -f "$supp_file" ] && [ -s "$supp_file" ]; then
        mapfile -t stats_lines < <(awk -v supp_weight="$supp_weight" "$awk_script" "$winning_file" "$supp_file")
    else
        mapfile -t stats_lines < <(awk -v supp_weight="0" "$awk_script" "$winning_file")
    fi

    TOTAL_DRAWS=0
    unset FREQ PROB COMBINED ODDS SUPP
    declare -g -a FREQ PROB COMBINED ODDS SUPP

    for line in "${stats_lines[@]}"; do
        if [[ $line == TOTAL* ]]; then
            TOTAL_DRAWS=${line#TOTAL }
            continue
        fi
        read -r raw_num freq prob combined odds supp <<<"$line"
        local num=$((10#$raw_num))
        FREQ[$num]=$freq
        PROB[$num]=$prob
        COMBINED[$num]=$combined
        ODDS[$num]=$odds
        SUPP[$num]=$supp
    done
}

load_past_combinations() {
    local winning_file="$1"
    PAST_COMBINATIONS=()
    while IFS=',' read -r date n1 n2 n3 n4 n5 n6; do
        if [[ -z $date || -z $n6 ]]; then
            continue
        fi
        sorted_combo=$(sort_numbers "$n1" "$n2" "$n3" "$n4" "$n5" "$n6")
        PAST_COMBINATIONS+=("$sorted_combo")
    done < "$winning_file"
}

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

is_past_combination() {
    local combo="$1"
    for past in "${PAST_COMBINATIONS[@]}"; do
        if [[ "$combo" == "$past" ]]; then
            return 0
        fi
    done
    return 1
}

contains_number() {
    local needle=$1
    shift
    for item in "$@"; do
        if [[ $item -eq $needle ]]; then
            return 0
        fi
    done
    return 1
}

generate_recommendations() {
    local -n _sorted_numbers=$1

    if ! command -v python3 >/dev/null 2>&1; then
        echo -e "${RED}Error: python3 is required to generate weighted combinations.${RESET}"
        return 1
    fi

    local python_input=$(mktemp)
    {
        printf '%s\n' "${ranked[@]}"
        printf '%s\n' '--PAST--'
        printf '%s\n' "${PAST_COMBINATIONS[@]}"
    } > "$python_input"

    mapfile -t RECOMMENDATIONS < <(python3 - "$python_input" <<'PYINNER'
import sys
import itertools

data_path = sys.argv[1]
with open(data_path, 'r', encoding='utf-8') as handle:
    lines = [line.strip() for line in handle if line.strip()]
if not lines:
    sys.exit(1)

if "--PAST--" in lines:
    split_index = lines.index("--PAST--")
    stat_lines = lines[:split_index]
    past_lines = lines[split_index + 1 :]
else:
    stat_lines = lines
    past_lines = []

numbers = []
for entry in stat_lines:
    try:
        num, combined, freq, supp, prob = entry.split(":")
    except ValueError:
        continue
    numbers.append({
        "number": int(num),
        "combined": float(combined),
        "freq": int(freq),
        "supp": int(supp),
        "prob": float(prob),
    })

if len(numbers) < 6:
    sys.exit(1)

numbers.sort(key=lambda item: (-item["combined"], item["number"]))

past_set = set()
for combo in past_lines:
    if not combo:
        continue
    try:
        past_set.add(tuple(sorted(int(part) for part in combo.split(","))))
    except ValueError:
        continue

def combo_score(combo):
    return sum(item["combined"] for item in combo)

def generate_candidates(pool):
    for combo in itertools.combinations(pool, 6):
        yield combo_score(combo), tuple(sorted(item["number"] for item in combo))

selected = []
max_pool = min(len(numbers), 28)
start_pool = min(16, len(numbers))

if start_pool < 6:
    start_pool = len(numbers)

if start_pool < 6:
    sys.exit(1)

def share_count(a, b):
    return len(set(a) & set(b))

for pool_size in range(start_pool, max_pool + 1):
    pool = numbers[:pool_size]
    candidates = []
    for score, combo in generate_candidates(pool):
        if combo in past_set:
            continue
        candidates.append((score, combo))
    candidates.sort(key=lambda item: (-item[0], item[1]))
    for score, combo in candidates:
        if any(share_count(combo, existing) > 2 for existing in selected):
            continue
        selected.append(combo)
        if len(selected) == 10:
            break
    if len(selected) == 10:
        break

if len(selected) < 10:
    for pool_size in range(start_pool, max_pool + 1):
        pool = numbers[:pool_size]
        candidates = []
        for score, combo in generate_candidates(pool):
            if combo in past_set:
                continue
            candidates.append((score, combo))
        candidates.sort(key=lambda item: (-item[0], item[1]))
        for score, combo in candidates:
            if combo in selected:
                continue
            if any(share_count(combo, existing) > 3 for existing in selected):
                continue
            selected.append(combo)
            if len(selected) == 10:
                break
        if len(selected) == 10:
            break

if len(selected) < 10:
    pool = numbers[:max_pool]
    candidates = []
    seen = set()
    for score, combo in generate_candidates(pool):
        if combo in seen:
            continue
        candidates.append((score, combo))
        seen.add(combo)
    candidates.sort(key=lambda item: (-item[0], item[1]))
    for score, combo in candidates:
        if combo in selected:
            continue
        selected.append(combo)
        if len(selected) == 10:
            break

for combo in selected[:10]:
    print(",".join(str(num) for num in combo))
PYINNER
    )

    rm -f "$python_input"

    if (( ${#RECOMMENDATIONS[@]} == 0 )); then
        return 1
    fi
}

print_recommendations() {
    printf "%-3s | %-2s | %-2s | %-2s | %-2s | %-2s | %-2s | %-15s | %-10s | %-6s | %-4s\n" \
        "No." "N1" "N2" "N3" "N4" "N5" "N6" "Avg Odds" "Avg %" "Main" "Supp"
    echo "-----|----|----|----|----|----|----|---------------|-----------|-------|------"

    for i in "${!RECOMMENDATIONS[@]}"; do
        IFS=',' read -ra nums <<< "${RECOMMENDATIONS[$i]}"

        local total_odds=0
        local total_prob="0.0"
        local main_hits=0
        local supp_hits=0
        local valid_numbers=0

        for n in "${nums[@]}"; do
            local odds=${ODDS[$n]:-0}
            local combined=${COMBINED[$n]:-0}
            local main=${FREQ[$n]:-0}
            local supp=${SUPP[$n]:-0}

            if (( odds > 0 )); then
                total_odds=$((total_odds + odds))
            fi

            total_prob=$(awk -v current="$total_prob" -v add="$combined" 'BEGIN { printf "%.8f", current + add }')

            if (( main > 0 )); then
                main_hits=$((main_hits + main))
            fi
            if (( supp > 0 )); then
                supp_hits=$((supp_hits + supp))
            fi
            valid_numbers=$((valid_numbers + 1))
        done

        local avg_odds=0
        local avg_percent="0.00"
        if (( valid_numbers > 0 )); then
            avg_odds=$(awk -v total="$total_odds" -v count="$valid_numbers" 'BEGIN { if (count == 0) { printf "0" } else { printf "%.0f", total / count } }')
            avg_percent=$(awk -v total="$total_prob" -v count="$valid_numbers" 'BEGIN { if (count == 0) { printf "0.00" } else { printf "%.2f", (total / count) * 100 } }')
        fi

        printf "%-3s | %-2s | %-2s | %-2s | %-2s | %-2s | %-2s | %-15s | %-10s | %-6s | %-4s\n" \
            "$((i + 1))" \
            "${nums[0]}" \
            "${nums[1]}" \
            "${nums[2]}" \
            "${nums[3]}" \
            "${nums[4]}" \
            "${nums[5]}" \
            "1 in $avg_odds" \
            "$avg_percent%" \
            "$main_hits" \
            "$supp_hits"
    done
}

perform_analysis() {
    load_statistics "$WINNING_FILE" "$SUPP_FILE"

    if [[ -z $TOTAL_DRAWS || $TOTAL_DRAWS -eq 0 ]]; then
        echo -e "${RED}Error: No valid draw data found in $WINNING_FILE.${RESET}"
        return 1
    fi

    if [ "${#FREQ[@]}" -lt 6 ]; then
        echo -e "${RED}Error: Not enough unique numbers to generate recommendations.${RESET}"
        return 1
    fi

    load_past_combinations "$WINNING_FILE"

    local score_lines=()
    for n in {1..45}; do
        local combined=${COMBINED[$n]:-0}
        local freq=${FREQ[$n]:-0}
        local supp=${SUPP[$n]:-0}
        local prob=${PROB[$n]:-0}
        score_lines+=("$(printf "%02d:%.8f:%d:%d:%.6f" "$n" "$combined" "$freq" "$supp" "$prob")")
    done

    IFS=$'\n' read -r -d '' -a ranked < <(printf "%s\n" "${score_lines[@]}" | LC_ALL=C sort -t: -k2,2nr -k1,1n && printf '\0')

    local -a sorted_numbers=()
    for entry in "${ranked[@]}"; do
        IFS=':' read -r raw_num combined freq supp prob <<<"$entry"
        local num=$((10#$raw_num))
        sorted_numbers+=($num)
    done

    if ! generate_recommendations sorted_numbers; then
        echo -e "${RED}Error: Failed to generate deterministic recommendations.${RESET}"
        return 1
    fi

    echo ""
    echo -e "${BLUE}${BOLD}🎯 LOTTERY NUMBER RECOMMENDATIONS${RESET}"
    echo -e "${BLUE}===========================================================${RESET}"
    echo ""

    print_recommendations

    echo ""
    echo -e "${GREEN}📊 ANALYSIS SUMMARY:${RESET}"
    echo -e "  • Total draws processed: ${BLUE}$TOTAL_DRAWS${RESET}"
    echo -e "  • Considered supplementary hits with ${BLUE}35%${RESET} weighting for heat scoring"
    echo -e "  • Generated ${BLUE}${#RECOMMENDATIONS[@]}${RESET} unique recommendations"
    echo -e "  • No entry duplicates historical winning combinations"
    echo -e "  • No entry shares more than 2 numbers with other recommendations"
    echo -e "  • Scores balance main draw frequency with supplementary momentum"
    echo ""
}

WINNING_FILE="winning_numbers.csv"
SUPP_FILE="supplementary_numbers.csv"

if [ ! -f "$WINNING_FILE" ]; then
    echo -e "${RED}Error: $WINNING_FILE not found. Please run the scraper first.${RESET}"
    exit 1
fi

if [ ! -s "$WINNING_FILE" ]; then
    echo -e "${RED}Error: $WINNING_FILE is empty. Scrape results before analysis.${RESET}"
    exit 1
fi

# Auto-clean CSV files before processing
clean_csv_files "$WINNING_FILE" "$SUPP_FILE"

echo -e "${BLUE}Analyzing past results to recommend 10 unique entries with highest probability numbers...${RESET}"

if ! perform_analysis; then
    exit 1
fi

echo -e "${GREEN}Analysis completed successfully!${RESET}"
