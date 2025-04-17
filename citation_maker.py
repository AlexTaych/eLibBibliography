from bs4 import BeautifulSoup
import re
from citation_dump import citation_dump, url_save, get_urls, counter


def get_bibliography(html_content, url='', bibl=False):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Article type - str
    if soup.find('td', width='574'):
        if 'Тип' in soup.find('td', width='574').get_text(strip=True):
            art_type_text = soup.find('td', width='574').find('font').get_text(strip=True)
        else:
            art_type_text = ''
    else:
        art_type_text = ''
    if art_type_text == 'статья в сборнике трудов конференции':
        main_body = get_conference(soup)
    elif art_type_text == 'статья в журнале - научная статья':
        main_body = get_article(soup)
    elif art_type_text == 'статья в журнале - материалы конференции':
        main_body = get_article(soup)
    elif art_type_text == 'статья в журнале - персоналия':
        main_body = get_article(soup)
    elif art_type_text == 'статья в журнале - рецензия':
        main_body = get_article(soup)
    elif art_type_text == 'диссертация':
        main_body = get_dissertation(soup)
    elif art_type_text == 'автореферат диссертации':
        main_body = get_dissertation(soup, autoref=True)
    else:
        return 'Обработка такого типа записи еще не готова'
    # DOI
    if soup.select('tr > td:nth-child(5) > font > a'):
        doi = soup.select('tr > td:nth-child(5) > font > a')[0]['href']
    else:
        doi = url
    if bibl:
        if doi in get_urls():
            return 'Данная статья уже находится в библиографии'
    # Abstract
    if soup.find('div', id='abstract2'):
        abstract = soup.find('div', id='abstract2').get_text(strip=True)
    elif soup.find('div', id='abstract1'):
        abstract = soup.find('div', id='abstract1').get_text(strip=True)
    else:
        abstract = ''
    # Counter
    if bibl:
        rec_num = counter()
        full_cite = f'{rec_num}.{main_body} {doi}\n\t{abstract}'
        citation_dump(full_cite)
        url_save(doi)
        return {'full_cite': full_cite, 'short_cite': main_body}
    else:
        return main_body

def get_article(soup):
    authors = get_authors(soup)
    title = get_title(soup)

    metric_list = []
    if soup.find_all('td', width='574'):
        metric_blocks = soup.find_all('td', width='574')
        for metric_block in metric_blocks:
            metric_block = metric_block.get_text()
            if 'Год' in metric_block:
                year = re.search(r'(?<=Год:).+|(?<=Год издания:).+', metric_block).group()
                metric_list.append(year.strip())
            vol_num_block = []
            if 'Том' in metric_block:
                volume = re.search(r'(?<=Том:).+(?=Номер)', metric_block).group()
                vol_num_block.append(f'T. {volume.strip()}')
            if 'Номер' in metric_block:
                number = re.search(r'(?<=Номер:).+', metric_block).group().split()
                number = ''.join(number)
                vol_num_block.append(f'№ {number.strip()}')
            if vol_num_block:
                metric_list.append(', '.join(vol_num_block))
            if 'Страницы' in metric_block:
                pages = re.search(r'(?<=Страницы:).+', metric_block).group()
                metric_list.append(f'C. {pages.strip()}')
        if len(metric_list) < 1:
            metric_list.append('метрические данные не найдены')
        else:
            metric_list = [element.replace('\xa0', ' ') for element in metric_list]
    else:
        metric_list.append('метрические данные не найдены')

    if soup.find('td', width='504'):
        if soup.find('td', width='504').find('a'):
            journal = soup.find('td', width='504').find('a').get_text().lower().capitalize()
        else:
            journal = 'Журнал не найден'
    else:
        journal = 'Журнал не найден'

    if len(authors["authors"]) > 4:
        citation = (f'{title} / {", ".join(authors["authors_reversed"][:3])} [и др.]. – Текст : непосредственный // '
                  f'{journal}. – {". – ".join(metric_list)}.')
    elif len(authors["authors"]) == 4:
        citation = (f'{title} / {", ".join(authors["authors_reversed"])}. – Текст : непосредственный // '
                  f'{journal}. – {". – ".join(metric_list)}.')
    elif 4 > len(authors["authors"]) and authors["authors"]:
        citation = (f'{authors["authors"][0]} {title} / {", ".join(authors["authors_reversed"])}. – '
                    f'Текст : непосредственный // {journal}. – {". – ".join(metric_list)}.')
    else:
        citation = (f'{title}. – Текст : непосредственный // '
                  f'{journal}. - {". – ".join(metric_list)}.')
    return citation

