#!/bin/bash

# Color definitions
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
BOLD="\033[1m"
RESET="\033[0m"

# Requirements checker/installer for Lotto scripts
REQUIRED_CMDS=(curl python3 pup awk grep)

MISSING=()

# Helper utilities
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

use_sudo_if_available() {
    if command_exists sudo; then
        sudo "$@"
    else
        "$@"
    fi
}

install_binary() {
    local source="$1"
    local name="$2"
    local target="/usr/local/bin/$name"

    if cp "$source" "$target" 2>/dev/null; then
        chmod +x "$target"
        echo -e "${GREEN}Installed $name to $target${RESET}"
        return 0
    fi

    if command_exists sudo && sudo cp "$source" "$target" 2>/dev/null; then
        sudo chmod +x "$target"
        echo -e "${GREEN}Installed $name to $target${RESET}"
        return 0
    fi

    local local_bin="$HOME/.local/bin"
    mkdir -p "$local_bin"
    if cp "$source" "$local_bin/$name" 2>/dev/null; then
        chmod +x "$local_bin/$name"
        export PATH="$local_bin:$PATH"
        echo -e "${YELLOW}Installed $name to $local_bin. Ensure this directory is in your PATH.${RESET}"
        return 0
    fi

    echo -e "${RED}Failed to install $name binary.${RESET}"
    return 1
}

install_pup_binary() {
    local os="$1"
    local version="v0.4.0"
    local arch

    case "$(uname -m)" in
        x86_64|amd64)
            arch="amd64"
            ;;
        arm64|aarch64)
            arch="arm64"
            ;;
        armv7l|armv6l)
            arch="arm"
            ;;
        i386|i686)
            arch="386"
            ;;
        *)
            echo -e "${RED}Unsupported architecture for automatic pup installation.${RESET}"
            return 1
            ;;
    esac

    local asset_os
    case "$os" in
        macOS)
            asset_os="darwin"
            ;;
        Linux)
            asset_os="linux"
            ;;
        FreeBSD)
            asset_os="freebsd"
            ;;
        *)
            echo -e "${RED}No prebuilt pup binary available for $os. Install manually from https://github.com/ericchiang/pup/releases.${RESET}"
            return 1
            ;;
    esac

    local tmp_dir
    tmp_dir=$(mktemp -d 2>/dev/null || mktemp -d -t pup)
    local zip_path="$tmp_dir/pup.zip"
    local url="https://github.com/ericchiang/pup/releases/download/${version}/pup_${version}_${asset_os}_${arch}.zip"

    echo -e "${BLUE}Downloading pup from ${url}${RESET}"
    if ! curl -fsSL "$url" -o "$zip_path"; then
        echo -e "${RED}Failed to download pup archive.${RESET}"
        rm -rf "$tmp_dir"
        return 1
    fi

    if ! python3 - "$zip_path" "$tmp_dir" <<'PY'; then
import sys
import zipfile

zip_path, out_dir = sys.argv[1:3]
with zipfile.ZipFile(zip_path) as archive:
    archive.extractall(out_dir)
PY
        echo -e "${RED}Failed to extract pup archive.${RESET}"
        rm -rf "$tmp_dir"
        return 1
    fi

    local extracted="$tmp_dir/pup"
    if [ ! -f "$extracted" ]; then
        extracted=$(find "$tmp_dir" -maxdepth 2 -type f -name 'pup' | head -n 1)
    fi

    if [ ! -f "$extracted" ]; then
        echo -e "${RED}Unable to locate pup binary in the downloaded archive.${RESET}"
        rm -rf "$tmp_dir"
        return 1
    fi

    chmod +x "$extracted"
    if ! install_binary "$extracted" "pup"; then
        rm -rf "$tmp_dir"
        return 1
    fi

    rm -rf "$tmp_dir"
    return 0
}

