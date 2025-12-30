import random
import string

def generate_random_string(length=6000):
    """
    Generates a random string with various character types
    
    Args:
        length: desired string length (default: 6000)
    
    Returns:
        str: random string containing letters, digits, punctuation, spaces
    """
    
    # Character pools
    lowercase = string.ascii_lowercase  # a-z
    uppercase = string.ascii_uppercase  # A-Z
    digits = string.digits  # 0-9
    punctuation = '' #string.punctuation  # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    spaces = ''  # space, newline, tab
    special = ''  # accented characters
    symbols = ''  # special symbols
    
    # Combine all character types
    all_chars = lowercase + uppercase + digits + punctuation + spaces + special + symbols
    
    # Generate random string
    result = ''.join(random.choice(all_chars) for _ in range(length))
    
    return result


def analyze_string(s):
    """Display statistics about the generated string"""
    print("\n" + "="*70)
    print("STRING ANALYSIS")
    print("="*70)
    print(f"Total length: {len(s):,} characters")
    print(f"Unique characters: {len(set(s))}")
    print(f"\nCharacter type distribution:")
    
    lowercase_count = sum(1 for c in s if c.islower())
    uppercase_count = sum(1 for c in s if c.isupper())
    digit_count = sum(1 for c in s if c.isdigit())
    space_count = sum(1 for c in s if c.isspace())
    other_count = len(s) - lowercase_count - uppercase_count - digit_count - space_count
    
    print(f"   Lowercase letters: {lowercase_count:,} ({lowercase_count/len(s)*100:.1f}%)")
    print(f"   Uppercase letters: {uppercase_count:,} ({uppercase_count/len(s)*100:.1f}%)")
    print(f"   Digits: {digit_count:,} ({digit_count/len(s)*100:.1f}%)")
    print(f"   Spaces/whitespace: {space_count:,} ({space_count/len(s)*100:.1f}%)")
    print(f"   Other (punctuation, symbols): {other_count:,} ({other_count/len(s)*100:.1f}%)")
    
    print(f"\nFirst 200 characters:")
    print(repr(s[:200]))
    print(f"\nLast 200 characters:")
    print(repr(s[-200:]))
    print("="*70 + "\n")


def save_to_file(s, filename="random_string_6000.txt"):
    """Save string to file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(s)
    print(f"String saved to: {filename}")


if __name__ == "__main__":
    print("="*70)
    print("RANDOM STRING GENERATOR")
    print("="*70)
    
    # Generate 6000 character random string
    random_string = generate_random_string(6000)
    
    # Analyze it
    analyze_string(random_string)
    
    # Save to file
    save_to_file(random_string, "random_string_6000.txt")
    
    # Show how to use with compression scripts
    print("\n" + "="*70)
    print("NEXT STEPS - TEST COMPRESSION:")
    print("="*70)
    print("""
# Option 1: Use directly in code
from compress import create_freq_generator
from compress_zlib import create_zlib_generator

# Read the generated file
with open('random_string_6000.txt', 'r', encoding='utf-8') as f:
    test_string = f.read()

# Test frequency mapping compression
create_freq_generator(test_string, "generator_test_freq.py")

# Test zlib compression
create_zlib_generator(test_string, "generator_test_zlib.py")

# Compare results
from compress_zlib import compare_with_freq_mapping
compare_with_freq_mapping(test_string)
    """)
    
    print("\n" + "="*70)
    print("THE COMPLETE STRING IS STORED IN THE VARIABLE: random_string")
    print("="*70)
    print("\nYou can copy it from the file: random_string_6000.txt")
    print("Or use the variable directly in your compression tests")
