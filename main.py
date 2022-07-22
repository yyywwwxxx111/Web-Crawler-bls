import copy

import requests
import pandas as pd
from bs4 import BeautifulSoup


def main():
    html = requests.get('https://beta.bls.gov/dataQuery/find?')
    html.encoding = 'utf-8'

    soup = BeautifulSoup(html.text, 'lxml')
    # title
    soup_parent = soup.select('#dq-facets > h2')
    # subtitle
    soup_children = soup.select('#dq-facets > .dq-facets-container')
    data = []
    # len(soup_parent)
    # measures
    for i in range(2, 3):
        total = []
        category = [soup_parent[i].text]
    # print(soup_parent[i].text)
        soup_child = soup_children[i].select('a')
    # measure attribute
        for j in soup_child:
            # subtitle and link
            # print(j.text.strip(), j['href'])
            if j.text.strip() != 'Occupational Employment and Wage Statistics':
                category.append(j.text.strip())
                find_third_level(j['href'], i, category, total, data)
                category.pop()

    df = pd.DataFrame(data, columns=['Category1', 'Category2', 'Category3', 'Category4', 'Series', 'Name'], dtype=str)
    df.to_csv('site.csv')


def find_third_level(link, i, category, total, data):
    if i != 2:
        next_html = requests.get('https://beta.bls.gov/dataQuery/' + link)
        next_html.encoding = 'utf-8'
        soup_next_page = BeautifulSoup(next_html.text, 'lxml')
        # third_level
        soup_third_level = soup_next_page.select('.dq-facets-toggle-h4 a')
        for each_third_level in soup_third_level:
            # print(each_third_level.text.strip(), each_third_level['href'])
            category.append(each_third_level.text.strip())
            find_four_level(each_third_level['href'], category, total, data)
            category.pop()

    category.append('')
    category.append('')
    find_series(link, category, total, data)
    category.pop()
    category.pop()


def find_four_level(link, category, total, data):
    next_html = requests.get('https://beta.bls.gov/dataQuery/' + link)
    next_html.encoding = 'utf-8'
    soup_next_page = BeautifulSoup(next_html.text, 'lxml')
    # four_level
    soup_four_level = soup_next_page.select('.dq-facets-container .dq-facets-toggle-h4 .dq-facets-toggle-h4 a')
    for each_four_level in soup_four_level:
        # print(each_four_level.text.strip(), each_four_level['href'])
        category.append(each_four_level.text.strip())
        find_series(each_four_level['href'], category, total, data)
        category.pop()


def find_series(link, category, total, data):
    now_link = 'https://beta.bls.gov/dataQuery/find?st={}&r=20' + link[14:]
    html = requests.get(now_link)
    html.encoding = 'utf-8'
    soup_page = BeautifulSoup(html.text, 'lxml')
    pages = soup_page.select('#dq-num-results-wrapper strong')
    page_last = pages[1].string
    # for page in range(0, int(page_last), 20):
    for page in range(0, int(page_last), 20):
        r = requests.get(f'https://beta.bls.gov/dataQuery/find?st={page}&r=20' + link[14:])
        content = r.text
        soup = BeautifulSoup(content, 'html.parser')
        rows = soup.select('.dq-result-item .dq-button-catalog')
        names = soup.select('.dq-result-item a')

        for i in range(len(rows)):
            category.append(rows[i]['id'])
            category.append(names[i].text.strip())
            new_category = copy.deepcopy(category)
            total.append(new_category)
            category.pop()
            category.pop()
    print(total)
    data.extend(copy.deepcopy(total))
    total.clear()
    # todo
    # use pandas to store data and link to csv
    # print(data)


main()
import requests
import json
import prettytable
headers = {'Content-type': 'application/json'}
data = json.dumps({"seriesid": ['CUUR0000SA0','SUUR0000SA0'],"startyear":"2011", "endyear":"2014"})
p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
json_data = json.loads(p.text)
for series in json_data['Results']['series']:
    x=prettytable.PrettyTable(["series id","year","period","value","footnotes"])
    seriesId = series['seriesID']
    for item in series['data']:
        year = item['year']
        period = item['period']
        value = item['value']
        footnotes=""
        for footnote in item['footnotes']:
            if footnote:
                footnotes = footnotes + footnote['text'] + ','
        if 'M01' <= period <= 'M12':
            x.add_row([seriesId,year,period,value,footnotes[0:-1]])
    output = open(seriesId + '.txt','w')
    output.write (x.get_string())
    output.close()



