from pathlib import Path
import re



base_folder = Path(__file__).resolve().parent

def citation_dump(citation):
    with open(base_folder.joinpath("bibliography.txt"), "a", encoding="UTF-8") as bibliography:
        bibliography.write(f'{citation}\n')


def clean_bibliography():
    with open(base_folder.joinpath("bibliography.txt"), "w", encoding="UTF-8") as bibliography:
        pass
    with open(base_folder.joinpath("urls.txt"), "w", encoding="UTF-8") as urls:
        pass


def url_save(url):
    with open(base_folder.joinpath("urls.txt"), "a", encoding="UTF-8") as urls:
        urls.write(f'{url}\n')


def get_urls():
    with open(base_folder.joinpath("urls.txt"), "r", encoding="UTF-8") as urls:
        return urls.read()


def counter():
    if base_folder.joinpath("bibliography.txt").exists():
        with open(base_folder.joinpath("bibliography.txt"), "r", encoding="utf-8") as f:
            temp_bibl = f.readlines()
            if len(temp_bibl) > 0 and re.search(r'\d+(?=\.[А-ЯЁ])', temp_bibl[0]):
                num_list = [int(re.search(r'\d+(?=\.[А-ЯЁ])', art).group()) for art in temp_bibl
                            if re.search(r'[0-9]+', art[0])]
                return max(num_list) + 1
            else:
                return 1
    else:
        return 'библиография не найдена'
