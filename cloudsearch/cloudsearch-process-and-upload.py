"""
Designed to be run in parallel, uploads processed archives-text
data in 5 mb batches

designed to be run in the cloudsearch/ directory
"""

import boto3
import os
import re

DOC_ENDPOINT = "https://doc-dev-alex-j7lgucvvgtchzkfv7dze2su4ey.us-east-1.cloudsearch.amazonaws.com"
# perhaps have this as a class variable
doc_client = boto3.client('cloudsearchdomain', endpoint_url=DOC_ENDPOINT)

MAX_BATCH_SIZE = 5242880 # 5 MB
MAX_FILE_SIZE = 1048576 # 1 MB

ARCHIVES_TEXT_PATH = "./archives-text/"
LOG_PATH = "./logs/"

VALID_ARTICLE_TYPES = ['article', 'advertisement',]
VALID_AUTHOR_TITLES = ['', 'SENIOR STAFF WRITER', 'STAFF WRITER', 'DESK EDITOR', 'CONTRIBUTING WRITER', 
'MANAGING EDITOR', 'EDITOR IN CHIEF', 'DEPUTY EDITOR', 'EXECUTIVE EDITOR', 'STAFF', 
'ASSU President', 'ASSU Parlimentarian', 'STAFF FOOTBALL WRITERS', 'FASHION COLUMNIST', 
'FOOTBALL EDITOR', 'ARTS EDITOR', 'FOOD EDITOR', 'FOOD DINING EDITOR', 'OPINIONS DESK',
'FOOD DRUNK EDITOR', 'FELLOW', 'DAILY INTERN', 'CONTRIBUTING EDITOR', 'MANAGING WRITER',
'GUEST COLUMNIST', 'SEX GODDESS', 'GUEST COLUMNISTS', 'EDITORIAL STAKE', 'CONTRIBUTING YANKEE',
'SPECIAL CONTRIBUTOR', 'EDITORIAL BOARD', 'CONTRIBUTING WRITER', 'EDITORIAL STAFF', 'FILM CRITIC',
'HEALTH EDITOR', 'ASSHOLE', 'INTERMISSION', 'NEWS EDITOR', 'CLASS PRESIDENT', 'ASSOCIATED PRESS',
'AP SPORTS WRITER', 'AP BASEBALL WRITER', 'WEEKLY COLUMNIST', 'HEALTH COLUMNIST', 'ASSOCIATED EDITOR',
'ASSOCIATE EDITOR', 'SPORTS EDITOR', 'EDITOR THE DAILY', ]

class Logger:
    def __init__(self, path, basename):
        self.fullpath = path + basename + '.log'
        self.f = open(self.fullpath, 'w')

    def log(self, message):
        f.write(message)

    def get_fullpath(self):
        return self.fullpath

    def __del__(self):
        self.f.close()