def get_conference(soup):
    authors = get_authors(soup)
    title = get_title(soup)
    if soup.find('div', style='width:580px; margin:0; border:0; padding:0; '):
        metric_block = soup.find('div', style='width:580px; margin:0; border:0; padding:0; ').find_all(
            'table', width='550', recursive=False)
        start_block = metric_block[0]
        start_index = metric_block.index(start_block)
        for block in metric_block:
            if 'источник' in block.get_text(strip=True).lower():
                start_block = block
                start_index = metric_block.index(start_block)
        if re.search(r'(?<=<br/>).+', str(metric_block[start_index + 1])):
            place_date = re.search(r'(?<=<br/>).+', str(metric_block[start_index + 1])).group()
        else:
            place_date = ''
        if re.search(r'.+(?=Издательство)', metric_block[start_index].get_text()):
            conf_name2 = re.search(r'.+(?=Издательство)', metric_block[start_index].get_text()).group()
        else:
            conf_name2 = ''
        if re.search(r'\d{4}', conf_name2):
            if conf_name2.split()[-2] == place_date.split()[0]:
                place_year = re.search(r'[,|\\.]\s[А-Я][а-я]+.+\d{4}', conf_name2).group()
                conf_name2 = conf_name2.replace(place_year, f', {place_date}')
            else:
                year = re.search(r'[,|\\.]\s\d{4}', conf_name2).group()
                conf_name2 = conf_name2.replace(year, f', {place_date}')
        else:
            year = ''
            conf_name2 = f'{conf_name2} {place_date}'
        if len(re.findall(r'(?<=>)\D+(?=</a)', str(metric_block[start_index]))) == 2:
            conf_n_publ = re.findall(r'(?<=>)\D+(?=</a)', str(metric_block[start_index]))
            conf_name1 = conf_n_publ[0].lower().capitalize()
            publisher = conf_n_publ[1]
        elif re.findall(r'(?<=>)\D+(?=</a)', str(metric_block[start_index])):
            conf_name1 = re.search(r'(?<=>)\D+(?=</a)',
                                   str(metric_block[start_index])).group().lower().capitalize()
            publisher = re.search(r'(?<=f\">)\D+(?=</font)', str(metric_block[start_index])).group()
        else:
            conf_name1 = ''
            publisher = ''
        if place_date:
            place = place_date.split()[0].strip(',')
        else:
            place = ''
    else:
        conf_name1, conf_name2, year, publisher, place = [""] * 5

    if soup.find_all('td', width='574'):
        year = ''
        pages = ''
        year_n_pages = soup.find_all('td', width='574')
        for string in year_n_pages:
            string = string.get_text(strip=True)
            if 'Год' in string:
                year = re.search(r'(?<=Год:).+\d+|(?<=Год издания:).+\d+', string).group()
            if 'Страницы' in string:
                pages = re.search(r'(?<=Страницы:).+[0-9-]+', string).group()
    else:
        year = ''
        pages = ''
    if len(authors["authors"]) > 4:
        citation = (f'{title} / {", ".join(authors["authors_reversed"][:3])} [и др.]. – Текст : непосредственный // '
                  f'{conf_name1} : {conf_name2}. – {place} : {publisher}, {year}. – С. {pages}.')
    elif len(authors["authors"]) == 4:
        citation = (f'{title} / {", ".join(authors["authors_reversed"])}. – Текст : непосредственный // '
                    f'{conf_name1} : {conf_name2}. – {place} : {publisher}, {year}. – С. {pages}.')
    elif authors["authors"] and 4 > len(authors["authors"]):
        citation = (f'{authors["authors"][0]} {title} / {", ".join(authors["authors_reversed"])}. – '
                    f'Текст : непосредственный // {conf_name1} : {conf_name2}. – '
                    f'{place} : {publisher}, {year}. – С. {pages}.')
    else:
        citation = (f'{title}. – Текст : непосредственный // {conf_name1} : {conf_name2}. – '
                    f'{place} : {publisher}, {year}. – С. {pages}.')
    return citation

