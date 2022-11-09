import json

with open('obdelani-podatki/stripi.json') as f:
   data = json.load(f)

import re
import orodja

vzorec_bloka = re.compile(
    r'<div class="book-item" itemscope itemtype="http://schema.org/Book">.*?'
    r'</a>(\s|\n)*</div>(\s|\n)*</div>(\s|\n)*</div>.*?',
    flags=re.DOTALL
)

vzorec_stripa = re.compile(
    r'<meta itemprop="isbn" content=(?P<id>"\d{13}") />(\s|\n)*?' #vzorec za id
    r'<meta itemprop="name" content=(?P<naslov>.*) />(.|\n)*?' #vzorec za naslov
    r'<h3 class="title">(\n|\s)*<a href="(?P<url>.*?)">(.|\n)*?'
    r'<span itemprop="author" itemtype="http://schema.org/Person" itemscope=(?P<avtor>.*)>(\n|.)*?</a>(\n|.)*?</span>(\n|.)*?' #vzorec za avtorja
    r'<p class=\'published\' itemprop="datePublished">(\n|\s)*\d\d\s\w\w\w\s(?P<leto>.*)</p>(\n|.)*?' #vzorec za datum
    r'<p class="format">(\n|\s)*(?P<format>.*)</p>(\n|.)*?' #vzorec za format
)

vzorec_sedanja_cena = re.compile(
    r'<span class="sale-price">(?P<sedanja_cena>.*) €</span>'
)

vzorec_prejsnja_cena = re.compile(
    r'<span class="rrp omnibus">(?P<prejsnja_cena>.*) €</span>'
)

def izloci_podatke_stripa(blok):
    strip = vzorec_stripa.search(blok).groupdict()
    strip['id'] = int(strip['id'][1:-1])
    strip['naslov'] = str(strip['naslov'][1:-1].replace("&#039;", "'").replace("&amp;!", "&!"))
    strip['avtor'] = str(strip['avtor'][1:-1])
    strip['url'] = str(strip['url'])
    strip['leto'] = int(strip['leto'])
    strip['format'] = str(strip['format'])
    sedanja_cena = vzorec_sedanja_cena.search(blok)
    if sedanja_cena:
        strip['sedanja_cena'] = float(sedanja_cena['sedanja_cena'].replace(',', '.'))
    else:
        strip['sedanja_cena'] = None
    prejsnja_cena = vzorec_prejsnja_cena.search(blok)
    if prejsnja_cena:
        strip['prejsnja_cena'] = float(prejsnja_cena['prejsnja_cena'].replace(',', '.'))
    else:
        strip['prejsnja_cena'] = None
    return strip

def stripi_st_strani(st_strani):
    url = (
        f'https://www.bookdepository.com'
        f'/category/2634/Graphic-Novels-Manga?page={st_strani}'
    )
    ime_datoteke = 'obdelani-podatki/manga-stripi{}.html'.format(st_strani)
    orodja.shrani_spletno_stran(url, ime_datoteke) #headers={'Accept-Language': 'en'}) #Ta headers ne dela
    vsebina = orodja.vsebina_datoteke(ime_datoteke)
    for blok in vzorec_bloka.finditer(vsebina):
        yield izloci_podatke_stripa(blok.group(0))

def izloci_gnezdene_podatke(stripi):
    osebe, avtorji = [], []
    videne_osebe = set()

    def dodaj_vlogo(strip, oseba, mesto):
        if oseba['id'] not in videne_osebe:
            videne_osebe.add(oseba['id'])
            osebe.append(oseba)
        avtorji.append({
            'strip': strip['id'],
            'oseba': oseba['id'],
            'mesto': mesto,
        })


    for strip in stripi:
        for mesto, oseba in enumerate(strip.pop()["avtor"], 1):
            dodaj_vlogo(strip, oseba, mesto)

    osebe.sort(key=lambda oseba: oseba['id'])


    return osebe



stripi = []
for st_strani in range(1,35):
    for strip in stripi_st_strani(st_strani):
        stripi.append(strip)
stripi.sort(key=lambda strip: strip['id'])
orodja.zapisi_json(stripi, 'obdelani-podatki/stripi.json')
#avtorji = izloci_gnezdene_podatke(stripi)
orodja.zapisi_csv(
    stripi,
    ['id', 'naslov', 'avtor', 'url', 'leto', 'format', 'sedanja_cena', 'prejsnja_cena'], 'obdelani-podatki/stripi.csv'
)
#orodja.zapisi_csv(avtorji, ['id', 'ime'], 'obdelani-podatki/avtorji.csv')



for strip in [data[:10]]:
    for mesto, oseba in enumerate(strip.pop(2), 1):
        print(oseba, mesto)



