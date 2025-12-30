# generator_maker.py - Frequency Mapping Compression

from collections import Counter

def create_freq_generator(original_string="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", output_file="generator_string.py"):
    """
    Analyzes a string and generates a Python script that regenerates it
    using frequency mapping compression
    
    Args:
        original_string: the string to compress (can be very long)
        output_file: name of generated script (default: generator_string.py)
    """
    
    print("="*70)
    print("ANALYZING STRING...")
    print("="*70 + "\n")
    
    # STEP 1: Create alphabet (unique sorted characters)
    unique_chars = ''.join(sorted(set(original_string)))
    indices = [unique_chars.index(c) for c in original_string]
    
    print(f"Basic information:")
    print(f"   String length: {len(original_string):,} characters")
    print(f"   Unique characters: {len(unique_chars)}")
    print(f"   Alphabet: {unique_chars[:50]}{'...' if len(unique_chars) > 50 else ''}")
    print()
    
    # STEP 2: Analyze index frequency
    freq = Counter(indices)
    print(f"Top 15 most frequent indices:")
    for idx, count in freq.most_common(15):
        percent = count / len(indices) * 100
        print(f"   Index {idx:3d} ('{unique_chars[idx]}'): {count:5,} occurrences ({percent:5.2f}%)")
    print()
    
    # STEP 3: Create mapping for most frequent indices
    # Use a-z (26) + A-Z (26) = 52 symbols for most frequent
    top_freq = [idx for idx, _ in freq.most_common(52)]
    
    symbols = []
    symbols.extend([chr(97 + i) for i in range(26)])  # a-z
    symbols.extend([chr(65 + i) for i in range(26)])  # A-Z
    
    mapping = {idx: symbols[i] for i, idx in enumerate(top_freq)}
    reverse_map = {v: k for k, v in mapping.items()}
    
    # Calculate coverage
    count_top52 = sum(count for idx, count in freq.items() if idx in mapping)
    coverage = count_top52 / len(indices) * 100
    
    print(f"Mapping created:")
    print(f"   Mapped indices: {len(mapping)} (most frequent)")
    print(f"   Coverage: {coverage:.1f}% of all data")
    print(f"   Symbols used: a-z, A-Z")
    print()
    
    # STEP 4: Compress data
    compressed_parts = []
    for idx in indices:
        if idx in mapping:
            # Frequent index -> simple letter (1 char)
            compressed_parts.append(mapping[idx])
        else:
            # Rare index -> format |number|
            compressed_parts.append(f"|{idx}|")
    
    compressed_str = ''.join(compressed_parts)
    
    # STEP 5: Calculate statistics
    original_size = len(str(indices))  # length as Python list
    compressed_size = len(compressed_str)
    savings = (1 - compressed_size / original_size) * 100
    
    print(f"COMPRESSION RESULTS:")
    print(f"   Original length (Python list): {original_size:,} characters")
    print(f"   Compressed length (string): {compressed_size:,} characters")
    print(f"   Savings: {savings:.1f}%")
    print()
    
    if savings > 55:
        print(f"   EXCELLENT! Very efficient compression")
    elif savings > 35:
        print(f"   GOOD! Decent compression")
    else:
        print(f"   WARNING: Poor compression - string is very uniform")
    print()
    
    # STEP 6: Generate Python script with CORRECTED decoding logic
    generated_code = f'''"""
String generator with Frequency Mapping Compression
Auto-generated by generator_maker.py

Statistics:
- Original string length: {len(original_string):,} characters
- Unique characters: {len(unique_chars)}
- Savings: {savings:.1f}%
- Top-52 coverage: {coverage:.1f}%
"""

# Alphabet (unique sorted characters) - GLOBAL
ALPHABET = "{unique_chars}"

# Reverse mapping: simple letter -> index in alphabet - GLOBAL
# a-z, A-Z map the 52 most frequent indices
FREQ_MAP = {reverse_map}

# Compressed data - GLOBAL
# - Simple letters (a-z, A-Z) = frequent indices
# - Format |N| = rare indices
DATA = """{compressed_str}"""


def generate_string():
    """
    Regenerates the original string from compressed data
    
    Returns:
        str: The complete original string
    """
    
    # Decode: convert compressed string back to indices
    indices = []
    i = 0
    while i < len(DATA):
        if DATA[i] == '|':
            # Format |number| for rare indices
            j = i + 1
            while j < len(DATA) and DATA[j] != '|':
                j += 1
            
            num_str = DATA[i+1:j]
            if num_str:  # check not empty
                indices.append(int(num_str))
            
            # Position AFTER second delimiter
            i = j + 1
        else:
            # Simple letter = frequent index
            if DATA[i] in FREQ_MAP:
                indices.append(FREQ_MAP[DATA[i]])
            i += 1
    
    # Reconstruct string from alphabet + indices
    return ''.join(ALPHABET[idx] for idx in indices)


def verify_string(expected_string=None):
    """
    Verifies if generated string is correct
    
    Args:
        expected_string: original string for comparison (optional)
    
    Returns:
        bool or str: True/False if expected_string given, otherwise generated string
    """
    generated = generate_string()
    
    print(f"Generated string length: {{len(generated):,}}")
    print(f"First 100 characters: {{generated[:100]}}")
    
    if expected_string:
        match = generated == expected_string
        print(f"Match with original: {{match}}")
        if not match:
            # Find first difference
            for i, (a, b) in enumerate(zip(generated, expected_string)):
                if a != b:
                    print(f"First difference at position {{i}}: '{{a}}' vs '{{b}}'")
                    break
        return match
    
    return generated


def info():
    """Display compression information"""
    print("="*60)
    print("COMPRESSION INFO")
    print("="*60)
    print(f"Original string length: {len(original_string):,} characters")
    print(f"Unique characters in alphabet: {{len(ALPHABET)}}")
    print(f"Mapped indices (top frequent): {{len(FREQ_MAP)}}")
    print(f"Top-52 coverage: {coverage:.1f}%")
    print(f"Compressed data size: {{len(DATA)}} characters")
    print(f"Savings vs Python list: {savings:.1f}%")
    print("="*60)


if __name__ == "__main__":
    print("="*60)
    print("STRING GENERATOR")
    print("="*60)
    print()
    
    s = generate_string()
    print(f"String generated successfully!")
    print(f"   Length: {{len(s):,}} characters")
    print()
    print("="*60)
    print("COMPLETE STRING:")
    print("="*60)
    print(s)
    print()
    print("="*60)
    print(f"First 100 characters: {{s[:100]}}")
    print(f"Last 100 characters: {{s[-100:]}}")
    print()
    
    info()
'''
    
    # STEP 7: Save generated script
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(generated_code)
    
    print("="*70)
    print(f"SCRIPT GENERATED: {output_file}")
    print("="*70)
    print(f"\nNext steps:")
    print(f"   1. Run directly: python {output_file}")
    print(f"   2. Or import: from {output_file[:-3]} import generate_string")
    print(f"   3. Use: s = generate_string()")
    print()


