# Saturday Tatts Lotto Scraper & Analyzer

A comprehensive bash-based tool for scraping Saturday Tatts Lotto results from Australia and providing statistical analysis for number recommendations.

## 🎯 Overview

This tool scrapes historical Saturday Tatts Lotto results from [au.lottonumbers.com](https://au.lottonumbers.com) and analyzes the data to provide statistically-based number recommendations. It's designed for educational and research purposes to understand lottery number patterns.

## 📊 Features

- **Automated Scraping**: Fetches historical Saturday Tatts Lotto results (1986-2025)
- **Smart Updates**: Only processes new draws, skipping existing data with early termination after 5 consecutive skips
- **Automatic Data Cleaning**: Built-in CSV corruption detection and repair
- **Statistical Analysis**: Calculates odds and probabilities for each number
- **Deterministic Recommendations**: Uses a weighted ranking engine to deliver 10 stable, history-aware combinations
- **Cross-Platform**: Works on macOS, Linux, and other Unix systems
- **Requirements Management**: Automatic detection and installation of dependencies
- **GitHub Pages Website**: Live statistics and project documentation

## 🏗️ Architecture

```
Lotto/
├── master_lotto.sh          # Main menu interface
├── scrape_lotto_results.sh  # Web scraper for lotto results
├── parse_and_recommend.sh   # Statistical analysis & recommendations (with auto-clean)
├── clean_csv.sh            # Manual CSV cleaning utility
├── requirements.sh          # Dependency checker/installer
├── generate_stats.sh        # Generate statistics for website
├── winning_numbers.csv      # Scraped winning numbers
├── supplementary_numbers.csv # Scraped supplementary numbers
├── index.html              # GitHub Pages website
├── assets/
│   ├── lotto_stats.json    # Live statistics data
│   └── favicon.svg         # Website favicon
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

The script will automatically check and install these requirements:
- `curl` - HTTP requests
- `pup` - HTML parsing
- `awk` - Text processing
- `grep` - Pattern matching
- `python3` - Deterministic combination ranking

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/JDsnyke/saturday-tatts-lotto-scraper.git
   cd saturday-tatts-lotto-scraper
   ```

2. **Make scripts executable:**
   ```bash
   chmod +x *.sh
   ```

3. **Run the master script:**
   ```bash
   ./master_lotto.sh
   ```

## 📖 Usage

### Master Menu Options

1. **Scrape Lotto Results** - Fetches and stores historical data
2. **Parse Data & Recommend Entries (with auto-clean)** - Analyzes data and provides recommendations
3. **Check & Install Requirements** - Ensures all dependencies are installed
4. **Exit** - Close the application

### Example Workflow

```bash
# Start the application
./master_lotto.sh

# Select option 3 to check requirements
# Select option 1 to scrape results
# Select option 2 to get recommendations (includes automatic CSV cleaning)
```

### Manual CSV Cleaning

If you need to manually clean corrupted CSV files:

```bash
./clean_csv.sh
```

This will remove any lines containing "Processed:" text and keep only valid data.

### Sample Output

```
No. | N1 | N2 | N3 | N4 | N5 | N6 | Avg Odds        | Avg %      | Main   | Supp
-----|----|----|----|----|----|----|---------------|-----------|-------|------
1   | 1  | 8  | 11 | 18 | 22 | 42 | 1 in 7          | 16.18%     | 1773   | 553
2   | 1  | 5  | 7  | 11 | 40 | 41 | 1 in 8          | 15.92%     | 1735   | 572
3   | 1  | 6  | 7  | 8  | 12 | 19 | 1 in 8          | 15.82%     | 1733   | 542
4   | 1  | 3  | 11 | 12 | 15 | 26 | 1 in 8          | 15.76%     | 1724   | 547
5   | 5  | 6  | 11 | 15 | 19 | 42 | 1 in 8          | 15.66%     | 1707   | 561
```

## 📊 Data Format

### CSV Structure

**winning_numbers.csv:**
```csv
Date,Winning Numbers
2025-06-21,7,14,22,28,33,41
2025-06-14,3,11,19,27,35,44
```

**supplementary_numbers.csv:**
```csv
Date,Supplementary Numbers
2025-06-21,5,17
2025-06-14,8,29
```

## 🎲 Saturday Tatts Lotto Rules

- **Game Type**: 6/45 Lotto
- **Draw Day**: Every Saturday
- **Numbers**: 6 main numbers (1-45) + 2 supplementary numbers
- **Jackpot**: Division 1 prize pool
- **Draw Time**: 8:30 PM AEST

## 🔧 Technical Details

### Algorithm

The recommendation system uses:
1. **Frequency Analysis**: Counts historical appearance of each number
2. **Weighted Scoring**: Blends main and supplementary frequencies with a 35% weighting boost for supplementary hits
3. **Deterministic Ranking**: Runs a Python 3 search to score combinations and avoid historical winners
4. **Diversity Filtering**: Ensures recommendations share ≤2 numbers before fallback broadening
5. **Auto-Cleaning**: Automatically removes corrupted data before analysis

### Statistical Methods

- **Individual Number Probability**: `frequency / total_draws`
- **Odds Calculation**: `total_draws / frequency`
- **Weighted Selection**: Prioritizes high-probability numbers while maintaining diversity

### Data Integrity

- **Automatic Cleaning**: Parse script automatically cleans CSV files before analysis
- **Corruption Detection**: Removes lines with "Processed:" text or invalid formats
- **Manual Cleaning**: `clean_csv.sh` utility for manual data repair
- **Early Termination**: Scraper stops after 5 consecutive skips to prevent infinite loops

## 🌐 Website & Live Statistics

Visit the [GitHub Pages website](https://jdsnyke.github.io/saturday-tatts-lotto-scraper/) for:
- Live lotto statistics
- Interactive data visualization
- Project documentation
- Usage examples

The website automatically updates with the latest data through GitHub Actions.

## 🔄 Updates

The scraper automatically:
- Processes draws from newest to oldest
- Skips existing data to avoid duplicates
- Terminates early after 5 consecutive skips
- Updates incrementally for efficiency
- Cleans corrupted data automatically

## 🌐 Supported Systems

- **macOS**: Homebrew, MacPorts
- **Linux**: apt, yum, dnf, pacman, zypper, emerge
- **FreeBSD**: pkg, ports
- **Windows**: Manual installation (WSL recommended)

## 📝 License

This project is for educational purposes. Please ensure compliance with local laws and regulations regarding lottery analysis and web scraping.

## ⚠️ Disclaimer

- This tool is for educational and research purposes only
- Past performance does not guarantee future results
- Lottery games are games of chance
- Please gamble responsibly
- The authors are not responsible for any financial losses

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues, questions, or contributions:
- Create an issue on GitHub

## 📈 Future Enhancements

- [ ] Additional lottery games support
- [ ] Advanced statistical analysis
- [ ] Web interface
- [ ] API endpoints
- [ ] Machine learning predictions
- [ ] Historical trend analysis

---

**Repository Owner**: [JDsnyke](https://github.com/JDsnyke)  
**Last Updated**: June 2025  
**Version**: 1.1.0 