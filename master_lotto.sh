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
    while kill -0 "$pid" 2>/dev/null; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        spinstr=$temp${spinstr%$temp}
        sleep "$delay"
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# Success/Error indicator function
show_result() {
    local success=$1
    local message=$2
    if [ "$success" -eq 0 ]; then
        echo -e "${GREEN}✓ $message${RESET}"
    else
        echo -e "${RED}✗ $message${RESET}"
    fi
}

INTERACTIVE=1
if [ ! -t 0 ] || [ ! -t 1 ]; then
    INTERACTIVE=0
    OPTION=${AUTO_CHOICE:-4}
    export TERM=${TERM:-xterm}
else
    OPTION=""
fi

while true; do
    if [ "$INTERACTIVE" -eq 1 ]; then
        clear
    fi
    echo -e "${BLUE}${BOLD}========================="
    echo -e " Lotto Master Menu"
    echo -e "=========================${RESET}"
    echo -e "${BOLD}1)${RESET} Scrape Lotto Results"
    echo -e "${BOLD}2)${RESET} Parse Data & Recommend Entries (with auto-clean)"
    echo -e "${BOLD}3)${RESET} Check & Install Requirements"
    echo -e "${BOLD}4)${RESET} Exit"
    echo -e "${BLUE}=========================${RESET}"
    echo
    if [ "$INTERACTIVE" -eq 1 ]; then
        read -r -p "Select an option [1-4]: " OPTION
    else
        echo "Select an option [1-4]: $OPTION"
    fi
    echo
    case $OPTION in
        1)
            echo -e "${BLUE}Running scrape_lotto_results.sh...${RESET}"
            ./scrape_lotto_results.sh &
            spinner $!
            wait $!
            status=$?
            echo
            show_result "$status" "Scraping completed"
            if [ "$status" -eq 0 ]; then
                echo -e "${GREEN}✓ Data successfully scraped and saved to CSV files${RESET}"
            else
                echo -e "${RED}✗ Scraping failed. Check the output above for details${RESET}"
            fi
            echo
            if [ "$INTERACTIVE" -eq 1 ]; then
                read -r -p "Press Enter to return to menu..."
            fi
            ;;
        2)
            echo -e "${BLUE}Running parse_and_recommend.sh...${RESET}"
            ./parse_and_recommend.sh &
            pid=$!
            spinner "$pid" &
            spinner_pid=$!
            wait "$pid"
            status=$?
            kill "$spinner_pid" 2>/dev/null
            echo
            show_result "$status" "Analysis completed"
            if [ "$status" -eq 0 ]; then
                echo -e "${GREEN}✓ Recommendations generated successfully${RESET}"
            else
                echo -e "${RED}✗ Analysis failed. Check the output above for details${RESET}"
            fi
            echo
            if [ "$INTERACTIVE" -eq 1 ]; then
                read -r -p "Press Enter to return to menu..."
            fi
            ;;
        3)
            echo -e "${BLUE}Checking and installing requirements...${RESET}"
            ./requirements.sh &
            spinner $!
            wait $!
            status=$?
            echo
            show_result "$status" "Requirements check completed"
            if [ "$status" -eq 0 ]; then
                echo -e "${GREEN}✓ All requirements are satisfied${RESET}"
            else
                echo -e "${YELLOW}⚠ Some requirements may not have installed correctly${RESET}"
            fi
            echo
            if [ "$INTERACTIVE" -eq 1 ]; then
                read -r -p "Press Enter to return to menu..."
            fi
            ;;
        4)
            echo -e "${GREEN}Exiting. Have a lucky day!${RESET}"
            exit 0
            ;;
        *)
            echo -e "${YELLOW}Invalid option. Please select 1, 2, 3, or 4.${RESET}"
            if [ "$INTERACTIVE" -eq 1 ]; then
                sleep 1.5
            fi
            ;;
    esac
    echo
    if [ "$INTERACTIVE" -ne 1 ]; then
        break
    fi
    sleep 0.5
done