map_package_name() {
    local cmd="$1"
    local manager="$2"
    case "$cmd" in
        awk)
            case "$manager" in
                brew)
                    echo "gawk"
                    ;;
                port)
                    echo "gawk"
                    ;;
                *)
                    echo "gawk"
                    ;;
            esac
            ;;
        python3)
            case "$manager" in
                brew)
                    echo "python"
                    ;;
                port)
                    echo "python310"
                    ;;
                pacman)
                    echo "python"
                    ;;
                zypper)
                    echo "python3"
                    ;;
                emerge)
                    echo "dev-lang/python"
                    ;;
                pkg)
                    echo "python3"
                    ;;
                *)
                    echo "python3"
                    ;;
            esac
            ;;
        *)
            echo "$cmd"
            ;;
    esac
}

install_with_manager() {
    local manager="$1"
    local package="$2"

    case "$manager" in
        brew)
            brew install "$package"
            ;;
        port)
            use_sudo_if_available port install "$package"
            ;;
        apt)
            use_sudo_if_available env DEBIAN_FRONTEND=noninteractive apt-get install -y "$package"
            ;;
        yum)
            use_sudo_if_available yum install -y "$package"
            ;;
        dnf)
            use_sudo_if_available dnf install -y "$package"
            ;;
        pacman)
            use_sudo_if_available pacman -S --noconfirm "$package"
            ;;
        zypper)
            use_sudo_if_available zypper install -y "$package"
            ;;
        emerge)
            use_sudo_if_available emerge "$package"
            ;;
        pkg)
            use_sudo_if_available pkg install -y "$package"
            ;;
        *)
            echo -e "${RED}Unsupported package manager: $manager${RESET}"
            return 1
            ;;
    esac
}

prepare_package_manager() {
    local manager="$1"
    case "$manager" in
        apt)
            echo -e "${BLUE}Updating apt package lists...${RESET}"
            use_sudo_if_available env DEBIAN_FRONTEND=noninteractive apt-get update || return 1
            ;;
        yum)
            echo -e "${BLUE}Refreshing yum metadata...${RESET}"
            use_sudo_if_available yum makecache || return 1
            ;;
        dnf)
            echo -e "${BLUE}Refreshing dnf metadata...${RESET}"
            use_sudo_if_available dnf makecache || return 1
            ;;
        pacman)
            echo -e "${BLUE}Synchronizing pacman databases...${RESET}"
            use_sudo_if_available pacman -Sy || return 1
            ;;
        zypper)
            echo -e "${BLUE}Refreshing zypper repositories...${RESET}"
            use_sudo_if_available zypper refresh || return 1
            ;;
        emerge)
            echo -e "${BLUE}Syncing Portage tree...${RESET}"
            use_sudo_if_available emerge --sync || return 1
            ;;
        pkg)
            echo -e "${BLUE}Updating pkg repositories...${RESET}"
            use_sudo_if_available pkg update || return 1
            ;;
        port)
            echo -e "${BLUE}Syncing MacPorts (selfupdate)...${RESET}"
            use_sudo_if_available port selfupdate || return 1
            ;;
        brew)
            :
            ;;
        *)
            ;;
    esac
    return 0
}

determine_environment() {
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

    case "$OS_TYPE" in
        macOS)
            if command_exists brew; then
                PKG_MANAGER="brew"
            elif command_exists port; then
                PKG_MANAGER="port"
            else
                PKG_MANAGER=""
            fi
            ;;
        Linux)
            if command_exists apt-get; then
                PKG_MANAGER="apt"
            elif command_exists apt; then
                PKG_MANAGER="apt"
            elif command_exists yum; then
                PKG_MANAGER="yum"
            elif command_exists dnf; then
                PKG_MANAGER="dnf"
            elif command_exists pacman; then
                PKG_MANAGER="pacman"
            elif command_exists zypper; then
                PKG_MANAGER="zypper"
            elif command_exists emerge; then
                PKG_MANAGER="emerge"
            else
                PKG_MANAGER=""
            fi
            ;;
        FreeBSD)
            if command_exists pkg; then
                PKG_MANAGER="pkg"
            elif command_exists ports; then
                PKG_MANAGER="ports"
            else
                PKG_MANAGER=""
            fi
            ;;
        *)
            PKG_MANAGER=""
            ;;
    esac
}

