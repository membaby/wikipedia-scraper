from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer
from tkinter import filedialog, Tk
import requests, urllib
from bs4 import BeautifulSoup
import pandas as pd
import sys, os, re
import datefinder
from pathlib import Path
import concurrent.futures
import csv
import time
import sys
import logging

root = Tk()
root.withdraw()
queue, scraped, articles = 0, 0, 0

logging.basicConfig(filename="logging.log", filemode='w+', level=logging.DEBUG,
                    format="%(asctime)s;%(levelname)s; %(message)s")


app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle('Wikipedia Scraper')
window.setFixedWidth(600)
window.setFixedHeight(700)
window.move(200, 160)

window_grid, general_grid, filter_grid, q_grid = QGridLayout(), QGridLayout(), QGridLayout(), QGridLayout()
window.setLayout(window_grid)

#display logo
try:
    window.setWindowIcon(QIcon(os.path.join(sys.path[0], 'logo.png')))
    image = QPixmap(os.path.join(sys.path[0], 'logo.png')).scaled(200, 150, Qt.KeepAspectRatio)
    logo = QLabel()
    logo.setPixmap(image)
    logo.setAlignment(Qt.AlignCenter)
    window_grid.addWidget(logo, 0, 0, 1, 2)
except:
    pass

tabs = QTabWidget()
tabstylesheet = '''
    QTabBar::tab:selected {background: gray;}
    QTabBar::tab {padding: 5px; background: lightgray; font-weight: bold; margin-right: 5px; width: 123px; height:20px;}
    QTabBar::tab:hover {background: darkgrey;}
    QTabBar::tab:disabled {background: #e8eaed;}
    QTabWidget>QWidget>QWidget{background: white;}
'''
tabs.setStyleSheet(tabstylesheet)
tabs.resize(300,200)
tab1, tab2 =  QTabWidget(), QTabWidget()
tabs.addTab(tab1, 'General Settings')
tabs.addTab(tab2, 'Filter Results')
window_grid.addWidget(tabs, 1, 0, 1, 2)
tab1.setLayout(general_grid)
tab2.setLayout(filter_grid)

# General Tab
general_list_urls = QListWidget()
general_textbox_views = QLineEdit()
general_textbox_folder = QLineEdit()
general_textbox_thread = QLineEdit()
general_textbox_maxdepth = QLineEdit()
general_textbox_maxretries = QLineEdit()
general_button_load = QPushButton('Load Wikipedia URLs')
general_button_start = QPushButton('Start')
general_button_stop = QPushButton('Stop All')
general_editbox_add = QLineEdit()
general_button_add = QPushButton('Add URL')
general_checkbox_excludeBD = QCheckBox('Exclude pages w/o birth dates')
general_checkbox_excludeIM = QCheckBox('Exclude pages w/o main image')
general_checkbox_excludeDUP = QCheckBox('Exclude duplicates')

msgbox = QLabel('')
msgbox.setAlignment(Qt.AlignCenter)
general_grid.addWidget(msgbox, 0, 0, 1, 4)
general_grid.addWidget(QLabel('Min. Page Views:'), 1, 0)
general_grid.addWidget(general_textbox_views, 1, 1)
general_grid.addWidget(QLabel('Folder Name:'), 2, 0)
general_grid.addWidget(general_textbox_folder, 2, 1)
general_grid.addWidget(QLabel('Max Threads:'), 3, 0)
general_grid.addWidget(general_textbox_thread, 3, 1)
general_grid.addWidget(QLabel('Max Depth:'), 4, 0)
general_grid.addWidget(general_textbox_maxdepth, 4, 1)
general_grid.addWidget(QLabel('Retry Failed Requests:'), 5, 0)
general_grid.addWidget(general_textbox_maxretries, 5, 1)
general_grid.addWidget(QLabel('Options:'), 6, 0)
general_grid.addWidget(general_checkbox_excludeBD, 6, 1)
general_grid.addWidget(general_checkbox_excludeIM, 7, 1)
general_grid.addWidget(general_checkbox_excludeDUP, 8, 1)
general_grid.addWidget(QLabel('Load URLs:'), 9, 0)
general_grid.addWidget(general_button_load, 9, 1, 1, 1)
general_grid.addWidget(general_list_urls, 10, 0, 1, 4)
general_grid.addWidget(general_editbox_add, 11, 0, 1, 2)
general_grid.addWidget(general_button_add, 11, 2, 1, 2)
general_grid.addWidget(general_button_start, 12, 0, 1, 2)
general_grid.addWidget(general_button_stop, 12, 2, 1, 2)

