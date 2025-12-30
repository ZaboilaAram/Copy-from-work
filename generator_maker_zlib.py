# generator_maker_zlib.py - Compresie cu zlib

import zlib
import base64

def creeaza_generator_zlib(sir_original, nume_fisier="generator_sir_zlib.py"):
    """
    Analizează un șir și generează un script Python care îl regenerează
    folosind compresia zlib (DEFLATE algorithm)
    
    Args:
        sir_original: șirul de caractere (poate fi foarte lung)
        nume_fisier: numele scriptului generat (default: generator_sir_zlib.py)
    """
    
    print("="*70)
    print("🔍 ANALIZEZ ȘIRUL CU ZLIB COMPRESSION...")
    print("="*70 + "\n")
    
    # Informații despre șirul original
    print(f"📊 Informații de bază:")
    print(f"   Lungime șir: {len(sir_original):,} caractere")
    print(f"   Dimensiune raw: {len(sir_original.encode('utf-8')):,} bytes")
    
    caractere_unice = len(set(sir_original))
    print(f"   Caractere unice: {caractere_unice}")
    print()
    
    # Testează diferite niveluri de compresie
    print(f"🧪 Testez niveluri de compresie zlib:")
    
    nivele = {}
    for nivel in range(0, 10):
        compressed = zlib.compress(sir_original.encode('utf-8'), level=nivel)
        nivele[nivel] = len(compressed)
        
        if nivel == 0:
            print(f"   Nivel {nivel} (fără compresie): {len(compressed):,} bytes")
        elif nivel == 1:
            print(f"   Nivel {nivel} (rapid):          {len(compressed):,} bytes")
        elif nivel == 6:
            print(f"   Nivel {nivel} (default):        {len(compressed):,} bytes")
        elif nivel == 9:
            print(f"   Nivel {nivel} (maxim):          {len(compressed):,} bytes ⭐")
    
    print()
    
    # Folosește nivelul maxim (9) pentru compresie optimă
    compressed_bytes = zlib.compress(sir_original.encode('utf-8'), level=9)
    compressed_b64 = base64.b64encode(compressed_bytes).decode('ascii')
    
    # Calculează statistici
    original_bytes = len(sir_original.encode('utf-8'))
    compressed_size = len(compressed_bytes)
    base64_size = len(compressed_b64)
    
    ratio_compressed = (1 - compressed_size / original_bytes) * 100
    ratio_base64 = (1 - base64_size / original_bytes) * 100
    
    print(f"💾 REZULTATE COMPRESIE (nivel 9):")
    print(f"   Original (UTF-8):       {original_bytes:>10,} bytes")
    print(f"   Comprimate (zlib):      {compressed_size:>10,} bytes ({compressed_size/original_bytes*100:5.1f}%)")
    print(f"   Base64 encoded:         {base64_size:>10,} bytes ({base64_size/original_bytes*100:5.1f}%)")
    print()
    print(f"   Economie (zlib):        {ratio_compressed:>10.1f}%")
    print(f"   Economie (base64):      {ratio_base64:>10.1f}%")
    print()
    
    if ratio_compressed > 70:
        print(f"   ✅ EXCELENT! Compresie extraordinară")
    elif ratio_compressed > 50:
        print(f"   ✅ FOARTE BUN! Compresie eficientă")
    elif ratio_compressed > 30:
        print(f"   👍 BUN! Compresie decentă")
    else:
        print(f"   ⚠️  Compresie moderată - șirul e foarte random")
    print()
    
    # Informații despre pattern-uri (de ce funcționează bine/rău compresia)
    from collections import Counter
    
    # Analizează repetiții
    bigrams = [sir_original[i:i+2] for i in range(len(sir_original)-1)]
    bigram_freq = Counter(bigrams)
    top_bigram = bigram_freq.most_common(1)[0] if bigram_freq else (None, 0)
    
    trigrams = [sir_original[i:i+3] for i in range(len(sir_original)-2)]
    trigram_freq = Counter(trigrams)
    top_trigram = trigram_freq.most_common(1)[0] if trigram_freq else (None, 0)
    
    print(f"🔬 Analiza pattern-urilor (de ce compresia funcționează):")
    print(f"   Cel mai frecvent bigram: '{top_bigram[0]}' ({top_bigram[1]} apariții)")
    print(f"   Cel mai frecvent trigram: '{top_trigram[0]}' ({top_trigram[1]} apariții)")
    
    # Entropie aproximativă
    char_freq = Counter(sir_original)
    entropy = -sum((count/len(sir_original)) * 
                   (count/len(sir_original)).bit_length() 
                   for count in char_freq.values())
    print(f"   Entropie aproximativă: {entropy:.2f} bits/char")
    print()
    
    # Generează scriptul Python
    cod_generat = f'''"""
Generator de șir cu zlib compression (DEFLATE algorithm)
Generat automat de generator_maker_zlib.py

Statistici compresie:
- Lungime șir original: {len(sir_original):,} caractere ({original_bytes:,} bytes)
- Comprimate cu zlib: {compressed_size:,} bytes
- Economie: {ratio_compressed:.1f}%
- Nivel compresie: 9 (maxim)

zlib folosește algoritmul DEFLATE care combină:
- LZ77: Detectează secvențe repetate
- Huffman coding: Codificare optimă a simbolurilor
"""

import zlib
import base64


def genereaza_sir():
    """
    Regenerează șirul original din date comprimate cu zlib
    
    Returns:
        str: Șirul original complet, decomprimat
    """
    
    # Date comprimate cu zlib (nivel 9) și encodate în base64
    # Base64 e necesar pentru a stoca date binare ca string în cod Python
    compressed_data = """{compressed_b64}"""
    
    # Pasul 1: Decodifică din base64 la bytes
    compressed_bytes = base64.b64decode(compressed_data)
    
    # Pasul 2: Decomprimă cu zlib
    decompressed_bytes = zlib.decompress(compressed_bytes)
    
    # Pasul 3: Decodifică din bytes la string UTF-8
    sir_original = decompressed_bytes.decode('utf-8')
    
    return sir_original


def info():
    """Afișează informații despre compresie"""
    print("="*60)
    print("📊 INFORMAȚII COMPRESIE ZLIB")
    print("="*60)
    print(f"Lungime șir original: {len(genereaza_sir()):,} caractere")
    print(f"Dimensiune originală: {original_bytes:,} bytes")
    print(f"Dimensiune comprimată: {compressed_size:,} bytes")
    print(f"Dimensiune base64: {base64_size:,} bytes")
    print(f"Ratio compresie: {compressed_size/original_bytes*100:.1f}%")
    print(f"Economie: {ratio_compressed:.1f}%")
    print(f"Nivel compresie zlib: 9 (maxim)")
    print("="*60)


def verifica_sir(sir_asteptat=None):
    """
    Verifică dacă șirul generat este corect
    
    Args:
        sir_asteptat: șirul original pentru comparație (opțional)
    
    Returns:
        bool sau str: True/False dacă sir_asteptat e dat, altfel șirul generat
    """
    sir_generat = genereaza_sir()
    
    print(f"Lungime șir generat: {{len(sir_generat):,}}")
    print(f"Primele 100 caractere: {{sir_generat[:100]}}")
    
    if sir_asteptat:
        match = sir_generat == sir_asteptat
        print(f"Match cu originalul: {{match}}")
        
        if not match:
            print(f"EROARE: Șirul nu se potrivește!")
            # Găsește prima diferență
            min_len = min(len(sir_generat), len(sir_asteptat))
            for i in range(min_len):
                if sir_generat[i] != sir_asteptat[i]:
                    print(f"Prima diferență la poziția {{i}}:")
                    print(f"  Generat:  '{{sir_generat[i]}}'")
                    print(f"  Așteptat: '{{sir_asteptat[i]}}'")
                    break
            
            if len(sir_generat) != len(sir_asteptat):
                print(f"Lungimi diferite: {{len(sir_generat)}} vs {{len(sir_asteptat)}}")
        
        return match
    
    return sir_generat


if __name__ == "__main__":
    print("="*60)
    print("🚀 GENERATOR DE ȘIR (ZLIB COMPRESSION)")
    print("="*60)
    print()
    
    sir = genereaza_sir()
    print(f"✅ Șir generat cu succes!")
    print(f"   Lungime: {{len(sir):,}} caractere")
    print(f"   Primele 100 caractere: {{sir[:100]}}")
    print()
    
    info()
'''
    
    # Salvează scriptul generat
    with open(nume_fisier, 'w', encoding='utf-8') as f:
        f.write(cod_generat)
    
    print("="*70)
    print(f"✅ SCRIPT GENERAT: {nume_fisier}")
    print("="*70)
    print(f"\n📝 Următorii pași:")
    print(f"   1. Rulează direct: python {nume_fisier}")
    print(f"   2. Sau importă: from {nume_fisier[:-3]} import genereaza_sir")
    print(f"   3. Folosește: sir = genereaza_sir()")
    print()


