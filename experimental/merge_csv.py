#!/usr/bin/env python3
"""
CSV merge script that handles files with different column orders.
Merges multiple CSV files by aligning columns based on header names.
"""

import csv
import argparse
import sys
from pathlib import Path
from collections import OrderedDict


def read_csv_file(file_path):
    """Read CSV file and return header and data rows."""
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
    return header, rows


def merge_csv_files(file_paths, output_path=None):
    """
    Merge CSV files with potentially different column orders.
    
    Args:
        file_paths: List of CSV file paths to merge
        output_path: Output file path (optional)
    
    Returns:
        Merged data as (header, rows)
    """
    if not file_paths:
        raise ValueError("No input files provided")
    
    # Read all CSV files
    all_data = []
    all_columns = set()
    
    for file_path in file_paths:
        try:
            header, rows = read_csv_file(file_path)
            print(f"Loaded {file_path}: {len(rows)} rows, columns: {header}")
            
            # Store data with column mapping
            data_dict = OrderedDict()
            for row in rows:
                if len(row) > 0:  # Skip empty rows
                    model_name = row[0]  # First column is model name
                    row_data = {}
                    for i, col_name in enumerate(header):
                        if i < len(row):
                            row_data[col_name] = row[i]
                        else:
                            row_data[col_name] = ""
                    data_dict[model_name] = row_data
            
            all_data.append(data_dict)
            all_columns.update(header)
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
            continue
    
    if not all_data:
        raise ValueError("No valid CSV files could be read")
    
    # Sort columns (first column is model name, rest alphabetically)
    first_column = next(iter(all_columns))  # Get first column name from first file
    other_columns = sorted([col for col in all_columns if col != first_column])
    merged_header = [first_column] + other_columns
    
    # Merge all data, avoiding duplicates (first occurrence wins)
    merged_data = OrderedDict()
    for data_dict in all_data:
        for model_name, row_data in data_dict.items():
            if model_name not in merged_data:
                merged_data[model_name] = row_data
    
    # Convert to rows format
    merged_rows = []
    for model_name, row_data in merged_data.items():
        row = []
        for col_name in merged_header:
            row.append(row_data.get(col_name, ""))
        merged_rows.append(row)
    
    print(f"Merged result: {len(merged_rows)} rows, columns: {merged_header}")
    
    # Save to file if output path is provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(merged_header)
            writer.writerows(merged_rows)
        print(f"Saved merged CSV to: {output_path}")
    
    return merged_header, merged_rows


def main():
    parser = argparse.ArgumentParser(description="Merge CSV files with different column orders")
    parser.add_argument("files", nargs="+", help="CSV files to merge")
    parser.add_argument("-o", "--output", help="Output CSV file path")
    
    args = parser.parse_args()
    
    # Validate input files
    file_paths = []
    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"Warning: File not found: {file_path}", file=sys.stderr)
            continue
        file_paths.append(str(path))
    
    if not file_paths:
        print("Error: No valid input files found", file=sys.stderr)
        sys.exit(1)
    
    try:
        header, rows = merge_csv_files(file_paths, args.output)
        
        # Print preview
        print("\nMerged CSV preview:")
        print(",".join(header))
        for i, row in enumerate(rows[:5]):
            print(",".join(row))
            if i >= 4:
                break
        
        if not args.output:
            print("\nFull merged CSV:")
            print(",".join(header))
            for row in rows:
                print(",".join(row))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()