label_queue, label_scraped, label_articles = QLabel('0'), QLabel('0'), QLabel('0')
general_grid.addWidget(QLabel('URLs in Queue:'), 1, 2)
general_grid.addWidget(label_queue, 1, 3)
general_grid.addWidget(QLabel('Scraped URLs:'), 2, 2)
general_grid.addWidget(label_scraped, 2, 3)
general_grid.addWidget(QLabel('Scraped Articles:'), 3, 2)
general_grid.addWidget(label_articles, 3, 3)

# FILTER TAB
filter_editbox_excel, filter_editbox_images = QLineEdit(), QLineEdit()
filter_button_excel, filter_button_images = QPushButton('Locate'), QPushButton('Locate')
filter_list = QListWidget()

filter_msgbox = QLabel('')
filter_msgbox.setAlignment(Qt.AlignCenter)
filter_grid.addWidget(filter_msgbox, 0, 0, 1, 9)
filter_grid.addWidget(QLabel('Excel File:'), 1, 0, 1, 2)
filter_grid.addWidget(filter_editbox_excel, 1, 2, 1, 6)
filter_grid.addWidget(filter_button_excel, 1, 8)
filter_full = QLineEdit()
filter_add = QPushButton('Add')
filter_grid.addWidget(QLabel('Filter Category Path:'), 4, 0, 1, 2)
filter_grid.addWidget(filter_full, 4, 2, 1, 6)
filter_grid.addWidget(filter_add, 4, 8)

filter_grid.addWidget(QLabel('Filter Article Name:'), 5, 0, 1, 2)
filter_article_name_editbox = QLineEdit()
filter_add_article_name = QPushButton('Add')
filter_grid.addWidget(filter_article_name_editbox, 5, 2, 1, 6)
filter_grid.addWidget(filter_add_article_name, 5, 8)
filter_checkbox_DUP = QCheckBox('Exclude Duplicates')
filter_grid.addWidget(filter_checkbox_DUP, 8, 0, 1, 3)
filter_grid.addWidget(filter_list, 9, 0, 1, 9)

filter_export = QPushButton('Export File')
filter_grid.addWidget(filter_export, 10, 0, 1, 9)

# Default Values
general_textbox_thread.setText('3')
general_textbox_views.setText('10000')
general_textbox_folder.setText('General Files')
general_textbox_maxdepth.setText('999')
general_textbox_maxretries.setText('5')

# GUI Functions
def loadURLs():
    general_list_urls.clear()
    files = filedialog.askopenfilenames(parent=root)
    for file in files:
        with open(file, 'r') as f:
            lines = f.read().split('\n')
            for line in lines:
                general_list_addURL(line)
general_button_load.clicked.connect(loadURLs)

def loadExcelFile():
    file = filedialog.askopenfilename(parent=root)
    filter_editbox_excel.setText(file)
filter_button_excel.clicked.connect(loadExcelFile)

def filter_addCategoryPath():
    path = filter_full.text()
    if path:
        filter_list.addItem('[CATEGORY]: ' + path.strip())
        filter_full.setText('')
filter_add.clicked.connect(filter_addCategoryPath)

def filter_addArticleName():
    path = filter_article_name_editbox.text()
    if path:
        filter_list.addItem('[NAME]: ' + path.strip())
        filter_article_name_editbox.setText('')
filter_add_article_name.clicked.connect(filter_addArticleName)

def filter_list_remKeyword():
    listItems = filter_list.selectedItems()
    filter_list.takeItem(filter_list.row(listItems[0]))
filter_list.doubleClicked.connect(filter_list_remKeyword)

