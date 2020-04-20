"""
processes data in archives-text into data readable by cloudsearch
outputs JSON data.

processes data in 5mb chunks (the max/optimal chunk size for cloudsearch
requests)

see `docs/search.md` for a description of the fields

ref https://github.com/awsdocs/amazon-cloudsearch-developer-guide/blob/master/doc_source/preparing-data.md#creating-document-batches

important: need to make sure that special characters are properly escaped.

todo:

create a script to find all of the author titles

should probably define a class to read over data in a certain
directory. For example, objects can be defined with a year to process
and then will process all documents in that year

this object can also keep track of total data stored, s.t. it doesn't exceed 5 MB

this object will have a function process_next_article_data() which will do just that
and if this data doesn't put the total data over 5 MB, then it will tack it on
Otherwise, it will write current data to a file, and then clear that data, and start
new data collection starting with this current article data.
"""

import os
import re

# You need to set this
ARCHIVES_TEXT_PATH = "PATH_TO_ARCHIVES_TEXT_DIRECTORY"

VALID_ARTICLE_TYPES = ['article', 'advertisement',]
VALID_AUTHOR_TITLES = ['','DESK EDITOR',]

# see here for limits https://github.com/awsdocs/amazon-cloudsearch-developer-guide/blob/master/doc_source/limits.md
MAX_BATCH_SIZE = 5242880 # 5 MB
MAX_FILE_SIZE = 1048576 # 1 MB

def checkDate(date):
    if(not isinstance(date['year'], int)):
        return False
    if(not isinstance(date['month'], int)):
        return False
    if(not isinstance(date['day'], int)):
        return False
    return True    

"""
articleDate is a dict {year: int, month: int, day: int}. cloudsearch needs this format: yyyy-mm-ddTHH:mm:ss.SSSZ 
"""
def create_article_fields(articleText, articleType, articleNumber, publishDate, 
                             title="", subtitle="",author="",authorTitle=""):
    if(articleType not in VALID_ARTICLE_TYPES):
        print(f'{articleType} not a valid article type. Article Number: {articleNumber} Date: {publishDate}')
        return
    if(authorTitle not in VALID_AUTHOR_TITLES):
        print(f'{authorTitle} not a valid author title. Article Number: {articleNumber} Date: {publishDate}')
        return
    if(not isinstance(articleNumber, int)):
        print(f'{articleNumber} not an int. Article Number: {articleNumber} Date: {publishDate}')
        return
    if(not checkDate(publishDate)):
        print(f'{publishDate} not a valid date. Article Number: {articleNumber} Date: {publishDate}')
        return
    fields = {
        "article-text": articleText,
        "article-type": articleType,
        "article-number": articleNumber,
        "publish-date": f'{str(publishDate["year"]).zfill(4)}-{str(publishDate["month"]).zfill(2)}-{str(publishDate["day"]).zfill(2)}T12:00:00Z', # default set time to 12:00, since we don't care about that.
        "title": title, # perhaps just don't include this if field is empty?
        "subtitle": subtitle,
        "author": author,
        "author-title": authorTitle,
    }
    return fields

def get_archives_years():
    entries = os.listdir(ARCHIVES_TEXT_PATH)
    for i in range(0, len(entries)):
        try: 
            entries[i] = int(entries[i])
        except:
            continue
    return entries

def get_archives_months(year):
    entries = os.listdir(ARCHIVES_TEXT_PATH + str(year).zfill(4) + "/")
    for i in range(0, len(entries)):
        try: 
            entries[i] = int(entries[i])
        except:
            continue
    return entries

def get_archives_days(year, month):
    entries = os.listdir(ARCHIVES_TEXT_PATH + str(year).zfill(4) + "/" + str(month).zfill(2) + "/")
    for i in range(0, len(entries)):
        try: 
            entries[i] = int(entries[i])
        except:
            continue
    return entries

def get_archives_article_filenames(year, month, day):
    entries = os.listdir(ARCHIVES_TEXT_PATH + str(year).zfill(4) + "/" + str(month).zfill(2) + "/" + str(day).zfill(2))
    for i in range(0, len(entries)):
        try: 
            entries[i] = int(entries[i])
        except:
            continue
    return entries

"""
returns a dict containing article data
"""
def get_article_data(year, month, day, filename):
    with open(ARCHIVES_TEXT_PATH + str(year).zfill(4) + "/" + str(month).zfill(2) + "/" + str(day).zfill(2) + "/" + filename, 'r') as f:
        articleData = f.read()
        articleLines = articleData.splitlines()
        if(not articleLines[0].startswith('#')):
            print("error in first line of article", year, month, day, filename)
        if(not articleLines[1].startswith('##')):
            print("error in second line of article", year, month, day, filename)
        if(not articleLines[2].startswith('###')):
            print("error in third line of article", year, month, day, filename)
        title = articleLines[0][2:]
        subtitle = articleLines[1][3:]
        author = articleLines[2][4:]
        articleText = ""
        articleText = articleText.join(articleLines[3:])
        
        filename_parts = filename.split('.')
        articleType = filename_parts[1]
        temp = re.findall(r'\d+', filename_parts[0]) 
        articleNumber = list(map(int, temp))[0]

        articleData = {
            'articleText': articleText.strip(),
            'articleType': articleType.strip(),
            'articleNumber': articleNumber,
            'publishDate': {'year': year, 'month': month, 'day': day},
            'title': title.strip(),
            'subtitle': subtitle.strip(),
            'author': author.strip(),
            'authorTitle': '', # authorTitle not yet implemented.
        }
        return articleData

def pretty_print_article_fields(article_fields):
    print("----------------------------------------------------------")
    print("title:", article_fields['title'])
    print("subtitle:", article_fields['subtitle'])
    print("author:", article_fields['author'])
    print("author-title:", article_fields['author-title'])
    print("article-type:", article_fields['article-type'])
    print("article-number:", article_fields['article-number'])
    print("publish-date:", article_fields['publish-date'])
    print("text sample:", article_fields['article-text'][0:40])
    print("----------------------------------------------------------")

def generate_lots_article_data():
    archives_years = get_archives_years()
    archives_months = get_archives_months(archives_years[0])
    archives_days = get_archives_days(archives_years[0], archives_months[0])
    article_names = get_archives_article_filenames(archives_years[0], archives_months[0], archives_days[0])
    for article_name in article_names:
        article_data = get_article_data(archives_years[0], archives_months[0], archives_days[0], article_name)
        article_fields = create_article_fields(**article_data)
        pretty_print_article_fields(article_fields)

def tests():
    archives_years = get_archives_years()
    archives_months = get_archives_months(archives_years[0])
    archives_days = get_archives_days(archives_years[0], archives_months[0])
    article_names = get_archives_article_filenames(archives_years[0], archives_months[0], archives_days[0])
    article_data = get_article_data(archives_years[0], archives_months[0], archives_days[0], article_names[0])
    article_fields = create_article_fields(**article_data)
    pretty_print_article_fields(article_fields)
    generate_lots_article_data()

def main():
    tests()

if __name__ == '__main__':
    main()