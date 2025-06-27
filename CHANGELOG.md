# Changelog

All notable changes to the Saturday Tatts Lotto Scraper project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-06-27

### Added
- **Automatic CSV Cleaning**: Parse script now automatically cleans corrupted CSV files before analysis
- **Manual CSV Cleaning Utility**: New `clean_csv.sh` script for manual data repair
- **Early Termination**: Scraper now stops after 5 consecutive skips to prevent infinite loops
- **Enhanced Error Prevention**: Built-in corruption detection and repair mechanisms
- **Updated Master Menu**: Menu now indicates auto-clean functionality in parse option

### Improved
- **Data Integrity**: Automatic removal of "Processed:" text and other corrupted lines
- **User Experience**: Clear feedback when cleaning occurs and how many lines were affected
- **Robustness**: System now handles CSV corruption gracefully without manual intervention
- **Documentation**: Updated README with comprehensive information about new features

### Technical Enhancements
- **Smart Cleaning Algorithm**: Only removes clearly corrupted lines, preserves all valid data
- **Performance**: Cleaning only occurs when needed, no impact on clean files
- **Cross-Platform**: All new features work across all supported operating systems

### Fixed
- **Syntax Errors**: Resolved issues caused by corrupted CSV data in parse script
- **Data Corruption**: Prevented future corruption through proper output redirection
- **Infinite Loops**: Early termination prevents scraper from running indefinitely

## [1.0.0] - 2025-06-26

### Added
- Initial release of Saturday Tatts Lotto Scraper
- Web scraping functionality for au.lottonumbers.com
- Statistical analysis and number recommendation system
- Cross-platform compatibility (macOS, Linux, BSD)
- Automated dependency management and installation
- Master script with menu-driven interface
- CSV data storage for winning and supplementary numbers
- Probability-based number recommendations with odds calculation
- Smart update system that skips existing data
- Comprehensive documentation and contributing guidelines

### Features
- **Scraping**: Fetches historical Saturday Tatts Lotto results (2020-2025)
- **Analysis**: Calculates individual number frequencies, odds, and percentages
- **Recommendations**: Generates 10 unique number combinations based on historical data
- **Diversity**: Ensures recommendations share no more than 2 numbers
- **Exclusion**: Never recommends exact past winning combinations
- **Efficiency**: Processes newest to oldest, skipping existing entries

### Technical Implementation
- Bash-based architecture with modular design
- HTML parsing using `pup` for reliable data extraction
- Cross-platform package manager detection (brew, apt, yum, dnf, pacman, etc.)
- Error handling and validation throughout
- POSIX-compliant shell scripting

### Documentation
- Comprehensive README with installation and usage instructions
- Contributing guidelines for open source collaboration
- MIT License for permissive use
- Project structure and architecture documentation
- Troubleshooting and FAQ sections

### Data Format
- **winning_numbers.csv**: Date and 6 main winning numbers
- **supplementary_numbers.csv**: Date and 2 supplementary numbers
- CSV format for easy data analysis and import

### Supported Systems
- macOS (Homebrew, MacPorts)
- Linux (apt, yum, dnf, pacman, zypper, emerge)
- FreeBSD (pkg, ports)
- Windows (WSL recommended)

## [Unreleased]

### Planned Features
- Additional lottery games support (Powerball, Oz Lotto)
- Advanced statistical analysis and trend detection
- Web interface for easier interaction
- API endpoints for programmatic access
- Machine learning-based predictions
- Real-time updates and notifications
- Database integration for better data management
- Mobile app support
- Configuration file for customization
- Logging system for debugging
- Unit and integration tests
- Performance optimizations for large datasets

### Potential Improvements
- Enhanced error recovery mechanisms
- More sophisticated recommendation algorithms
- Historical trend analysis
- Export functionality for different formats
- Batch processing capabilities
- Cloud deployment options
- Docker containerization
- CI/CD pipeline integration

---

## Version History Notes

### Version 1.1.0
- **Data Integrity Focus**: Major improvements to handle CSV corruption automatically
- **User Experience**: Better feedback and error prevention
- **Robustness**: System now handles edge cases gracefully
- **Documentation**: Comprehensive updates to reflect new features

### Version 1.0.0
- **Initial Release**: Complete working system for Saturday Tatts Lotto analysis
- **Stable**: All core functionality tested and working
- **Documented**: Comprehensive documentation and guides
- **Cross-Platform**: Tested on macOS and Linux systems
- **Open Source**: MIT License for community contribution

### Development Timeline
- **June 2025**: Initial development and testing
- **June 2025**: Cross-platform compatibility fixes
- **June 2025**: Documentation and repository setup
- **June 2025**: Public release (v1.0.0)
- **June 2025**: Data integrity improvements and auto-clean functionality (v1.1.0)

---

**Note**: This changelog will be updated with each new release. For detailed development history, see the Git commit log. 