def compara_cu_freq_mapping(sir_original):
    """
    Compară compresia zlib cu frequency mapping
    Pentru a vedea câștigul real
    """
    from collections import Counter
    
    print("\n" + "="*70)
    print("⚖️  COMPARAȚIE: zlib vs Frequency Mapping")
    print("="*70 + "\n")
    
    # zlib
    compressed_zlib = zlib.compress(sir_original.encode('utf-8'), level=9)
    zlib_b64 = base64.b64encode(compressed_zlib).decode('ascii')
    
    # Frequency mapping (simulare)
    caractere_unice = ''.join(sorted(set(sir_original)))
    indici = [caractere_unice.index(c) for c in sir_original]
    
    freq = Counter(indici)
    top_52 = [idx for idx, _ in freq.most_common(52)]
    
    simboluri = [chr(97+i) for i in range(26)] + [chr(65+i) for i in range(26)]
    mapping = {idx: simboluri[i] for i, idx in enumerate(top_52)}
    
    compressed_freq = []
    for idx in indici:
        if idx in mapping:
            compressed_freq.append(mapping[idx])
        else:
            compressed_freq.append(f"_{idx}_")
    
    freq_string = ''.join(compressed_freq)
    freq_total = len(freq_string) + len(caractere_unice) + 500  # overhead
    
    original_size = len(sir_original)
    
    print(f"📊 Dimensiuni:")
    print(f"   Original:              {original_size:>10,} bytes (100.0%)")
    print(f"   Frequency Mapping:     {freq_total:>10,} bytes ({freq_total/original_size*100:5.1f}%)")
    print(f"   zlib + base64:         {len(zlib_b64):>10,} bytes ({len(zlib_b64)/original_size*100:5.1f}%)")
    print(f"   zlib raw:              {len(compressed_zlib):>10,} bytes ({len(compressed_zlib)/original_size*100:5.1f}%)")
    print()
    
    if len(compressed_zlib) < freq_total:
        diff = freq_total - len(compressed_zlib)
        procent = (1 - len(compressed_zlib)/freq_total) * 100
        print(f"🏆 CÂȘTIGĂTOR: zlib")
        print(f"   Mai mic cu: {diff:,} bytes ({procent:.1f}% mai eficient)")
    else:
        diff = len(compressed_zlib) - freq_total
        procent = (1 - freq_total/len(compressed_zlib)) * 100
        print(f"🏆 CÂȘTIGĂTOR: Frequency Mapping")
        print(f"   Mai mic cu: {diff:,} bytes ({procent:.1f}% mai eficient)")
    
    print()


