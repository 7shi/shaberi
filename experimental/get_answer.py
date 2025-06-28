#!/usr/bin/env python3
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description='Extract ModelAnswer from JSON file')
    parser.add_argument('input_file', help='Input JSON file path')
    parser.add_argument('-l', '--line', type=int, required=True, help='Line number to extract (1-indexed)')
    parser.add_argument('-o', '--output', required=True, help='Output file path')
    
    args = parser.parse_args()
    
    with open(args.input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if args.line < 1 or args.line > len(lines):
        raise ValueError(f"Line {args.line} is out of range (1-{len(lines)})")
    
    # Get the specified line (convert to 0-indexed)
    line = lines[args.line - 1]
    
    # Parse JSON
    data = json.loads(line)
    
    # Extract ModelAnswer
    model_answer = data.get('ModelAnswer', '')
    
    # Write to output file
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(model_answer)

if __name__ == '__main__':
    main()