import re
import orodja
import csv

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


stripi = []
for st_strani in range(1,35):
    for strip in stripi_st_strani(st_strani):
        stripi.append(strip)
stripi.sort(key=lambda strip: strip['id'])
orodja.zapisi_json(stripi, 'obdelani-podatki/stripi.json')
orodja.zapisi_csv(
    stripi,
    ['id', 'naslov', 'avtor', 'url', 'leto', 'format', 'sedanja_cena', 'prejsnja_cena'], 'obdelani-podatki/stripi.csv'
)

vzorec_bloka_enega_stripa = re.compile(
    r'<h2>Description</h2>(\n|.)*?'
    r'</li>(\s|\n)*</ul>(\s|\n)*</div>(\s|\n)*</div>(\s|\n)*</div>'
)

vzorec_enega_stripa = re.compile(
    r'<div class="item-excerpt trunc" itemprop="description" data-height="230">(\s|\n)*?'
    r'(?P<prvi_del>.*)(\s|\n)*<br />(.|\n)*?'
    r'<span itemprop="numberOfPages">(?P<stevilo_strani>\d*) pages(\n|.)*?'
    r'<label>Publisher</label>(\n|.)*?<span itemprop="name">(\n|\s)*(?P<izdajatelj>.*)</span>(\n|.)*?'
    r'<label>Publication City/Country</label>(\s|\n)*<span>(\s|\n)*(?P<drzava>.*)</span>(\n|.)*?'
    r'<label>Language</label>(\s|\n)*<span>(\s|\n)*(?P<jezik>.*)</span>(\n|.)*?'
    r'<label>ISBN13</label>(\s|\n)*<span itemprop="isbn">(?P<id>\d{13})</span>'
)


vzorec_drugi_vpis = re.compile(
    r'<br/>(\s|\n)*?<br/>(\s|\n)*(?P<drugi_opis>.*)(\n|\s)*<br/>(\s|\n)*?'
    r'<a class=\'read-more\' tabIndex="0">show more</a>'
)

def izloci_podatke_za_en_strip(blok):
    strip = vzorec_enega_stripa.search(blok).groupdict()
    strip['id'] = int(strip['id'][1:-1])
    strip['stevilo_strani'] = int(strip['stevilo_strani'])
    strip['jezik'] = str(strip['jezik'])
    strip['izdajatelj'] = str(strip['izdajatelj'])
    strip['drzava'] = str(strip['drzava'])
    strip['prvi_del'] = str(strip['prvi_del'])
    drugi_del = vzorec_drugi_vpis.search(blok)
    if drugi_del:
        strip['opis'] = str(strip['prvi_del']) + " " + str(drugi_del['drugi_opis'])
        strip['opis'].replace("&#039;", "'").replace("&amp;!", "&!")
        del strip['drugi_del']
    else:
        strip['opis'] = str(strip['prvi_del'].replace("&#039;", "'").replace("&amp;!", "&!"))
    del strip['prvi_del']
    return strip



with open("obdelani-podatki/stripi.csv", 'r') as file:
        seznam_iz_csv = []
        csvreader = csv.reader(file)
        for row in csvreader:
            seznam_iz_csv.append(row)

def strip_eden(vrstica):
    id, url = vrstica[0], vrstica[3]
    url = (
        f'https://www.bookdepository.com/'
        f'{url}'
       )
    ime_datoteke = 'obdelani-podatki/posamezni/posamezen_strip{}.html'.format(id)
    orodja.shrani_spletno_stran(url, ime_datoteke)
    vsebina = orodja.vsebina_datoteke(ime_datoteke)
    return izloci_podatke_za_en_strip(vsebina)

stripi2 = []
for vrstica in seznam_iz_csv[1:]:
    stripi2.append(strip_eden(vrstica))
orodja.zapisi_json(stripi2, 'obdelani-podatki/posamezni-stripi.json')
orodja.zapisi_csv(
    stripi2,
    ['id', 'stevilo_strani', 'jezik', 'izdajatelj', 'drzava', 'opis'], 'obdelani-podatki/posamezni-stripi.csv'
)

#Se imena avtorjev, izdajateljev zamenjaj s stevilkami