def estimate_compression(original_string):
    """
    Estimates savings without generating script (quick analysis)
    
    Args:
        original_string: string to analyze
    
    Returns:
        float: estimated savings percentage
    """
    unique_chars = ''.join(sorted(set(original_string)))
    indices = [unique_chars.index(c) for c in original_string]
    
    freq = Counter(indices)
    top_52 = [idx for idx, _ in freq.most_common(52)]
    
    # Calculate coverage
    count_top52 = sum(count for idx, count in freq.items() if idx in top_52)
    coverage = count_top52 / len(indices) * 100
    
    # Estimate sizes
    list_length = len(str(indices))
    
    chars_frequent = int(len(indices) * (coverage/100) * 1)
    chars_rare = int(len(indices) * ((100-coverage)/100) * 4)
    total_compressed = chars_frequent + chars_rare
    
    savings = (1 - total_compressed / list_length) * 100
    
    print(f"QUICK ESTIMATE:")
    print(f"   String length: {len(original_string):,}")
    print(f"   Unique characters: {len(unique_chars)}")
    print(f"   Top 52 covers: {coverage:.1f}% of data")
    print(f"   Python list: {list_length:,} characters")
    print(f"   Estimated compressed: {total_compressed:,} characters")
    print(f"   Estimated savings: {savings:.1f}%")
    
    return savings


# ============================================
# USAGE EXAMPLES
# ============================================

if __name__ == "__main__":
    print("\n")
    print("="*70)
    print("GENERATOR CREATOR - Frequency Mapping Compression")
    print("="*70)
    print("\n")
    
    # Example with short string
    example_str = "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"
    
    print(f"Example with short string ({len(example_str)} characters):\n")
    create_freq_generator(example_str, "generator_string.py")
    
    print("\n" + "="*70)
    print("FOR YOUR 30,000 CHARACTER STRING:")
    print("="*70)
    print("""
# Option 1: String directly in code
my_string = "your_complete_30000_character_string..."
create_freq_generator(my_string, "generator_final.py")

# Option 2: Read from file
with open('string_30000.txt', 'r', encoding='utf-8') as f:
    long_string = f.read()
create_freq_generator(long_string, "generator_final.py")

# Option 3: Only estimate (without generating)
estimate_compression(long_string)
    """)