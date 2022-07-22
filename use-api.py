import requests
import json
import prettytable


def find_more_years(start_year, end_year, number):
    headers = {'Content-type': 'application/json'}
    data = json.dumps({"seriesid": ['CUUR0000SA0'], "startyear": str(start_year), "endyear": str(end_year)})
    p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
    json_data = json.loads(p.text)
    for series in json_data['Results']['series']:
        x = prettytable.PrettyTable(["series id", "year", "period", "value", "footnotes"])
        seriesId = series['seriesID']
        for item in series['data']:
            year = item['year']
            period = item['period']
            value = item['value']
            footnotes = ""
            for footnote in item['footnotes']:
                if footnote:
                    footnotes = footnotes + footnote['text'] + ','
            if 'M01' <= period <= 'M12':
                x.add_row([seriesId, year, period, value, footnotes[0:-1]])
        output = open(seriesId + '.csv', 'a')
        output.write(x.get_string())
        output.close()


def solution():
    start_year = 1900
    end_year = 2022
    if end_year - start_year > 9:
        times = (end_year - start_year) // 10
        rest = (end_year - start_year) % 10
        last_start = end_year - rest
        # 倒序排序
        find_more_years(last_start, end_year, 1)
        while times > 0:
            find_more_years(last_start - 10, last_start - 1, 0)
            last_start -= 10
            times -= 1
    else:
        find_more_years(start_year, end_year, 1)


solution()



# 修改大数据量的csv文件
# import pandas as pd
#
# df = pd.read_csv('/Users/yuwenxiang/Desktop/no12.csv')
# df_new = df.drop(['web-scraper-start-url'], axis=1)
# df_new = df_new.drop(['web-scraper-order'], axis=1)
# # df_new = df_new.rename(columns=({'web-scraper-order': 'category'}))
# df_new.insert(0, "category", ['Occupational injuries and illnesses industry data'] * 866828)
# df_new.to_csv("/Users/yuwenxiang/Desktop/no12_new.csv", index=0)