def exportNewCSV():
    counters = []
    csv_filename = filter_editbox_excel.text()
    tabs.tabBar().setTabTextColor(1, Qt.green)
    input_file = open(csv_filename, 'r', encoding='utf-8-sig')
    output_file = open(csv_filename.replace('.csv', '_Exported.csv').replace('.csv', '_Exported.csv'), 'a+', newline='', encoding='utf-8-sig')
    reader = csv.reader(input_file)
    filtered_list = []
    images_path = ''
    for item in getListKeys(filter_list):
        if '[CATEGORY]' in item:
            try:
                Criteria = ' _ '.join([x.strip() for x in item.strip('[CATEGORY]:').split('_')])
                if filtered_list:
                    reader = filtered_list
                    filtered_list = []
                for row in reader:
                    images_path = '/'.join(row[8].split('/')[:-1])
                    if not Criteria.lower() in row[9].lower():
                        filtered_list.append(row)
                    else:
                        os.remove(row[8]) if os.path.exists(row[8]) else print('NOT FOUND', row[8])
            except Exception as err:
                print('5', err)
        elif '[NAME]' in item:
            Criteria = item.strip('[NAME]:')
            if filtered_list:
                reader = filtered_list
                filtered_list = []
            for row in reader:
                try:
                    if not Criteria.lower().strip() in row[1].lower():
                        images_path = '/'.join(row[8].split('/')[:-1])
                        print(images_path)
                        filtered_list.append(row)
                    else:
                        os.remove(row[8]) if os.path.exists(row[8]) else print('NOT FOUND', row[8])
                except Exception as err:
                    print('2', err)
    if filter_checkbox_DUP.isChecked():
        if not filtered_list:
            filtered_list = reader
        no_dups = []
        for item in filtered_list:
            try:
                if not any(x[0] == item[0] for x in no_dups):
                    no_dups.append(item)
            except:
                pass
        filtered_list = no_dups
    filter_msgbox.setText('Successfully Exported!')
    df = pd.DataFrame(filtered_list)
    df.to_csv(output_file, index=False, header=False)
    print(images_path)
    if images_path:
        for item in os.listdir(images_path):
            output_file.seek(0)
            if item not in output_file.read():
                print(item)
                os.remove(item) if os.path.exists(item) else print('NOT FOUND', item)
    tabs.tabBar().setTabTextColor(1, Qt.black)


filter_export.clicked.connect(exportNewCSV)


def general_list_addURL(keyword=None):
    global queue
    if not keyword:
        keyword = general_editbox_add.text().strip()
        general_editbox_add.setText('')
    if keyword != '' and keyword not in getListKeys(general_list_urls):
        if 'wiki' in keyword:
            general_list_urls.addItem(keyword.strip())
            queue += 1

general_button_add.clicked.connect(general_list_addURL)

def general_list_remKeyword():
    global queue
    listItems = general_list_urls.selectedItems()
    general_list_urls.takeItem(general_list_urls.row(listItems[0]))
    queue -= 1
general_list_urls.doubleClicked.connect(general_list_remKeyword)

def startProcess():
    msgbox.setText('')
    tabs.tabBar().setTabTextColor(0, Qt.green)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers = 1)
    general_button_start.setEnabled(False)
    general_button_stop.setEnabled(True)
    executor.submit(startScraper)
    print(f"{os.getcwd() + os.sep + general_textbox_folder.text() + os.sep}logging.log")

general_button_start.clicked.connect(startProcess)

