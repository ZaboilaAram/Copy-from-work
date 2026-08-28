#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
carte_txt_in_word.py — transformă manuscrisul .txt în document Word paginat.

    python carte_txt_in_word.py                       (găsește singur .txt-ul)
    python carte_txt_in_word.py sursa.txt
    python carte_txt_in_word.py sursa.txt -o "Cuvinte despre viata.docx"
    python carte_txt_in_word.py sursa.txt --titlu "CUVINTE|DESPRE TOT" --fara-subtitlu

Pe Windows se poate și cu dublu-clic: dacă în folder există un singur
fișier .txt, scriptul îl ia pe acela și așteaptă o tastă la final.

Cere o singură bibliotecă, python-docx, pe care o ai deja instalată.
Testat pe python-docx 1.1.2.  Dacă lipsește:  pip install python-docx

CE RECUNOAȘTE DIN .TXT
  ====...====  /  PARTEA A N-A — X  /  ====...====   → titlu de parte, pagină nouă
  ====...====  /  CUPRINS           /  ====...====   → cuprins (font monospațiat)
  „N. TITLU"                                         → titlu de capitol
  ───                                                → separator (romb centrat)
  linia de după ─── , fără punct la final            → subtitlu (bold-italic)
  ----- PRAG I -----  ... -----                      → casetă încadrată, italic
  -----  /  PUNTE — ...  /  -----                    → casetă de punte
  rânduri indentate cu 4+ spații                     → citat retras, italic
  UN RÂND SCRIS TOT CU MAJUSCULE                     → titlu de secțiune

REGULA CENTRALĂ
  În .txt textul e înfășurat la ~72 de caractere, dar stilul cărții este
  un rând pe propoziție. Scriptul reface distincția: un rând nou începe
  doar dacă rândul precedent s-a terminat cu . ! ? : ” — altfel e
  continuarea aceleiași propoziții și se lipește înapoi.
