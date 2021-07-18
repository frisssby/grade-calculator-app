from bs4 import BeautifulSoup
import pandas as pd
import re
import requests
from copy import deepcopy
from grade import Grade

MAX_NUM_PAGES = 10
year = 2020
OK_RESPONSE_STATUS = 200


# scaping courses' names and links to their pages

course_names = []
course_links = []

for page_num in range(MAX_NUM_PAGES):
    url = f'https://www.hse.ru/ba/ami/courses/page{page_num}.html?year={year}'
    try:
        response = requests.get(url, timeout=20)
    except:
        break
    if response.status_code != OK_RESPONSE_STATUS:
        break

    soup = BeautifulSoup(response.content, 'html.parser')
    courses = soup.find_all('a', 'link link_dark')

    # stop if there are no courses on page

    if not courses:
        break

    page_course_names = [course.text.strip() for course in courses]
    page_course_links = [course['href'] for course in courses]

    assert(len(page_course_names) == len(page_course_links))

    course_names += page_course_names
    course_links += page_course_links

# creating pandas.DataFrame with scraped data

df = pd.DataFrame(
    {
        'name': course_names,
        'link': course_links
    }
)

df = df.drop_duplicates(subset='name')
df = df.set_index('name')

# for each course scrape info about assessment criteria

row_soups = []
for row in df.iloc:  # saving html soups for each course
    try:
        row_response = requests.get(row.link, timeout=20)
    except:
        break
    if response.status_code != OK_RESPONSE_STATUS:
        break

    row_soups.append(BeautifulSoup(row_response.content, 'html.parser'))

formulas = []
for row_soup in row_soups:  # finding assessment formula on a course page
    pud_sections = row_soup.find_all('div', 'pud__section')
    assessment_section = None
    for section in pud_sections:
        img = section.find('img', alt=True)
        if img and img['alt'] in ['Промежуточная аттестация', 'Interim Assessment']:
            assessment_section = section
            break
    # if no info about assessment put None value
    if not assessment_section:
        formulas.append(None)
        continue
    formula = assessment_section.find_all('div', 'grey')[-1].text.strip()
    formulas.append(formula)

# adding a formula column to DataFrame

df['raw_formula'] = formulas

# dropping courses without assessment info

df = df.dropna()

# cleaning formulas from xhtml tags and deleting extra characters


def clean(s: str) -> str:
    html_tags_clean_pattern = re.compile(
        '<[^а-я]*?>|&(\w+|#\d{1,6}|#x[\da-f]{1,6});'
    )
    res = re.sub(html_tags_clean_pattern, '', s)
    return res.replace('\n', ' ').replace('\t', ' ')


df['formula'] = df['raw_formula'].apply(lambda s: clean(s))
df = df.drop(columns='raw_formula')

# choosing rows with formula no more than 200 characters

df_short = deepcopy(df[df.formula.map(len) <= 200])

# creating Grade objects from string formulas

grades = []
for row in df_short.iloc:
    grades.append(Grade.from_string(row.formula))
df_short['grade'] = grades

# saving DataGrame to pickle file

df_short.to_pickle('assessment_db.pkl')
