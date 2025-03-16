# Shearwater CSV

Convert Shearwater Cloud dive log data to CSV format with data not included in Shearwater Cloud's CSV exports.

## Features

- Converts dive logs from Shearwater Cloud database export to CSV
- Includes temperatures and avg depth data not available in Shearwater Cloud's CSV exports
- Also includes standard data like location and site name, time, duration, and max depth
- Supports both metric (meters, °C) and imperial (feet, °F) units
- Sort dives chronologically (oldest or newest first)

## Installation

```bash
git clone https://github.com/derekspelledcorrectly/shearwater-csv.git
```

## Usage

1. Export your dive log database from Shearwater Cloud:
   - Open Shearwater Cloud
   - Go to File > Export > Export Database (\*.db)
   - Save the database file

2. Activate the Python environment:
   ```bash
   make activate  # This will copy the activation command to your clipboard
   # Paste and run the activation command
   ```

3. Run the script:
   ```bash
   python shearwater_csv.py /path/to/divelog.db [options]
   ```

Common options:
- `-i` - Use imperial units (feet and °F)
- `-r` - Reverse sort order (newest dives first)
- `-o filename.csv` - Specify output file (default: divelog.csv)

## Output Format

The CSV file contains the following columns:
- \# - Dive number
- Location - Dive location
- Site - Specific dive site
- StartTime - Date and time when the dive started
- Duration (min) - Dive duration in minutes
- MaxDepth (m/ft) - Maximum depth in meters or feet
- AvgDepth (m/ft) - Average depth in meters or feet
- MinTemp (°C/°F) - Minimum temperature
- MaxTemp (°C/°F) - Maximum temperature
- AvgTemp (°C/°F) - Average temperature

## Example Output

```csv
#,Location,Site,StartTime,Duration (min),MaxDepth (m),AvgDepth (m),MinTemp (°C),MaxTemp (°C),AvgTemp (°C)
256,Cozumel,Devil's Throat,2024-03-19 08:40:47,35,40.9,19.7,27.8,28.9,28.2
257,Bonaire,Hilma Hooker,2025-03-26 09:28:34,35,29.3,16.6,27.2,27.8,27.2
```

## Requirements

- Python 3.6 or later
- Shearwater Cloud app

## Notes

- All data is read directly from the exported Shearwater Cloud database
- The script is read-only and does not modify any dive log data

## License

MIT License

Copyright (c) 2025 Derek Shockey

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Author

Written by Derek Shockey using Goose, the Block AI assistant (https://block.github.io/goose/)