# ============================================
# EXEMPLE DE UTILIZARE
# ============================================

if __name__ == "__main__":
    print("\n")
    print("="*70)
    print("🎯 GENERATOR DE GENERATOARE - zlib Compression")
    print("="*70)
    print("\n")
    
    # Exemplu 1: Șir scurt
    print("📝 EXEMPLU 1: Șir scurt (62 caractere)\n")
    sir_scurt = "12xaebcad92bdas0hdlopm2963bgdjkewpmadgrizndunsohvsjibsjxoj"
    creeaza_generator_zlib(sir_scurt, "generator_sir_zlib.py")
    compara_cu_freq_mapping(sir_scurt)
    
    print("\n" + "="*70)
    print("💡 PENTRU ȘIRUL TĂU DE 30,000 CARACTERE:")
    print("="*70)
    print("""
# Variantă 1: Șir direct în cod
sir_meu = "șirul_tău_complet_de_30000_caractere..."
creeaza_generator_zlib(sir_meu, "generator_final_zlib.py")

# Variantă 2: Citire din fișier
with open('sir_30000.txt', 'r', encoding='utf-8') as f:
    sir_lung = f.read()
creeaza_generator_zlib(sir_lung, "generator_final_zlib.py")

# Variantă 3: Cu comparație
creeaza_generator_zlib(sir_lung, "generator_final_zlib.py")
compara_cu_freq_mapping(sir_lung)
    """)