def get_dissertation(soup, autoref=False):
    author_dict = get_authors(soup)
    author = author_dict['authors'][0]
    if soup.find('div', class_='tooltip'):
        auth_full = soup.find('div', class_='tooltip').find('b').find('font').get_text()
    else:
        auth_full = author_dict['authors_reversed'][0]
    title = get_title(soup)
    art_type, year, speciality, institution, defense_place, locality, pages, degree = [""] * 8
    if soup.find('div', style='width:580px; margin:0; border:0; padding:0; '):
        metric_block = (soup.find('div', style='width:580px; margin:0; border:0; padding:0; ')
                        .find('table', width='580').find_all('tr'))
        metric_list = [i.get_text(strip=True) for i in metric_block if i.get_text()]
        for element in metric_list:
            if 'Тип' in element:
                art_type = re.search(r'(?<=Тип:).+(?=Год)', element).group()
            if 'Год' in element:
                year = re.search(r'(?<=Год:)[0-9]+', element).group()
            if 'Специальность' in element:
                speciality = re.search(r'(?<=Специальность:).+', element).group().split()
                if len(speciality) > 1:
                    speciality = f'специальность {speciality[0]} "{" ".join(speciality[2:])}"'
                else:
                    speciality = f'специальность {speciality[0]}'
            if 'Место выполнения работы' in element:
                institution = re.search(r'(?<=Место выполнения работы:).+', element).group()
            if 'Место защиты' in element:
                defense_place = re.search(r'(?<=Место защиты:).+', element).group()
            if 'Город' in element:
                locality = re.search(r'(?<=Город:).+(?=[А-Я])', element).group()
            if 'Число страниц' in element:
                pages = re.search(r'(?<=Число страниц:).+', element).group()
            if 'Ученая степень' in element:
                degree_raw = re.search(r'(?<=Ученая степень:).+', element).group().split()
                if len(degree_raw) == 3:
                    degree = f'{degree_raw[0]}а {degree_raw[1]} {degree_raw[2]}'
                else:
                    degree = ' '.join(degree_raw)

    auth_inst = '; '.join([element for element in [auth_full, institution] if element])
    loc_year = ', '.join([element for element in [locality, year] if element])
    au_loc_page = '. – '.join([element for element in [auth_inst, loc_year, pages] if element])
    tit_spec_type = ' : '.join([element for element in [title, speciality, art_type] if element])

    if not autoref:
        citation = (f'{author} {tit_spec_type} на соискание ученой степени {degree} / '
                    f'{au_loc_page} с. – Текст: непосредственный.')
    else:
        citation = (f'{author} {tit_spec_type} на соискание ученой степени {degree} / '
                    f'{au_loc_page} с. – Место защиты: {defense_place}. – Текст: непосредственный.')
    return citation


def get_authors(soup):
    if soup.find_all('div', style='display: inline-block; white-space: nowrap'):
        authors = soup.find_all('div', style='display: inline-block; white-space: nowrap')
        if 'Страницы' not in authors[0].get_text(strip=True):
            authors = [author.get_text(strip=True) for author in authors if 'Страницы' not in author.get_text()]
            authors_reg = (r'[а-яА-ЯёЁ]+\s[А-ЯЁ]. [А-ЯЁ]. [А-ЯЁ].|[а-яА-ЯёЁ]+\s[А-ЯЁ].[А-ЯЁ].[А-ЯЁ].|'
                           r'[а-яА-ЯёЁ]+\s[А-ЯЁ]. [А-ЯЁ].|[а-яА-ЯёЁ]+\s[А-ЯЁ].[А-ЯЁ].|[а-яА-ЯёЁ]+\s[А-ЯЁ].')
            authors = [re.search(authors_reg, author).group() for author in authors if re.search(authors_reg, author)]
            authors_reversed = [(f'{author.split()[1].replace(".", ". ").strip()} '
                                 f'{author.split()[0].lower().capitalize()}') for author in authors]
            authors = [(f'{author.split()[0].lower().capitalize()}, '
                        f'{author.split()[1].replace(".", ". ").strip()}') for author in authors]
        else:
            authors = ''
            authors_reversed = ''
    else:
        authors = ''
        authors_reversed = ''
    return {'authors': authors, 'authors_reversed': authors_reversed}

def get_title(soup):
    if soup.find('td', width='534'):
        title = soup.find('td', width='534').find('b').get_text(strip=True).lower().capitalize()
    else:
        title = 'Название не найдено'
    return title
