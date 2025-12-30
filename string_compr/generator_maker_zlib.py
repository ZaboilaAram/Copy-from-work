# generator_maker_zlib.py - Compression with zlib

import zlib
import base64
import math

def create_zlib_generator(original_string="ps7GMhKFzsQhiQqo84UtpfPTPOcwKZpQDd432PHrb3YqdgRmp2LcIscfY67owF2xqmo3ZGuXvloRsludmlYSs4KKlIl1cBeldyNBV7L5bc1OBbVZy0769PqRf3Ft4ZoFb5LZ9d6o5ybfea8K44pG9crhVVlFzIVV5RhlBTYSAOXZLhYEtVshiqPc2let6ZGyPps2Z1rCNoxumoRYOcuLnYtOgRz8CguUZdYk7EWq3VhqHydlQRrSE7WCpxFx76PBIH6Rv0x6UModudU88DYFITWn7Wt6jNgBGpstTfnAabVHDzJoVQLZI8zFUA9rE6iK87wEWJWkDaO8tzbl0Nwu9YUeb0eEdHhVtaIksmymDPL79pvoK3YHEf2mmHN7X19o7ONklB4zdQSKYo7Re6avlv9BkNQxA2kIasIILVXC4sgPlC6Kr7ahgr0pst6hMNC8STQBcXo8gZQBfkNjpzBIfncz3RCQbeNwsiiC7Cji4HOEitMGMvEYrpLrledthmyLUgfE0dm8wrN8vhjsbZPRyvkAKKPYxqXWLYFil2HPu3aHQbEyQDBSq8sQI9wSDpZpXaydNkTUA9zHI6I3zNLTakJPputBkiI2lX1G3AePmbpouJpoyt96PA3aH7LBifYzBocErkz9FoU1QDVNuhbihwRE6PqTwKJezhHGBFIg0GXMU2qri80vtmRxQbcZw3KGUjF0yyClXersizxT2JnXNyZt1OPtYqCidKL7idSpeueDlU02EYYOLtM4Y2YJw1ncUfhhMu6p463Gi9l7tpyd8EICeYsuX6csDfI5ituaUvIFaZY39t4KHiXCOzOzmHCls6TodUNj44FOIjBcbbemL87iG47FIRkrdZ70hFu1skwYP5sHFtSGgz3y3Z7vPHW4rXlAMHfMnLMSoifYih4ItZgsB1NMOY2zmGVZeIXYaH88iYsIZXtl4Fwxde0TJOKgTX1LZZGtRNMKA5jGwSNofJkD74IwRiBDfECHGvH4d0u3ZFGcSybwT1sPhu1tx5gv5yrxTvBYgSSHyUltTfcEZZxNHlm4qwbNr9NTBmQ67In38cRxWlOfdXun4gZ7IBvua80abNe5pCp4T9GXOfNz0sSFtdo40KCV7rNpxjjCzFJuFQEgKGoH95eS2TGL4LIe70lxyHa7BlT5UeYN4eELjRGNjbh1n2am5q9qRJoQO3KYSqOS3FCAHqK3uvWiF5MN49r3yCGb7Xi6cXwGjpcvR40jZgv4oIkOWE7yVr6lppp8XZG57rFemlDB50aVyQYXSalT6tkCT3RlvfNdDSD4Fh46eX5Oq7jbAigBT4glAAbnMBOMzE6wRxknO3z52nbThOvszU26F4k7sXYuAsXIeMM2jbsyAn3A4byTtizAsrMFEnQFSrz8h8yjecqHgqhHNesb6se6J1nD54Z1w0ZE1jnW68wHdmKcGpSyfhZrOtOlNwp2F6DEwStuidhGyFGqSnoIHGBS3CTQDmdiE8PBAvd6JcCrlXSP3HjizI8GGCTAd6Ov1FWldoi5xOROlNXr32qkcy3xgKr2UQp7574E5HrjZ1QrBZPHCoJy1AabpmW5dH9LuNzjsOTTIseQaTHnezbM053bQ1PQ2SA9ykwNWZIJcXM3JNgJR2HYFqKYr0ycrV22YCyx4l7CTuskergKUzS1FSqLns3Qpg89h2MsvbVAv8fs21FskKZYvNGlhzcuyby49rdgAzRs42u3WxNbEhbVhr4u8ZPCAW7oBvvPvKsSoMtilxnGhQhta618DuBD8xVPvohPaDgv3GhyuNTW6txLrCoOB8PSs2Cr0JnhS6L69jER3Yvh9a9gRizxVxJQxm0sSzsu5PtpPq1VLMJ6FAsFq3fMlOW4r9EneoWgmUiEsmoNNmKKc84yirdtlVLPR54KBxlWWiQXQg1Cep4mqMTSyxoq7ELdG6kYEPogLcHl0iN1EPT419oU3CDouVRMOYPZZ2ETGNBH2okIZ2ImGe3rNVIm8qMEZHrSsrWqXh2v62TxwudO5GqAWuw2NswzjyjebfYNbOEShrfvM4y2pPedw5ionSDnYTmE5lVuaLuwQ4AbT8Plt1QZBAHZvpv8UlVG3zXq5fXS8bHYccD9fJNp8cGQsdgd7u5YWDe00AkOlpEAOzHKMr6LQuTUmpEJ4Y5jBAMAPuvYtv9rN9TwbEpFGU2LS9VlXtOoNJgDa1l4JxIpQfaxXy12DkZvY2r8iweXMUU2QFrmCTp9OlevnzgthNoT2IFXLfNfs3t65SfcW99nbx1g1bkHUzi6y2uvydcuGtkegGUz5z946IQ66aXADcD0Hj02FTWNqslVne8X6IKjtHkwRJnVFXQ9rz8gkI4G6Ky6tloHO2jhtPSa9DqDTBLGWLiFrREmQH4AzBN79RKdGyYy5jXYYCz6JEmNOUq0pWNJRDQeGeZZ4WQn5OxELgMDGhlR6au3Gkff1EyCPnDRRbOku6keCqaChLiLrwy68aPen3sy0Y9hVWwgMoLUy00s5yosfMKCptWJrE5EUQQKZ6IcDjkWfgaL3rqLzEwlmcLqLT6UzRH4RjPkLgIIYGTkpnyEH66ZQIxeGpFiBBuQvZmWLVK6yTTC0amkylz1oFTMbMbNDarqxRl5Jx6jJkhcIgNNlLkp71g3cnsuxv2EugLUEXdvfNyLNxpDIIYzdVoqta9SsSkF9kw5AvI00Iotxy0zJ10zUxyKiKBpJdf2QVXjvfxO4hNTCJFI8PLrP4QqZlos0CbLCn1m01Nho1U4DLR24aA9fRIImSal8RYBfvURClBGD5N6ErU9IgfPOmX7dyP749Bc2ygE1Eiwho4uylpqpuwdpPP8ri7Vf3uUmqU8PO0YafckRXNqTiOSI0wKBa4qWV7f92XGdRW2F6DBStbPoAfF1oYJzsvRBekmoIy11hPjl63QdLY0ZCnCLnuD0MeUXiIBzA6jsZNbBk4dd5ZxtxNlHiMkB5D467BpVQs3aETL8Yl8eHZIQrIkg4JcrjgvIIgM1XZyPDY7HNXv5ePKvvc270C2auo6OA7FJgLVCKtVyOgz1VL1Vcrr56T4VTWWRi6rgW4A78JVvamqOy9mB34Zf7rYVEBh8d6SvDzFUODc8VCF5eiMZGoLUjZzUD4jCzqDT4RY4g8z8NUcpb628QP3pfdoDkslPvZvTiOrh9u6gu7Neec7JVeDDOWIQGVqFiFVioiCWdczK28V1mqtWHTJxQDO1wpEuV0kTWSlfNjdZriGbqa9f2g9lRAgG1Bj9cMz6zEeXSrpLc2JpGvHsAjnva5ZGoBP1ww2Emn8IHzJ5jUSuNEQHM68uXycMtoqEWP29ktjQIChnTJqgF02jLWGZ6e1o22A5doq6wAb951NCPJmEWQAvnx0YvzXo60a8bBtKc8CdUvhNcFl1auNrIjo5iPAajdWcvJQvlO2CJGE4qxfsrwG65WOu2Z9DqYrWc8W6sXnzehfnCoW2kjf8r21GGJRxCnO5KZgm8SwgdinZTsnMoRbnr3zTghLHA6KIYLXpBdNnfwN1q5xY6H1OLsOH6PYap5yuGesq3lWn4AOkE45gvVHXBFu6AlCFqV3HtnWF6sCbNLhQWoeJwGTRhd3PAPF6cDYEk3FdN549EldTBr2Fd5jVNZ51D9T8SFfpxyVnhqt2uTtUutdnmQz67Fp7Rdu7icGobOFqfVWh2ubd8cVbO2AgVKxtWK8InH9qGeLLQRqbaU1KhG3aZLfxVmT7Q1DypUuC1Y7tm97eMJVlRlU5UyagJQ467bTiW5jerNFFwMRqg2M8ivS317zxxckjQIm6OVWBzatojal3zHYVcXabnbsJRdPp4nfPNgQ1pVeKQrvrxwRA5IzgcxmovRkh3wSDFowAuSg8Go7OgMUu4A68HpWDFpYRB46AOM22rjQoxf6y17nHaa6oEs0mIJu9y5XXYrpWovgQ6ZHMra5NO30ldwwWQUgKRNpuPcUxD4sYNLoqlEheibSDVTBSEyYjn1c6nuM1aG3R4t8dDKT9FWnVItDiyfBSxjTc7Bigen3eZGdF8uv0jCea0P2yKWkKeOSKTC0JmDFNgIcLGS6Elg791BJtSV88njOjMimHFlu2BPeOr8ZDybmGlmEPR3RupaW8GJ14D29gsK2nKyQ5kXfuOvZa4zDEuE0J6comNMHjap0LfEzTg5WItEtdXKTQwbJ7YnkLt0H5Wwumg8rw8qthlkJdLmbWhgJy2GFu0bB71quVREAYxMO2nIANRZorEw8Gxfh6jmjcrmKUuvXbZsPgj0o3i5dZzeAQdUG3j2vwLMHveB9BvlPihZzzfWRAQ3djE9g3ixXR8ICrroYgTHOvsz16dtCcK1LRwoggWME8YIofIzzOzJAviEY5Kvo56Hdtb37rgw3isooNWFVsq1CKYq3va3fuAY4BTQVSrSgHozhitSVb2stXulqkIMfXXn1kRMZ8UhwJLhmELp9734CMoKsaph01dHPgHM1ro7zkv5aSQQfDvpypNHMSaCiC5rAqQ0wTXSMGZAyl0JrqzMhhDWzrlNy63MYxOR0bRyJVdRwy8tacZ5CqhEJrTZCSPmFIRXTTaAOLZx0GcfkAqfFkVkAKkGU4eTeEf7N7hWe2SrHmH4bb9BIfYWf1LfYcJh3lxoXbKSJKOlHHVLnIwj48MghRtKd9zMKTBTUwxVkjvoch35qwCpQlYjfWGmhD5Jrt3TEJvV41w1LGJda0rIQLpHuPAkui10X4lDghiJMoQJeeAZpfeuxuJvn6RcNkrrakFoEPjOijFjAy0p5jmyT9RjAHgSred9QnCZoyHqUudG4DzEn4l79Kbv9fw1Cb2sZQiqCiGphpsGKgxZirjlmuScnjWkrE9z5LxO7FSRxVXpkuZMczVmwMnZOijKmJcOMrCSTeilCpPPiTI7U15liKDR40Vw5U7CYmyBzbSMNuaBfmFrIWpA4ChK97AXOxr8e0bflP50pNt30SG0vXpqyEqK23q8ciGHaBgTE1Vgmpe8vIqjyKAmr2pOw6CTxbj2fbRNkn7EJrRqTHAbMbgmyJZqVm0ShUeh4B2BOcFJnAEfRDQbNTT0U9zHpAkj1QhuneVGKr4tRyDR39YbtUWuQiLeISPwXcyQcKOct08MF0nAQeg4sec12llNxEo9EDNoszGcvS7LJnBzZnd9RjWQxn9n0MwXFJqmATiOyzr444Fm53b5hWTPVsgIxSS125mzXeOUwgmttlHTgpR9QrGYD21mvwrO0XvD6qu0S52QrMTWrfKipsdwdWi93E0MlUmaMPaxcAFLtvGBgc2gwgyNjDvMHft3L3E3tYVd1uSpf3zQzixpzmTPWE6Owod27J9IRYPmORMmr5R0ZFJATSNTTe7wl1scpcufVUIUz5EBubxZ4b35eQQqzEHokLndThfNlUaFKTjvajroQdmDjMP94xsJSQKAZp9l2F7PLveymXIzmkqZbR5oPk2Rdi2MfjoRJJlllDX8j7I7ZVRW2N10ygpEEQuLDSI3a8LN73GBVYOlAii3SVMMynIWHMPOgNSnHqxDeKoEWinXDsYPmghnfBoCalHfU43TsFccGsAQo2otzqognrAl983k6H4Hwu3lqkRwf7i0ZV64iqqRpAJzL31zCmuVz5fkFQ53dF8HVlP0bLD3ZDhCeU8MRhxGmWBkmYsde0rwoJH6qnwOBe1ChPY6qhHSjuGoeCObsEVBxoF5jOdPAAlBkrRPnumAZMc43GXkHksyKXUbjUBjs6iDLpepiZDdwNAEEeaVwfcdLZX6Dt0W7GvApFYGZUp04quoIhonoNTvQJuzXjf3qz1IG4jH1uxnkWpHQp72AfybLhS7O88HjLCHjOwWqAD3qBMoppYfSVk2tVceEx41MhvknwAn85vG7WUbBB6621WLNNJH4DgGM4iP0hsjEaVSuOMbQgSdnHpzbodBCo6Ty4FO2vkOfFnFRNF2vv7jE1D2WGURhh6AAeccyjoRU4Y7zhyimJocIiuJtJEdDrsB4Zi24FkjyMid9", output_file="generator_string_zlib.py"):
    """
    Analyzes a string and generates a Python script that regenerates it
    using zlib compression (DEFLATE algorithm)
    
    Args:
        original_string: the string to compress (can be very long)
        output_file: name of generated script (default: generator_string_zlib.py)
    """
    
    print("="*70)
    print("ANALYZING STRING WITH ZLIB COMPRESSION...")
    print("="*70 + "\n")
    
    # Information about original string
    print(f"Basic information:")
    print(f"   String length: {len(original_string):,} characters")
    print(f"   Raw size: {len(original_string.encode('utf-8')):,} bytes")
    
    unique_chars = len(set(original_string))
    print(f"   Unique characters: {unique_chars}")
    print()
    
    # Test different compression levels
    print(f"Testing zlib compression levels:")
    
    levels = {}
    for level in range(0, 10):
        compressed = zlib.compress(original_string.encode('utf-8'), level=level)
        levels[level] = len(compressed)
        
        if level == 0:
            print(f"   Level {level} (no compression): {len(compressed):,} bytes")
        elif level == 1:
            print(f"   Level {level} (fast):           {len(compressed):,} bytes")
        elif level == 6:
            print(f"   Level {level} (default):        {len(compressed):,} bytes")
        elif level == 9:
            print(f"   Level {level} (maximum):        {len(compressed):,} bytes *")
    
    print()
    
    # Use maximum level (9) for optimal compression
    compressed_bytes = zlib.compress(original_string.encode('utf-8'), level=9)
    compressed_b64 = base64.b64encode(compressed_bytes).decode('ascii')
    
    # Calculate statistics
    original_bytes = len(original_string.encode('utf-8'))
    compressed_size = len(compressed_bytes)
    base64_size = len(compressed_b64)
    
    ratio_compressed = (1 - compressed_size / original_bytes) * 100
    ratio_base64 = (1 - base64_size / original_bytes) * 100
    
    print(f"COMPRESSION RESULTS (level 9):")
    print(f"   Original (UTF-8):       {original_bytes:>10,} bytes")
    print(f"   Compressed (zlib):      {compressed_size:>10,} bytes ({compressed_size/original_bytes*100:5.1f}%)")
    print(f"   Base64 encoded:         {base64_size:>10,} bytes ({base64_size/original_bytes*100:5.1f}%)")
    print()
    print(f"   Savings (zlib):         {ratio_compressed:>10.1f}%")
    print(f"   Savings (base64):       {ratio_base64:>10.1f}%")
    print()
    
    if ratio_compressed > 70:
        print(f"   EXCELLENT! Extraordinary compression")
    elif ratio_compressed > 50:
        print(f"   VERY GOOD! Efficient compression")
    elif ratio_compressed > 30:
        print(f"   GOOD! Decent compression")
    elif ratio_compressed > 0:
        print(f"   WARNING: Poor compression - string is quite random")
    else:
        print(f"   ERROR: Compression increases size! String is very random/short")
    print()
    
    # Information about patterns (why compression works well/poorly)
    from collections import Counter
    
    # Analyze repetitions
    bigrams = [original_string[i:i+2] for i in range(len(original_string)-1)]
    bigram_freq = Counter(bigrams)
    top_bigram = bigram_freq.most_common(1)[0] if bigram_freq else (None, 0)
    
    trigrams = [original_string[i:i+3] for i in range(len(original_string)-2)]
    trigram_freq = Counter(trigrams)
    top_trigram = trigram_freq.most_common(1)[0] if trigram_freq else (None, 0)
    
    print(f"Pattern analysis (why compression works):")
    print(f"   Most frequent bigram: '{top_bigram[0]}' ({top_bigram[1]} occurrences)")
    print(f"   Most frequent trigram: '{top_trigram[0]}' ({top_trigram[1]} occurrences)")
    
    # Shannon entropy (correct calculation)
    char_freq = Counter(original_string)
    entropy = 0.0
    for count in char_freq.values():
        prob = count / len(original_string)
        if prob > 0:
            entropy -= prob * math.log2(prob)
    
    print(f"   Shannon entropy: {entropy:.2f} bits/char (max: {math.log2(len(char_freq)):.2f})")
    print(f"   Complexity: {'High (hard to compress)' if entropy > 4 else 'Moderate (compressible)'}")
    print()
    
    # Generate Python script
    generated_code = f'''"""
String generator with zlib compression (DEFLATE algorithm)
Auto-generated by generator_maker_zlib.py

Compression statistics:
- Original string length: {len(original_string):,} characters ({original_bytes:,} bytes)
- Compressed with zlib: {compressed_size:,} bytes
- Savings: {ratio_compressed:.1f}%
- Compression level: 9 (maximum)

zlib uses the DEFLATE algorithm which combines:
- LZ77: Detects repeated sequences
- Huffman coding: Optimal symbol encoding
"""

import zlib
import base64


# Data compressed with zlib (level 9) and encoded in base64
# Base64 is necessary to store binary data as string in Python code
COMPRESSED_DATA = """{compressed_b64}"""

# Statistics (for info() function)
ORIGINAL_LENGTH = {len(original_string)}
ORIGINAL_BYTES = {original_bytes}
COMPRESSED_SIZE = {compressed_size}
BASE64_SIZE = {base64_size}
COMPRESSION_RATIO = {compressed_size/original_bytes*100:.1f}
SAVINGS = {ratio_compressed:.1f}


def generate_string():
    """
    Regenerates the original string from zlib compressed data
    
    Returns:
        str: The complete original string, decompressed
    """
    
    # Step 1: Decode from base64 to bytes
    compressed_bytes = base64.b64decode(COMPRESSED_DATA)
    
    # Step 2: Decompress with zlib
    decompressed_bytes = zlib.decompress(compressed_bytes)
    
    # Step 3: Decode from bytes to UTF-8 string
    original_string = decompressed_bytes.decode('utf-8')
    
    return original_string


def info():
    """Display compression information"""
    print("="*60)
    print("ZLIB COMPRESSION INFO")
    print("="*60)
    print(f"Original string length: {{ORIGINAL_LENGTH:,}} characters")
    print(f"Original size: {{ORIGINAL_BYTES:,}} bytes")
    print(f"Compressed size: {{COMPRESSED_SIZE:,}} bytes")
    print(f"Base64 size: {{BASE64_SIZE:,}} bytes")
    print(f"Compression ratio: {{COMPRESSION_RATIO}}%")
    print(f"Savings: {{SAVINGS}}%")
    print(f"zlib compression level: 9 (maximum)")
    print("="*60)


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
            print(f"ERROR: String does not match!")
            # Find first difference
            min_len = min(len(generated), len(expected_string))
            for i in range(min_len):
                if generated[i] != expected_string[i]:
                    print(f"First difference at position {{i}}:")
                    print(f"  Generated:  '{{generated[i]}}'")
                    print(f"  Expected: '{{expected_string[i]}}'")
                    break
            
            if len(generated) != len(expected_string):
                print(f"Different lengths: {{len(generated)}} vs {{len(expected_string)}}")
        
        return match
    
    return generated


if __name__ == "__main__":
    print("="*60)
    print("STRING GENERATOR (ZLIB COMPRESSION)")
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
    
    # Save generated script
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


def compare_with_freq_mapping(original_string):
    """
    Compares zlib compression with frequency mapping
    To see real gain
    """
    from collections import Counter
    
    print("\n" + "="*70)
    print("COMPARISON: zlib vs Frequency Mapping")
    print("="*70 + "\n")
    
    # zlib
    compressed_zlib = zlib.compress(original_string.encode('utf-8'), level=9)
    zlib_b64 = base64.b64encode(compressed_zlib).decode('ascii')
    
    # Frequency mapping (simulation)
    unique_chars = ''.join(sorted(set(original_string)))
    indices = [unique_chars.index(c) for c in original_string]
    
    freq = Counter(indices)
    top_52 = [idx for idx, _ in freq.most_common(52)]
    
    symbols = [chr(97+i) for i in range(26)] + [chr(65+i) for i in range(26)]
    mapping = {idx: symbols[i] for i, idx in enumerate(top_52)}
    
    compressed_freq = []
    for idx in indices:
        if idx in mapping:
            compressed_freq.append(mapping[idx])
        else:
            compressed_freq.append(f"|{idx}|")
    
    freq_string = ''.join(compressed_freq)
    freq_total = len(freq_string) + len(unique_chars) + 500  # overhead
    
    original_size = len(original_string)
    
    print(f"Sizes:")
    print(f"   Original:              {original_size:>10,} bytes (100.0%)")
    print(f"   Frequency Mapping:     {freq_total:>10,} bytes ({freq_total/original_size*100:5.1f}%)")
    print(f"   zlib + base64:         {len(zlib_b64):>10,} bytes ({len(zlib_b64)/original_size*100:5.1f}%)")
    print(f"   zlib raw:              {len(compressed_zlib):>10,} bytes ({len(compressed_zlib)/original_size*100:5.1f}%)")
    print()
    
    if len(compressed_zlib) < freq_total:
        diff = freq_total - len(compressed_zlib)
        percent = (1 - len(compressed_zlib)/freq_total) * 100
        print(f"WINNER: zlib")
        print(f"   Smaller by: {diff:,} bytes ({percent:.1f}% more efficient)")
    else:
        diff = len(compressed_zlib) - freq_total
        percent = (1 - freq_total/len(compressed_zlib)) * 100
        print(f"WINNER: Frequency Mapping")
        print(f"   Smaller by: {diff:,} bytes ({percent:.1f}% more efficient)")
    
    print()


# ============================================
# USAGE EXAMPLES
# ============================================

if __name__ == "__main__":
    print("\n")
    print("="*70)
    print("GENERATOR CREATOR - zlib Compression")
    print("="*70)
    print("\n")
    
    # Example 1: Short string
    print("EXAMPLE 1: Short string (58 characters)\n")
    short_str = "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"
    create_zlib_generator(short_str, "generator_string_zlib.py")
    compare_with_freq_mapping(short_str)
    
    print("\n" + "="*70)
    print("FOR YOUR 30,000 CHARACTER STRING:")
    print("="*70)
    print("""
# Option 1: String directly in code
my_string = "your_complete_30000_character_string..."
create_zlib_generator(my_string, "generator_final_zlib.py")

# Option 2: Read from file
with open('string_30000.txt', 'r', encoding='utf-8') as f:
    long_string = f.read()
create_zlib_generator(long_string, "generator_final_zlib.py")

# Option 3: With comparison
create_zlib_generator(long_string, "generator_final_zlib.py")
compare_with_freq_mapping(long_string)
    """)