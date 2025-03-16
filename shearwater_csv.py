#!/usr/bin/env python3
"""Convert Shearwater Cloud dive log data to CSV format with temperature data."""

import argparse
import csv
import json
import os
import sqlite3


# Conversion constants
FEET_PER_METER = 3.28084
SECONDS_PER_MINUTE = 60


def fahrenheit_to_celsius(fahrenheit):
    """Convert Fahrenheit to Celsius and round to 1 decimal place."""
    if fahrenheit is not None:
        return round((fahrenheit - 32) * 5/9, 1)
    return None


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Convert dive logs from Shearwater Cloud database export to CSV format.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python %(prog)s /path/to/divelog.db
  python %(prog)s /path/to/divelog.db -i  # Use imperial units (feet and °F)
  python %(prog)s /path/to/divelog.db -r  # Reverse sort (newest first)
  python %(prog)s /path/to/divelog.db -i -r -o my_dives.csv

First export your dive log database from Shearwater Cloud:
1. Open Shearwater Cloud
2. Go to File > Export > Export Database (*.db)
3. Run this script with the exported database file
'''
    )

    parser.add_argument(
        'database',
        help='Path to exported Shearwater Cloud database file (*.db)'
    )
    parser.add_argument(
        '-o', '--output',
        default='divelog.csv',
        help='Path for output CSV file (default: ./divelog.csv)'
    )
    parser.add_argument(
        '-i', '--imperial',
        action='store_true',
        help='Use imperial units (feet and °F) instead of metric (meters and °C)'
    )
    parser.add_argument(
        '-r', '--reverse',
        action='store_true',
        help='Reverse sort order (newest dives first)'
    )
    return parser.parse_args()


def get_calculated_values(db_path, dive_id):
    """Get calculated values for a dive from the log_data table.

    Note on units in Shearwater Cloud database:
    - AverageDepth is stored in feet
    - Temperature values are stored in Fahrenheit
    Returns raw values (avg_depth, min_temp, max_temp, avg_temp) tuple.
    Unit conversion is handled by the calling code.
    """
    try:
        # Open a separate connection for this query
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get the calculated values JSON for this dive
        cursor.execute("""
            SELECT calculated_values_from_samples
            FROM log_data
            WHERE log_id = ?
        """, (dive_id,))

        row = cursor.fetchone()
        if row and row[0]:
            data = json.loads(row[0])
            return (
                data.get('AverageDepth'),      # feet
                data.get('MinTemp'),           # fahrenheit
                data.get('MaxTemp'),           # fahrenheit
                data.get('AverageTemp')        # fahrenheit
            )

    except Exception as e:
        print(f"Error getting calculated values for dive {dive_id}: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

    return None, None, None, None


def main():
    args = parse_args()

    # Convert relative paths to absolute paths
    db_path = os.path.abspath(args.database)
    output_path = os.path.abspath(args.output)

    try:
        if not os.path.exists(db_path):
            print(f"Error: Database file '{db_path}' not found")
            exit(1)

        # Open the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        # Create the query joining dive_logs and dive_details
        sort_order = "DESC" if args.reverse else "ASC"
        query = f"""
            SELECT DISTINCT
                d.DiveNumber,
                d.DiveId,
                d.Location,
                d.Site,
                d.DiveDate,
                d.Depth,
                d.DiveLengthTime
            FROM dive_details d
            LEFT JOIN dive_logs l ON d.DiveId = l.diveId
            ORDER BY d.DiveDate {sort_order}
        """

        # Execute the query
        cursor = conn.cursor()
        results = cursor.execute(query).fetchall()

        if not results:
            print("No dive records found in the database!")
            exit(1)

        # Write to CSV
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write headers with appropriate units
            depth_unit = 'ft' if args.imperial else 'm'
            temp_unit = '°F' if args.imperial else '°C'
            headers = [
                '#', 'Location', 'Site', 'StartTime', 'Duration (min)',
                f'MaxDepth ({depth_unit})', f'AvgDepth ({depth_unit})',
                f'MinTemp ({temp_unit})', f'MaxTemp ({temp_unit})', f'AvgTemp ({temp_unit})'
            ]
            writer.writerow(headers)

            # Write data
            for row in results:
                # Get depth and convert if needed
                # Note: In Shearwater Cloud database:
                # - Maximum depth is stored in meters in dive_details.Depth
                # - Average depth is stored in feet in calculated_values_from_samples.AverageDepth
                max_depth = float(row['Depth']) if row['Depth'] is not None else 0.0
                if args.imperial:
                    max_depth = max_depth * FEET_PER_METER
                max_depth = round(max_depth, 1)

                # Convert dive length from seconds to minutes (rounded)
                minutes = round(float(row['DiveLengthTime']) / SECONDS_PER_MINUTE if row['DiveLengthTime'] else 0)

                # Use dive number from database, or '?' if not available
                dive_number = str(row['DiveNumber'] or '?').strip()

                # Get calculated values from log_data table (in feet and fahrenheit)
                avg_depth, min_temp, max_temp, avg_temp = get_calculated_values(db_path, row['DiveId'])

                # Convert average depth if needed (stored in feet)
                if avg_depth is not None:
                    avg_depth = round(avg_depth / FEET_PER_METER if not args.imperial else avg_depth, 1)

                # Convert temperatures if needed (stored in fahrenheit)
                if not args.imperial:
                    min_temp = fahrenheit_to_celsius(min_temp)
                    max_temp = fahrenheit_to_celsius(max_temp)
                    avg_temp = fahrenheit_to_celsius(avg_temp)
                else:
                    # Round imperial temperatures
                    min_temp = round(min_temp, 1) if min_temp is not None else None
                    max_temp = round(max_temp, 1) if max_temp is not None else None
                    avg_temp = round(avg_temp, 1) if avg_temp is not None else None

                writer.writerow([
                    dive_number,
                    row['Location'],
                    row['Site'],
                    row['DiveDate'],
                    minutes,
                    max_depth,
                    avg_depth,
                    min_temp,
                    max_temp,
                    avg_temp
                ])

        print(f"Export complete! File saved as: {output_path}")
        print(f"Number of dives exported: {len(results)}")

    except sqlite3.Error as e:
        print("Database error occurred:")
        print(e)
    except Exception as e:
        print("An error occurred:")
        print(e)
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    main()