# Discover missing commands
for cmd in "${REQUIRED_CMDS[@]}"; do
    if ! command_exists "$cmd"; then
        MISSING+=("$cmd")
    fi
done

if [ ${#MISSING[@]} -eq 0 ]; then
    echo -e "${GREEN}All requirements are already installed.${RESET}"
    exit 0
fi

echo -e "${YELLOW}Missing requirements: ${MISSING[*]}${RESET}"

determine_environment

if [ "$OS_TYPE" = "Windows" ] || [ "$OS_TYPE" = "Unknown" ]; then
    echo -e "${RED}Automatic installation is not supported on this platform. Please install the requirements manually.${RESET}"
    exit 1
fi

if [ -z "$PKG_MANAGER" ] && [[ " ${MISSING[*]} " != *" pup "* ]]; then
    echo -e "${RED}No supported package manager detected. Please install the requirements manually.${RESET}"
    exit 1
fi

if [ -n "$PKG_MANAGER" ]; then
    NEEDS_MANAGER=0
    for cmd in "${MISSING[@]}"; do
        if [ "$cmd" != "pup" ] || [[ "$PKG_MANAGER" = "brew" || "$PKG_MANAGER" = "port" ]]; then
            NEEDS_MANAGER=1
            break
        fi
    done

    if [ "$NEEDS_MANAGER" -eq 1 ]; then
        if ! prepare_package_manager "$PKG_MANAGER"; then
            echo -e "${RED}Failed to prepare package manager $PKG_MANAGER. Please resolve the issue and re-run the script.${RESET}"
            exit 1
        fi
    fi

    echo -e "${BLUE}Using package manager: $PKG_MANAGER${RESET}"
fi

for cmd in "${MISSING[@]}"; do
    if [ "$cmd" = "pup" ]; then
        echo -e "${BLUE}Installing pup...${RESET}"
        if [ -n "$PKG_MANAGER" ]; then
            case "$PKG_MANAGER" in
                brew)
                    if brew install pup; then
                        continue
                    fi
                    echo -e "${YELLOW}Falling back to manual pup installation...${RESET}"
                    ;;
                port)
                    if use_sudo_if_available port install pup; then
                        continue
                    fi
                    echo -e "${YELLOW}Falling back to manual pup installation...${RESET}"
                    ;;
                pkg)
                    if use_sudo_if_available pkg install -y pup; then
                        continue
                    fi
                    echo -e "${YELLOW}Falling back to manual pup installation...${RESET}"
                    ;;
                *)
                    ;;
            esac
        fi

        if ! install_pup_binary "$OS_TYPE"; then
            echo -e "${RED}Failed to install pup automatically. Please install it manually from https://github.com/ericchiang/pup/releases.${RESET}"
        fi
        continue
    fi

    if [ -z "$PKG_MANAGER" ]; then
        echo -e "${RED}Cannot install $cmd automatically. Install it manually and re-run the script.${RESET}"
        continue
    fi

    package=$(map_package_name "$cmd" "$PKG_MANAGER")
    echo -e "${BLUE}Installing $cmd (${package})...${RESET}"
    install_with_manager "$PKG_MANAGER" "$package" || echo -e "${RED}Failed to install $cmd.${RESET}"
done

echo
echo "Verifying requirements..."

VERIFY_MISSING=()
for cmd in "${REQUIRED_CMDS[@]}"; do
    if ! command_exists "$cmd"; then
        VERIFY_MISSING+=("$cmd")
    fi
done

if [ ${#VERIFY_MISSING[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All requirements successfully installed and verified!${RESET}"
else
    echo -e "${RED}❌ Some requirements are still missing: ${VERIFY_MISSING[*]}${RESET}"
    echo "Please install them manually and ensure they are on your PATH."
    exit 1
fi
