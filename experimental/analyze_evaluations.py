import json
from collections import Counter

def analyze_evaluations():
    """Analyze shaberi3-evaluations.json focusing on len(line_data) != 4"""
    
    # Track different lengths of line_data
    length_counter = Counter()
    
    # Track unique content prefixes when len(line_data) != 4
    content_prefix_counter = Counter()
    
    with open("shaberi3-evaluations.json", "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                # Parse each line as JSON
                line_data = json.loads(line.strip())
                
                # Count the length of line_data
                if isinstance(line_data, list):
                    length = len(line_data)
                    length_counter[length] += 1
                    
                    # Only analyze line_data[1]["content"][:10] when length is NOT 4
                    if length != 4 and len(line_data) >= 2:
                        # Check if second element has 'content' key
                        if isinstance(line_data[1], dict) and "content" in line_data[1]:
                            content = line_data[1]["content"]
                            # Get first 10 characters
                            prefix = content[:10]
                            content_prefix_counter[prefix] += 1
                        
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}")
            except Exception as e:
                print(f"Error processing line {line_num}: {e}")
    
    # Display results
    print("=== Length Distribution of line_data ===")
    print(f"Total different lengths: {len(length_counter)}")
    for length, count in sorted(length_counter.items()):
        print(f"Length {length}: {count} occurrences")
    
    print(f"\n=== Analysis for len(line_data) != 4 ===")
    print(f"Total unique line_data[1]['content'][:10] prefixes: {len(content_prefix_counter)}")
    print("\nFrequency of each content prefix (first 10 chars):")
    for prefix, count in content_prefix_counter.most_common():
        print(f"\nCount: {count}")
        print(f"Prefix: '{prefix}'")

if __name__ == "__main__":
    analyze_evaluations()