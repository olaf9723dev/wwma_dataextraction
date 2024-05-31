import csv
import requests
import os
from bs4 import BeautifulSoup
HOME_URL = 'https://www.yelp.com'
MAIN_URL = 'https://www.yelp.com/search?find_desc={}&find_loc=Nanaimo%2C+BC%2C+Canada';

class DataExtractor:
    def __init__(self) -> None:
        self.urls=[]
        try:
            os.mkdir('output')
            with open('output/result.csv', 'w') as file:
                file.write("")
        except FileExistsError:
            pass
    def get_request(self, url):
        try:
            session = requests.Session()
            response = session.get(url)
            return response
        except Exception as e:
            print(e)
    
    def get_search_urls(self):
        content = self.get_request(MAIN_URL).text
        soup_page = BeautifulSoup(content, 'html.parser')
        menu_elements = soup_page.find('nav', attrs={'aria-label':'Business categories'}).find_all('div', class_ = 'header-nav_unit header-nav_unit__09f24__pRjEN undefined css-1jq1ouh')
        for menu in menu_elements:
            for item in menu.find_all('a', attrs = {'data-testid':'menu-item-tag'}):
                self.urls.append(item.get_text())

    def get_data(self):
        for index, url in enumerate(self.urls):
            print("Category num" + str(index + 1))
            content = self.get_request(MAIN_URL.format(url)).text
            soup_page = BeautifulSoup(content, 'html.parser')
            category = url
            pagination = soup_page.find('div', attrs={'aria-label':'Pagination navigation'})
            if(pagination):
                page_num = len(pagination.find_all('div', class_='css-1qn0b6x'))-2
            else:
                page_num=1
            for page in range(1, page_num):
                print("Page num" + str(page))
                content = self.get_request(MAIN_URL.format(url) + "&start=" + str((page - 1)*10)).text
                soup_page = BeautifulSoup(content, 'html.parser')
                detail_urls = soup_page.select('.businessName__09f24__HG_pC > div > h3 > a')
                for detail_url in detail_urls:
                    self.get_detail_info(HOME_URL + detail_url['href'], category, detail_url.get_text())

    def get_detail_info(self, detail_url, category, name):
        data=dict()
        content = self.get_request(detail_url).text
        soup_page = BeautifulSoup(content, 'html.parser')
        data['Category'] = category
        data['Vendor'] = name

        for element in soup_page.select('aside > section > div .css-djo2w'):
            if(element.select_one('.css-hmsl4n > :nth-child(2) > :nth-child(1)').get_text() == 'Get Directions'):
                origin_address = element.select_one('.css-hmsl4n > :nth-child(2) > :nth-child(2)').get_text()
                data['Address'] = str(origin_address).split(' Nanaimo')[0]
                data['City'] = 'Nanaimo'
                data['Province'] = 'BC'
                data['Postal'] = str(origin_address).split('BC ')[1].replace(' Canada', '').replace(' ', '')
            if(element.select_one('.css-hmsl4n > :nth-child(2) > :nth-child(1)').get_text() == 'Phone number'):
                data['Phone'] = element.select_one('.css-hmsl4n > :nth-child(2) > :nth-child(2)').get_text()
        data['username'] = ''
        data['email'] = ''
        data['type'] = ''
        data['contact'] = ''
        data['position'] = ''
        data['logo'] = ''
        data['subdomain'] = ''
        self.save_info_csv(data)        
        print(detail_url)

    def save_info_csv(self, data):
        with open('output/result.csv', 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data.keys())
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow(data)

def main():
    data_extractor = DataExtractor()
    data_extractor.get_search_urls()
    data_extractor.get_data()

if __name__ == "__main__":
    main()