class ArchivesTextProcessor:
    def __init__(self, base_path, startYear, endYear, batchSize, docClient):
        self.base_path = base_path
        self.startYear = startYear
        self.endYear = endYear
        self.batchSize = batchSize
        self.docClient = docClient
        self.currentSizeInBytes = 0
        self.logger = Logger(LOG_PATH, str(startYear))
        print(f"logs outputted to {self.logger.get_fullpath()}")

        # initialize some data
        self.years_left = list(range(startYear, endYear))
        self.currentYear = None
        self.move_to_next_year()
        self.months_left_in_year = None
        self.set_months_left_in_year()
        self.currentMonth = None
        self.move_to_next_month()
        self.days_left_in_month = None
        self.set_days_left_in_month()
        self.currentDay = None
        self.move_to_next_day()
        self.articles_left_in_day = None
        self.set_articles_left_in_day()
        self.currentArticle = None
        self.move_to_next_article()

    def __del__(self):
        del self.logger
    """
    the following are functions to help us iterate through the files in archives-text
    """

    def get_current_path(self, level):
        if(level == 'year'):
            return self.base_path + str(self.currentYear).zfill(4) + "/"
        elif(level == 'month'):
            return self.base_path + str(self.currentYear).zfill(4) + "/" + str(self.currentMonth).zfill(2) + "/"
        elif(level == 'day'):
            return self.base_path + str(self.currentYear).zfill(4) + "/" + str(self.currentMonth).zfill(2) + "/" + str(self.currentDay).zfill(2) + "/"
        elif(level == 'article'):
            return self.base_path + str(self.currentYear).zfill(4) + "/" + str(self.currentMonth).zfill(2) + "/" + str(self.currentDay).zfill(2) + "/" + self.currentArticle
        else:
            self.logger.log(f"ERROR: {level} is an invalid level")

    def set_months_left_in_year(self):
        months = os.listdir(self.get_current_path("year"))
        filtered_months = []
        for i in range(0, len(months)):
            try:
                filtered_months.append(int(months[i]))
            except:
                continue
        filtered_months.sort()
        self.months_left_in_year = filtered_months

    def set_days_left_in_month(self):
        days = os.listdir(self.get_current_path("month"))
        filtered_days = []
        for i in range(0, len(days)):
            try:
                filtered_days.append(int(days[i]))
            except:
                continue
        filtered_days.sort()
        self.days_left_in_month = filtered_days

    def set_articles_left_in_day(self):
        articles = os.listdir(self.get_current_path("day"))
        filtered_articles = []
        for i in range(0, len(articles)):
            try:
                filtered_articles.append(articles[i])
            except:
                continue
        filtered_articles.sort()
        self.articles_left_in_day = filtered_articles
        
    # returns -1 if we can't move anymore (i.e. we're done), 1 on success
    def move_to_next_year(self):
        if(len(self.years_left) == 0):
            self.logger.log("done")
            print("DONE!!")
            return -1
        else:
            self.currentYear = self.years_left.pop()
            return 1

    # returns -1 if we can't move anymore (i.e. we're done), 1 on success
    def move_to_next_month(self):
        while(len(self.months_left_in_year) == 0):
            if(self.move_to_next_year() < 0):
                return -1
            self.set_months_left_in_year()
        self.currentMonth = self.months_left_in_year.pop()
        return 1
        
    # returns -1 if we can't move anymore (i.e. we're done), 1 on success
    def move_to_next_day(self):
        while(len(self.days_left_in_month) == 0):
            if(self.move_to_next_month() < 0):
                return -1
            self.set_days_left_in_month()
        self.currentDay = self.days_left_in_month.pop()
        return 1

    def move_to_next_article(self):
        while(len(self.articles_left_in_day) == 0):
            if(self.move_to_next_day() < 0):
                return -1
            self.set_articles_left_in_day()
        self.currentArticle = self.articles_left_in_day.pop()
        return 1
    
    """
    the following are functions to process data in the .txt files in archives-text
    """
    def get_current_publish_date(self):
        return f'{str(self.currentYear).zfill(4)}-{str(self.currentMonth).zfill(2)}-{str(self.currentDay).zfill(2)}T12:00:00Z' # default set time to 12:00, since we don't care about that.

    def get_current_article_data(self):
        with open(self.get_current_path('article'), 'r') as f:
            articleRawText = f.read()
            articleLines = articleRawText.splitlines()

            # perform some sanity checks 
            if(not articleLines[0].startswith('#')):
                self.logger.log(f"error in first line of article {self.get_current_path('article')}")
            if(not articleLines[1].startswith('##')):
                self.logger.log(f"error in second line of article {self.get_current_path('article')}")
            if(not articleLines[2].startswith('###')):
                self.logger.log(f"error in third line of article {self.get_current_path('article')}")

            # extract data
            title = re.sub('\s+', ' ', articleLines[0][2:].strip()) # get rid of extra whitespace, plus skip extra chars
            subtitle = re.sub('\s+', ' ', articleLines[1][3:].strip()) 
            author_raw = re.sub('\s+', ' ', articleLines[2][4:].strip())

            author = author_raw
            authorTitle = ''
            for possibleTitle in VALID_AUTHOR_TITLES:
                title_index = author_raw.upper().find(possibleTitle)
                if(title_index > 0):
                    authorTitle = possibleTitle
                    author = author[0:title_index]
                    break

            articleText = ''
            articleText = articleText.join(articleLines[3:]).strip()

            filename_parts = self.currentArticle.split('.')
            articleType = filename_parts[1]
            articleNumber = filename_parts[0]

            return {
                'article_text': articleText,
                'article_type': articleType,
                'article_number': articleNumber,
                'title': title,
                'subtitle': subtitle,
                'author': author,
                'author_title': authorTitle,
                'publish_date': self.get_current_publish_date()
            }

    def pretty_print_current_article_data(self):
        current_article_data = self.get_current_article_data()
        print("----------------------------------------------------------")
        print("title:", current_article_data['title'])
        print("subtitle:", current_article_data['subtitle'])
        print("author:", current_article_data['author'])
        print("author_title:", current_article_data['author_title'])
        print("article_type:", current_article_data['article_type'])
        print("article_number:", current_article_data['article_number'])
        print("publish_date:", current_article_data['publish_date'])
        print("text sample:", current_article_data['article_text'][0:40])
        print("----------------------------------------------------------")

def tests():
    print("tests:")
    testProcessor = ArchivesTextProcessor(ARCHIVES_TEXT_PATH, 2013, 2014, MAX_BATCH_SIZE, doc_client)
    for i in range(100):
        print(testProcessor.get_current_path('article'))
        testProcessor.pretty_print_current_article_data()
        testProcessor.move_to_next_article()
    print("if you compare with https://github.com/TheStanfordDaily/archives-text/tree/master/1899/12 you should see matching results")

def main():
    tests()

if __name__ == '__main__':
    main()