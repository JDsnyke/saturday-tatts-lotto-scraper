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

# Requirements checker/installer for Lotto scripts
REQUIRED_CMDS=(curl pup awk grep)

MISSING=()

# Check for each required command
for cmd in "${REQUIRED_CMDS[@]}"; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        MISSING+=("$cmd")
    fi
done

if [ ${#MISSING[@]} -eq 0 ]; then
    echo -e "${GREEN}All requirements are already installed.${RESET}"
    exit 0
fi

echo -e "${YELLOW}Missing requirements: ${MISSING[*]}${RESET}"

# Detect OS and package manager
OS_TYPE=""
PKG_MANAGER=""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="Linux"
elif [[ "$OSTYPE" == "freebsd"* ]]; then
    OS_TYPE="FreeBSD"
elif [[ "$OSTYPE" == "cygwin"* ]] || [[ "$OSTYPE" == "msys"* ]]; then
    OS_TYPE="Windows"
else
    OS_TYPE="Unknown"
fi

echo -e "${BLUE}Detected OS: $OS_TYPE${RESET}"

# Detect package manager based on OS
case "$OS_TYPE" in
    "macOS")
        if command -v brew >/dev/null 2>&1; then
            PKG_MANAGER="brew"
        elif command -v port >/dev/null 2>&1; then
            PKG_MANAGER="port"
        else
            echo -e "${RED}No package manager found. Please install Homebrew: https://brew.sh/ or MacPorts: https://www.macports.org/${RESET}"
            exit 1
        fi
        ;;
    "Linux")
        # Check for different Linux package managers
        if command -v apt >/dev/null 2>&1; then
            PKG_MANAGER="apt"
        elif command -v yum >/dev/null 2>&1; then
            PKG_MANAGER="yum"
        elif command -v dnf >/dev/null 2>&1; then
            PKG_MANAGER="dnf"
        elif command -v pacman >/dev/null 2>&1; then
            PKG_MANAGER="pacman"
        elif command -v zypper >/dev/null 2>&1; then
            PKG_MANAGER="zypper"
        elif command -v emerge >/dev/null 2>&1; then
            PKG_MANAGER="emerge"
        else
            echo -e "${RED}No supported package manager found. Supported: apt, yum, dnf, pacman, zypper, emerge${RESET}"
            exit 1
        fi
        ;;
    "FreeBSD")
        if command -v pkg >/dev/null 2>&1; then
            PKG_MANAGER="pkg"
        elif command -v ports >/dev/null 2>&1; then
            PKG_MANAGER="ports"
        else
            echo -e "${RED}No package manager found for FreeBSD.${RESET}"
            exit 1
        fi
        ;;
    "Windows")
        echo -e "${YELLOW}Windows detected. Please install requirements manually:${RESET}"
        echo "- curl: https://curl.se/windows/"
        echo "- pup: https://github.com/ericchiang/pup/releases"
        echo "- awk/grep: Available in Git Bash or WSL"
        exit 1
        ;;
    *)
        echo -e "${RED}Unsupported OS: $OS_TYPE. Please install requirements manually.${RESET}"
        exit 1
        ;;
esac

echo -e "${BLUE}Using package manager: $PKG_MANAGER${RESET}"

# Install missing requirements based on package manager
(
case "$PKG_MANAGER" in
    "brew")
        echo -e "${BLUE}Installing with Homebrew...${RESET}"
        for pkg in "${MISSING[@]}"; do
            echo -e "${BLUE}Installing $pkg...${RESET}"
            brew install "$pkg"
        done
        ;;
    "port")
        echo -e "${BLUE}Installing with MacPorts...${RESET}"
        for pkg in "${MISSING[@]}"; do
            echo -e "${BLUE}Installing $pkg...${RESET}"
            sudo port install "$pkg"
        done
        ;;
    "apt")
        echo -e "${BLUE}Installing with apt...${RESET}"
        sudo apt update
        for pkg in "${MISSING[@]}"; do
            echo -e "${BLUE}Installing $pkg...${RESET}"
            sudo apt install -y "$pkg"
        done
        ;;
    "yum")
        echo -e "${BLUE}Installing with yum...${RESET}"
        sudo yum update
        for pkg in "${MISSING[@]}"; do
            echo -e "${BLUE}Installing $pkg...${RESET}"
            sudo yum install -y "$pkg"
        done
        ;;
    "dnf")
        echo -e "${BLUE}Installing with dnf...${RESET}"
        sudo dnf update
        for pkg in "${MISSING[@]}"; do
            echo -e "${BLUE}Installing $pkg...${RESET}"
            sudo dnf install -y "$pkg"
        done
        ;;
    "pacman")
        echo -e "${BLUE}Installing with pacman...${RESET}"
        sudo pacman -Sy
        for pkg in "${MISSING[@]}"; do
            echo -e "${BLUE}Installing $pkg...${RESET}"
            sudo pacman -S --noconfirm "$pkg"
        done
        ;;
    "zypper")
        echo -e "${BLUE}Installing with zypper...${RESET}"
        sudo zypper refresh
        for pkg in "${MISSING[@]}"; do
            echo -e "${BLUE}Installing $pkg...${RESET}"
            sudo zypper install -y "$pkg"
        done
        ;;
    "emerge")
        echo -e "${BLUE}Installing with emerge...${RESET}"
        sudo emerge --sync
        for pkg in "${MISSING[@]}"; do
            echo -e "${BLUE}Installing $pkg...${RESET}"
            sudo emerge "$pkg"
        done
        ;;
    "pkg")
        echo -e "${BLUE}Installing with pkg...${RESET}"
        sudo pkg update
        for pkg in "${MISSING[@]}"; do
            echo -e "${BLUE}Installing $pkg...${RESET}"
            sudo pkg install "$pkg"
        done
        ;;
    "ports")
        echo -e "${BLUE}Installing with ports...${RESET}"
        for pkg in "${MISSING[@]}"; do
            echo -e "${BLUE}Installing $pkg...${RESET}"
            sudo ports install "$pkg"
        done
        ;;
    *)
        echo -e "${RED}Unsupported package manager: $PKG_MANAGER${RESET}"
        exit 1
        ;;
esac
) &
spinner $!

echo
echo "Installation completed!"
echo "Verifying requirements..."

# Verify all requirements are now installed
VERIFY_MISSING=()
for cmd in "${REQUIRED_CMDS[@]}"; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        VERIFY_MISSING+=("$cmd")
    fi
done

if [ ${#VERIFY_MISSING[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All requirements successfully installed and verified!${RESET}"
else
    echo -e "${RED}❌ Some requirements still missing: ${VERIFY_MISSING[*]}${RESET}"
    echo "Please install them manually."
    exit 1
fi 