"""

import argparse
import re
import sys
from pathlib import Path

# consola Windows este cp1252 și s-ar bloca la diacriticele din mesaje
for _flux in (sys.stdout, sys.stderr):
    try:
        _flux.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Mm, Pt, RGBColor
except ImportError:
    sys.exit("Lipsește python-docx.  Instalează-l cu:  pip install python-docx")

# ─────────────────────────── configurație ───────────────────────────

SERIF      = "Cambria"     # fontul corpului
MONO       = "Consolas"    # fontul cuprinsului (păstrează alinierea)
CORP_PT    = 11
INTERLINIE = 1.15
GRI        = RGBColor(0x6E, 0x6E, 0x6E)
GRI_SEMN   = RGBColor(0x9A, 0x9A, 0x9A)

MARGINI    = dict(top=Mm(25), bottom=Mm(25), left=Mm(28), right=Mm(28))

SPATIU_BLOC   = Pt(9)    # aer între blocuri (rândul gol din .txt)
SPATIU_CAPITOL= Pt(28)   # deasupra unui titlu de capitol
SPATIU_PARTE  = Pt(26)   # sub un titlu de parte

# ─────────────────────────── recunoaștere ───────────────────────────

RE_EGAL     = re.compile(r"^=+$")
RE_LINIUTE  = re.compile(r"^-{10,}$")
RE_PRAG     = re.compile(r"^-+\s*PRAG\b")
RE_PARTE    = re.compile(r"^(PARTEA |EPILOG)")
RE_CAPITOL  = re.compile(r"^\d+\.\s+[A-ZĂÂÎȘȚ]")
RE_MAJUSCULE= re.compile(r"^[A-ZĂÂÎȘȚ ,\-]{12,}$")
RE_INDENTAT = re.compile(r"^ {4,}\S")
SEPARATOR   = "───"
FINAL_FRAZA = re.compile(r"[.!?:”]$")


def este_separator(linie): return linie.strip() == SEPARATOR


def blocuri(linii):
    """Grupează rândurile consecutive ne-goale în blocuri."""
    rez, curent = [], []
    for l in linii:
        if l.strip():
            curent.append(l)
        elif curent:
            rez.append(curent)
            curent = []
    if curent:
        rez.append(curent)
    return rez


def randuri_autor(bloc):
    """Reface rândurile intenționate, desfăcând înfășurarea la 72 de caractere."""
    rez = []
    for l in bloc:
        t = l.strip()
        if not rez or FINAL_FRAZA.search(rez[-1]):
            rez.append(t)
        else:
            rez[-1] += " " + t
    return rez


# ─────────────────────────── unelte Word ───────────────────────────

def _fixeaza_font(run, font):
    """Fixează fontul pe toate cele patru sloturi, ca Word să nu substituie."""
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    for slot in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rFonts.set(qn(slot), font)


class Constructor:
    def __init__(self, doc):
        self.doc = doc

    def p(self, text="", *, font=SERIF, mărime=CORP_PT, bold=False, italic=False,
          culoare=None, aliniere=None, inainte=Pt(0), dupa=Pt(0),
          retras=None, interlinie=INTERLINIE):
        par = self.doc.add_paragraph()
        pf = par.paragraph_format
        pf.space_before, pf.space_after = inainte, dupa
        pf.line_spacing = interlinie
        if aliniere is not None:
            par.alignment = aliniere
        if retras is not None:
            pf.left_indent = retras
        if text:
            r = par.add_run(text)
            r.font.name, r.font.size = font, Pt(mărime)
            r.bold, r.italic = bold, italic
            if culoare is not None:
                r.font.color.rgb = culoare
            _fixeaza_font(r, font)
        return par

    def linie_sus(self, par, grosime=6, culoare="000000", spatiu=8):
        """Adaugă o bordură superioară paragrafului (folosită pentru casete)."""
        pPr = par._p.get_or_add_pPr()
        bdr = OxmlElement("w:pBdr")
        top = OxmlElement("w:top")
        top.set(qn("w:val"), "single")
        top.set(qn("w:sz"), str(grosime))
        top.set(qn("w:space"), str(spatiu))
        top.set(qn("w:color"), culoare)
        bdr.append(top)
        pPr.append(bdr)

    def titlu(self, text, nivel, *, mărime, pagina_noua=False,
              inainte=Pt(0), dupa=Pt(12), italic=False):
        par = self.doc.add_paragraph(style=f"Heading {nivel}")
        pf = par.paragraph_format
        pf.space_before, pf.space_after = inainte, dupa
        pf.page_break_before = pagina_noua
        pf.line_spacing = 1.0
        r = par.add_run(text)
        r.font.name, r.font.size = SERIF, Pt(mărime)
        r.bold, r.italic = True, italic
        r.font.color.rgb = RGBColor(0, 0, 0)
        _fixeaza_font(r, SERIF)
        return par

    def separator(self):
        self.p("◆", mărime=8, culoare=GRI_SEMN,
               aliniere=WD_ALIGN_PARAGRAPH.CENTER,
               inainte=Pt(13), dupa=Pt(11))

    def bloc(self, bloc_linii, *, italic=False, retras=None, inainte=SPATIU_BLOC):
        for i, t in enumerate(randuri_autor(bloc_linii)):
            self.p(t, italic=italic, retras=retras,
                   inainte=inainte if i == 0 else Pt(0))

    def numerotare_subsol(self, secțiune):
        par = secțiune.footer.paragraphs[0]
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_before = Pt(10)
        r = par.add_run()
        r.font.name, r.font.size = SERIF, Pt(9)
        r.font.color.rgb = GRI
        # câmpul PAGE, construit din trei elemente XML
        inceput = OxmlElement("w:fldChar")
        inceput.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = "PAGE"
        sfarsit = OxmlElement("w:fldChar")
        sfarsit.set(qn("w:fldCharType"), "end")
        for el in (inceput, instr, sfarsit):
            r._r.append(el)


# ─────────────────────────── conversia ───────────────────────────

def construiește(text, titlu_pagina, subtitlu):
    doc = Document()
    sec = doc.sections[0]
    for k, v in MARGINI.items():
        setattr(sec, f"{k}_margin", v)

    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = SERIF, Pt(CORP_PT)

    b = Constructor(doc)
    b.numerotare_subsol(sec)

    # ── pagina de titlu ──
    b.p(inainte=Pt(130))
    for rand in titlu_pagina:
        b.p(rand, mărime=26, bold=True, aliniere=WD_ALIGN_PARAGRAPH.CENTER,
            interlinie=1.0, inainte=Pt(6))
    if subtitlu:
        b.p(subtitlu, mărime=12, italic=True, culoare=GRI,
            aliniere=WD_ALIGN_PARAGRAPH.CENTER, inainte=Pt(21))
    b.doc.paragraphs[-1].add_run().add_break(WD_BREAK.PAGE)

    linii = text.split("\n")
    i = 0
    in_cuprins = False
    posibil_subtitlu = False   # imediat după un separator

    while i < len(linii):
        l = linii[i]

        # ── bandă ==== ... ==== ──
        if RE_EGAL.match(l.strip()):
            j = i + 1
            interior = []
            while j < len(linii) and not RE_EGAL.match(linii[j].strip()):
                interior.append(linii[j])
                j += 1
            curat = [s.strip() for s in interior if s.strip()]
            parte = next((t for t in curat if RE_PARTE.match(t)), None)
            if parte:
                b.titlu(parte, 1, mărime=17, pagina_noua=True, dupa=SPATIU_PARTE)
            elif any(t.startswith("CUPRINS") for t in curat):
                in_cuprins = True
                b.titlu("CUPRINS", 1, mărime=17, pagina_noua=True, dupa=Pt(14))
                nota = " ".join(t for t in curat if t.startswith("(") or t.endswith(")"))
                if nota:
                    b.p(re.sub(r"\s+", " ", nota), mărime=9.5, italic=True,
                        culoare=GRI, dupa=Pt(10))
            elif curat and not in_cuprins:
                # bandă de titlu de la începutul fișierului — ignorată,
                # pagina de titlu se compune separat
                pass
            i = j + 1
            posibil_subtitlu = False
            continue

        # ── casetă PRAG ──
        if RE_PRAG.match(l.strip()):
            eticheta = l.replace("-", "").strip()
            j = i + 1
            interior = []
            while j < len(linii) and not RE_LINIUTE.match(linii[j].strip()):
                interior.append(linii[j])
                j += 1
            par = b.p(eticheta, mărime=12, bold=True,
                      aliniere=WD_ALIGN_PARAGRAPH.CENTER,
                      inainte=Pt(21), dupa=Pt(8))
            b.linie_sus(par, grosime=6, culoare="000000", spatiu=8)
            for bl in blocuri(interior):
                b.bloc(bl, italic=True, inainte=Pt(8))
            închidere = b.p(dupa=Pt(17), inainte=Pt(3))
            b.linie_sus(închidere, grosime=6, culoare="000000", spatiu=6)
            i = j + 1
            posibil_subtitlu = False
            continue

        # ── casetă PUNTE / CELE PATRU PRAGURI ──
        if RE_LINIUTE.match(l.strip()):
            j = i + 1
            interior = []
            while j < len(linii) and not RE_LINIUTE.match(linii[j].strip()):
                interior.append(linii[j])
                j += 1
            curat = [s.strip() for s in interior]
            k = next((n for n, t in enumerate(curat)
                      if t.startswith("PUNTE") or t.startswith("CELE PATRU")), None)
            if k is not None:
                par = b.p(curat[k], mărime=10.5, bold=True,
                          inainte=Pt(23), dupa=Pt(9))
                b.linie_sus(par, grosime=4, culoare="AAAAAA", spatiu=10)
                rest = interior[k + 1:]
                if curat[k].startswith("CELE PATRU"):
                    for r in rest:
                        b.p(r.replace("\t", "    "), font=MONO, mărime=8.5,
                            inainte=Pt(0)) if r.strip() else b.p(mărime=6)
                else:
                    for bl in blocuri(rest):
                        b.bloc(bl, italic=True, inainte=Pt(8))
                închidere = b.p(dupa=Pt(10), inainte=Pt(6))
                b.linie_sus(închidere, grosime=4, culoare="AAAAAA", spatiu=6)
            i = j + 1
            posibil_subtitlu = False
            continue

        # ── separator ───
        if este_separator(l):
            b.separator()
            posibil_subtitlu = True
            i += 1
            continue

        if not l.strip():
            i += 1
            continue

        # ── titlu de capitol ──
        if RE_CAPITOL.match(l):
            b.titlu(l.strip(), 2, mărime=13, inainte=SPATIU_CAPITOL, dupa=Pt(12))
            posibil_subtitlu = False
            i += 1
            continue

        # ── titlu de secțiune scris cu majuscule ──
        if RE_MAJUSCULE.match(l.strip()) and not in_cuprins:
            b.titlu(l.strip(), 2, mărime=13, inainte=Pt(24), dupa=Pt(13))
            i += 1
            continue

        # ── bloc obișnuit ──
        j = i
        bloc_curent = []
        while (j < len(linii) and linii[j].strip()
               and not este_separator(linii[j])
               and not RE_EGAL.match(linii[j].strip())
               and not RE_LINIUTE.match(linii[j].strip())
               and not RE_CAPITOL.match(linii[j])):
            bloc_curent.append(linii[j])
            j += 1

        if in_cuprins:
            for r in bloc_curent:
                cap = bool(re.match(r"^(PARTEA |EPILOG|DESPRE FELUL)", r.strip()))
                b.p(r.replace("\t", "    "), font=MONO, mărime=8.5,
                    bold=cap, inainte=Pt(10) if cap else Pt(0))
            i = j
            continue

        indentat = all(RE_INDENTAT.match(r) for r in bloc_curent)
        randuri = randuri_autor(bloc_curent)

        # Un subtitlu real ocupă exact un rând în .txt și nu se termină cu
        # semn de final de frază. Condiția pe len(bloc_curent) este esențială:
        # fără ea, o frază înfășurată pe două rânduri al cărei prim rând este
        # scurt ar fi luată drept titlu, iar al doilea rând s-ar pierde.
        e_subtitlu = (posibil_subtitlu
                      and len(bloc_curent) == 1
                      and len(randuri) == 1
                      and not FINAL_FRAZA.search(randuri[0])
                      and len(randuri[0]) < 62)

        if e_subtitlu:
            b.titlu(randuri[0], 3, mărime=11,
                    inainte=Pt(2), dupa=Pt(10), italic=True)
        elif indentat:
            b.bloc(bloc_curent, italic=True, retras=Mm(12), inainte=Pt(13))
        else:
            b.bloc(bloc_curent)

        posibil_subtitlu = False
        i = j

    return doc


# ─────────────────────────── verificare ───────────────────────────

def randuri_asteptate(text):
    """Reconstruiește toate rândurile de autor din corpul cărții."""
    corp = re.split(r"\n\s+CUPRINS\s*\n", text)[0]
    rez, bloc = [], []

    def varsa():
        acc = []
        for r in bloc:
            if not acc or FINAL_FRAZA.search(acc[-1]):
                acc.append(r)
            else:
                acc[-1] += " " + r
        rez.extend(acc)

    for l in corp.split("\n"):
        t = l.strip()
        if not t or t == SEPARATOR or set(t) <= set("=-"):
            if bloc:
                varsa()
                bloc.clear()
            continue
        bloc.append(t)
    if bloc:
        varsa()
    return rez


def verifica(text, doc):
    """Caută fiecare rând din .txt în documentul Word. Întoarce ce lipsește."""
    normalizeaza = lambda s: re.sub(r"\s+", " ", s).strip()
    in_word = normalizeaza(" \n ".join(p.text for p in doc.paragraphs))

    # apar altfel prin construcție, nu sunt pierderi:
    #   banda de titlu de la începutul fișierului (pagina de titlu e separată)
    #   etichetele ---- PRAG ---- (în Word apar fără liniuțe, încadrate)
    de_ignorat = re.compile(r"^-+\s*PRAG|^CUVINTE DESPRE VIA|^O carte care merge")

    asteptate = randuri_asteptate(text)
    lipsa = [r for r in asteptate
             if not de_ignorat.match(r) and normalizeaza(r) not in in_word]
    return len(asteptate), lipsa


def gaseste_sursa():
    """Fără argument: caută un .txt în folderul curent, apoi lângă script."""
    candidate = []
    for folder in (Path.cwd(), Path(__file__).resolve().parent):
        for f in sorted(folder.glob("*.txt")):
            if f.resolve() not in [c.resolve() for c in candidate]:
                candidate.append(f)
        if candidate:
            break
    return candidate


def main():
    ap = argparse.ArgumentParser(
        description="Transformă manuscrisul .txt în document Word paginat.")
    ap.add_argument("sursa", nargs="?",
                    help="fișierul .txt al cărții (dacă lipsește, îl caută singur)")
    ap.add_argument("-o", "--ieșire", help="numele fișierului .docx rezultat")
    ap.add_argument("--titlu", default="CUVINTE|DESPRE VIAȚĂ",
                    help="titlul de pe prima pagină; rândurile se despart cu |")
    ap.add_argument("--subtitlu",
                    default="Un drum de la existență până la o zi obișnuită")
    ap.add_argument("--fara-subtitlu", action="store_true")
    ap.add_argument("--fara-verificare", action="store_true",
                    help="sare peste controlul că nu s-a pierdut niciun rând")
    a = ap.parse_args()

    fara_argumente = a.sursa is None

    # ── alegerea fișierului sursă ──
    if a.sursa:
        sursa = Path(a.sursa)
        if not sursa.exists():
            alt = Path(__file__).resolve().parent / a.sursa
            if alt.exists():
                sursa = alt
            else:
                termina(f"Nu găsesc fișierul: {a.sursa}", fara_argumente, cod=1)
    else:
        gasite = gaseste_sursa()
        if not gasite:
            termina("Nu am găsit niciun fișier .txt în acest folder.\n"
                    "Pune manuscrisul lângă script sau scrie numele lui:\n"
                    "    python carte_txt_in_word.py numele_cartii.txt",
                    fara_argumente, cod=1)
        if len(gasite) > 1:
            lista = "\n".join(f"    {f.name}" for f in gasite)
            termina("În folder sunt mai multe fișiere .txt. Spune-mi pe care:\n"
                    f"{lista}\n\n"
                    "    python carte_txt_in_word.py numele_cartii.txt",
                    fara_argumente, cod=1)
        sursa = gasite[0]
        print(f"folosesc: {sursa.name}")

    ieșire = Path(a.ieșire) if a.ieșire else sursa.with_suffix(".docx")

    try:
        text = sursa.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        termina(f"Fișierul {sursa.name} nu este salvat în UTF-8.\n"
                "Deschide-l în Notepad, Salvare ca..., Codificare: UTF-8.",
                fara_argumente, cod=1)

    doc = construiește(
        text,
        titlu_pagina=[t.strip() for t in a.titlu.split("|") if t.strip()],
        subtitlu=None if a.fara_subtitlu else a.subtitlu,
    )

    try:
        doc.save(ieșire)
    except PermissionError:
        termina(f"Nu pot scrie {ieșire.name} — probabil e deschis în Word.\n"
                "Închide-l și rulează din nou.", fara_argumente, cod=1)

    cuvinte = f"{len(text.split()):,}".replace(",", ".")
    print(f"gata: {ieșire.name}")
    print(f"      {cuvinte} cuvinte, {len(doc.paragraphs)} paragrafe, "
          f"{text.count('De aici ajungem')} punti")

    if a.fara_verificare:
        termina(None, fara_argumente, cod=0)

    total, lipsa = verifica(text, doc)
    if not lipsa:
        print(f"      verificare: toate cele {total} randuri din .txt "
              f"sunt in Word")
        termina(None, fara_argumente, cod=0)

    print(f"\n  ATENTIE: {len(lipsa)} randuri din .txt nu au ajuns in Word.")
    print("  Documentul a fost salvat, dar este INCOMPLET.\n")
    for r in lipsa[:15]:
        print(f"    - {r[:72]}")
    if len(lipsa) > 15:
        print(f"    ... si alte {len(lipsa) - 15}")
    raport = ieșire.with_name(ieșire.stem + "_randuri_lipsa.txt")
    raport.write_text("\n".join(lipsa), encoding="utf-8")
    print(f"\n  Lista completa: {raport.name}")
    termina(None, fara_argumente, cod=2)


def termina(mesaj, aspecta_tasta, cod=0):
    """Închide curat, ținând fereastra deschisă la dublu-clic pe Windows."""
    if mesaj:
        print(mesaj)
    if aspecta_tasta:
        try:
            input("\nApasă Enter ca sa inchizi...")
        except Exception:
            pass
    sys.exit(cod)


if __name__ == "__main__":
    main()
