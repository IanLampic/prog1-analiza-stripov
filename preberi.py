import re

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
        del strip['drugi_del']
    else:
        strip['opis'] = str(strip['prvi_del'])
    del strip['prvi_del']
    return strip

#with open('prvi_strip.html') as f:
#    vsebina = f.read()
#print(izloci_podatke_za_en_strip(vsebina))

import csv
import orodja

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

stripi = []
for vrstica in seznam_iz_csv[1:]:
    stripi.append(strip_eden(vrstica))
orodja.zapisi_json(stripi, 'obdelani-podatki/posamezni-stripi.json')
orodja.zapisi_csv(
    stripi,
    ['id', 'stevilo_strani', 'jezik', 'izdajatelj', 'drzava', 'opis'], 'obdelani-podatki/posamezni-stripi.csv'
)