executor = ''
category_path = []
stop_all = False
def startScraper():
    global queue, scraped, error, executor, stop_all
    logging.info('Scraper is starting a process')
    scraped = error = 0
    retries = int(general_textbox_maxretries.text()) if general_textbox_maxretries.text() else 0
    headers = {"User-Agent": "PythonWikiScraper/0.1 (https://embaby.xyz/python-scraper/; mah.embaby@outlook.com) requests-library/2.4", "Referer": "https://en.wikipedia.org/",}
    executor = concurrent.futures.ThreadPoolExecutor(max_workers = int(general_textbox_thread.text()))
    os.makedirs(os.getcwd() + os.sep + general_textbox_folder.text(), exist_ok=True)
    os.makedirs(os.getcwd() + os.sep + general_textbox_folder.text() + os.sep + 'images', exist_ok=True)
    stop_all = False

    def WikiTree(url):
        global category_path
        logging.info(f'Function: WikiTree({url})')
        try:
            retries1 = 0
            while True:
                try:
                    r = requests.get(url, headers=headers)
                except:
                    return
                if r.status_code == 200:
                    break
                elif r.status_code == 429:
                    time.sleep(10)
                    retries1 += 1
                elif r.status_code == 404:
                    df = pd.DataFrame([url])
                    df.to_csv(os.getcwd() + os.sep + general_textbox_folder.text() + os.sep + 'wiki.csv', mode='a+', index=False, header=False)
                    return
                if retries1 < retries:
                    retries1 += 1
                    msgbox.setText('Unable to proceed - Retrying |', retries1)
                    logging.error('Unable to proceed - Retrying |', retries1)
                    time.sleep(10)
                    continue
                else:
                    msgbox.setText('Unable to proceed - Request 1 Failed!')
                    logging.error('Unable to proceed - Request 1 Failed!')
                    raise 'Unable to proceed - Request 1 Failed!'
            soup = BeautifulSoup(r.text, 'lxml')
            title = soup.find('h1', id='firstHeading').text
            if 'Category:' in title:
                if general_textbox_maxdepth.text() and len(category_path) == int(general_textbox_maxdepth.text()):
                    return 'STOP'
                if stop_all:
                    return
                msgbox.setText(title)
                logging.info(title)
                if title.replace('Category:', '').strip() in category_path:
                    category_path = category_path[:category_path.index(title.replace('Category:', '').strip())+1]
                else:
                    category_path.append(title.replace('Category:', '').strip())
                category_path.append(title.replace('Category:', '').strip()) if len(category_path) == 0 else True
                scrapeCategory(soup)
            else:
                if executor:
                    time.sleep(0.1)
                    executor.submit(scrapeArticle, url, soup)
        except Exception as err:
            print(err)
            msgbox.setText(err)
            logging.info(err)
    
    def scrapeCategory(soup, Cats=True):
        logging.info(f'Function: scrapeCategory(..., {Cats})')
        global category_path
        if Cats:
            try:
                for item in soup.find_all('div', class_='CategoryTreeItem'):
                    URL = 'https://en.wikipedia.org' + item.find('a')['href']
                    x = category_path.copy()
                    print(URL)
                    wiki = WikiTree(URL)
                    if wiki == 'STOP':
                        break
                    category_path = x
            except:
                pass
        try:
            items = soup.find('div', id='mw-pages').find_all('li')
            for item in items:
                URL = 'https://en.wikipedia.org' + item.find('a')['href']
                WikiTree(URL)
            if len(items) == 200:
                new_page = ''
                if soup.find('div', id='mw-pages').find_all('a')[-1].text == 'next page':
                    new_page = 'https://en.wikipedia.org' + soup.find('div', id='mw-pages').find_all('a')[-1]['href']
                else:
                    for item in soup.find('div', id='mw-pages').find_all('a'):
                        if 'next page' in item:
                            new_page = 'https://en.wikipedia.org' + item['href']
                if new_page:
                    r = requests.get(new_page, headers=headers)
                    soup = BeautifulSoup(r.text, 'lxml')
                    scrapeCategory(soup, False)
        except:
            pass

    def scrapeArticle(url, soup):
        logging.info(f'Function: scrapeArticle({url}, ...)')
        global articles
        try:
            if general_checkbox_excludeDUP.isChecked():
                try:
                    with open(os.getcwd() + os.sep + general_textbox_folder.text() + os.sep + 'wiki.csv', encoding='utf-8-sig') as f:
                        if url in f.read():
                            return
                except:
                    pass
            info_table = soup.find('table', class_='infobox')
            article_born = soup.find('span', class_='bday').text if soup.find('span', class_='bday') else ''
            died = article_born = ''
            if info_table:
                for item in info_table.find_all('tr'):
                    try:
                        if 'Died' in item.text:
                            for date in datefinder.find_dates(item.find('td', class_="infobox-data").text):
                                died = date.strftime('%Y-%m-%d')
                                break
                            if not died:
                                try:
                                    died = re.findall('[0-9][0-9][0-9][0-9]', item.find('td', class_="infobox-data").text)[0]
                                except:
                                    died = ''
                        try:
                            if not article_born and 'Born' in item.text:
                                for date in datefinder.find_dates(item.find('td').text):
                                    article_born = date.strftime('%Y-%m-%d')
                                    break
                                if not article_born:
                                    try:
                                        article_born = re.findall('[0-9][0-9][0-9][0-9]', item.find('td').text)[0]
                                    except:
                                        article_born = ''
                        except:
                            pass
                    except:
                        pass
            article_link = url
            article_name = soup.find('h1', id='firstHeading').text
            msgbox.setText(f'** Article: {article_name}')
            logging.info(f'** Article: {article_name}')
            if not article_born and general_checkbox_excludeBD.isChecked():
                return
            article_died = died
            
            try:
                im = ''
                image = soup.find('td', class_='infobox-image')
                image = soup.find('td', class_='sidebar-image') if not image else image
                im  = soup.find('a', class_='image') if not image else ''
                article_image_url = 'https://en.wikipedia.org/' + image.find('a')['href'] if not im else 'https://en.wikipedia.org/' + im['href']
            except Exception as err:
                print(err)
                article_image_url = ''
            soup.find('table', class_='sidebar').clear() if soup.find('table', class_='sidebar') else True
            n = 0
            article_text = ''
            for text in [x.text for x in soup.find_all('p')]:
                if n == 2:
                    break
                if len(text) > 25:
                    n += 1
                article_text = article_text + text
            article_sentences = re.sub("[\(\[].*?[\)\]]", "", article_text)
            article_sentences = article_sentences.replace('\n', ' ').replace('  ', ' ').strip()


            if not article_image_url and general_checkbox_excludeIM.isChecked():
                return
            try:
                article_categories = ', '.join([x.text for x in soup.find('div', id='mw-normal-catlinks').find_all('li')])
            except:
                article_categories = ''
            if article_image_url:
                retries2 = 0
                while True:
                    try:
                        r = requests.get(article_image_url, headers=headers)
                    except:
                        break
                    if r.status_code == 200:
                        break
                    elif r.status_code == 429:
                        time.sleep(1)
                        retries2 += 1
                    elif r.status_code == 404:
                        return
                    elif retries2 < retries:
                        retries2 += 1
                        msgbox.setText(f'Unable to proceed - Retrying | {retries2}')
                        logging.error(f'Unable to proceed - Retrying | {retries2}')
                        time.sleep(10)
                        continue
                    else:
                        print(r)
                        return
                try:
                    soup = BeautifulSoup(r.text, 'lxml')
                    article_image_url = soup.find('div', id='file').find('a')['href']
                    article_image_url = 'https:' + article_image_url if 'https:' not in article_image_url else article_image_url
                except:
                    article_image_url = ''
            retries3 = 0
            while True:
                try:
                    r = requests.get('https://en.wikipedia.org/w/index.php?title=' + url.split('/')[-1] + '&action=info', headers=headers)
                except:
                    break
                if r.status_code == 200:
                    break
                elif r.status_code == 429:
                    time.sleep(10)
                    retries3 += 1
                elif r.status_code == 404:
                        return
                elif retries3 < retries:
                    retries3 += 1
                    msgbox.setText(f'Unable to proceed - Retrying | {retries3}')
                    logging.error(f'Unable to proceed - Retrying | {retries3}')
                    time.sleep(10)
                    continue
                else:
                    print(r)
                    break
            
            try:
                soup = BeautifulSoup(r.text, 'lxml')
                article_views = soup.find('tr', id='mw-pvi-month-count').find_all('td')[1].text
            except:
                article_views = '0'
            if int(article_views.replace(',', '')) >= int(general_textbox_views.text()):
                try:
                    if article_image_url:
                        extension = '.png' if '.jpg' not in article_image_url else '.jpg'
                        article_image_local = os.getcwd() + os.sep + general_textbox_folder.text() + os.sep + 'images' + os.sep + article_name + extension
                        urllib.request.urlretrieve(article_image_url, article_image_local)
                    else:
                        article_image_local = ''
                except:
                    pass
                data = {
                    'Wikipedia link': article_link,
                    'Name': article_name,
                    'Born': article_born,
                    'Died': article_died,
                    'First 2 sentences': article_sentences,
                    'Main image url': article_image_url,
                    'Page Views (30 days)': article_views,
                    'Categories': article_categories,
                    'Local image': article_image_local,
                    'Article Path': ' _ '.join(category_path)
                }
                with open(os.getcwd() + os.sep + general_textbox_folder.text() + os.sep + 'wiki.csv', 'a+', newline='', encoding='utf-8-sig') as file:
                    df = pd.DataFrame([data])
                    if Path(os.getcwd() + os.sep + general_textbox_folder.text() + os.sep + 'wiki.csv').stat().st_size < 5:
                        df.to_csv(file, index=False)
                    else:
                        df.to_csv(file, index=False, header=False)
                articles += 1
        except Exception as err:
            msgbox.setText(f'ARTICLE ERROR: {err}')
            logging.error(f'ARTICLE ERROR: {err}')
            print(f'ARTICLE ERROR: {err}')
            time.sleep(0.5)

    global category_path
    for url in getListKeys(general_list_urls):
        category_path = []
        WikiTree(url.strip().replace('<ul>', ''))
        scraped += 1
        queue -= 1
    executor.shutdown(wait=True)
    general_button_start.setEnabled(True)
    general_button_stop.setEnabled(False)
    general_list_urls.clear()
    tabs.tabBar().setTabTextColor(0, Qt.black)
    msgbox.setText('Completed!')
def stopAll():
    try:
        global executor, stop_all
        general_button_stop.setEnabled(False)
        executor.shutdown(wait=True)
        stop_all = True
        general_button_start.setEnabled(True)

        for i in range(scraped):
            general_list_urls.takeItem(i)
        msgbox.setText('Stopped!')
    except:
        pass
general_button_stop.clicked.connect(stopAll)

def getListKeys(list):
    items = []
    for x in range(list.count()):
        items.append(list.item(x).text())
    return items


def updateStatus():
    label_queue.setText(str(queue))
    label_scraped.setText(str(scraped))
    label_articles.setText(str(articles))

timer = QTimer(window)
timer.timeout.connect(updateStatus)
timer.start(1000)


if __name__ == "__main__":
    window.show()
    sys.exit(app.exec())