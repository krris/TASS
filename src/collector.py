#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import os
import re
from bs4 import BeautifulSoup

__author__ = 'krris'

directory = 'users'
data_dir = '../data/'
book_list_dir = 'books/'

def login():
    session = requests.Session()
    url = 'http://lubimyczytac.pl/zaloguj/c'
    my_username = 'YOUR_MAIL@mail.com'
    my_password = 'YOUR_PASSWORD'
    session.get(url)
    login_data = dict(Email=my_username, Password=my_password)
    session.post(url, data=login_data, headers={'Referer': 'http://lubimyczytac.pl/'})
    return session

def collect_user_page(session, base_page, user):
    if not os.path.exists(data_dir + user):
        os.makedirs(data_dir + user)

    filename = data_dir + user + '/' + 'user'
    url = base_page + user
    save_url_to_file(session, url, filename)

def collect_read_books(session, base_page, user):
    dir = data_dir + user + '/' + book_list_dir
    if not os.path.exists(dir):
        os.makedirs(dir)

    user_url = base_page + user
    page = session.get(user_url)
    soup = BeautifulSoup(page.content)
    link = soup.find(href=re.compile('przeczytane'))
    # if a user haven't read any book yet
    if link is None:
        return
    link_to_read_books = link.get('href')

    max_page_num = get_max_page_number(link_to_read_books, session)
    for i in range(1, max_page_num + 1):
        url = link_to_read_books + '/' + str(i)
        filename = data_dir + user + '/' + book_list_dir + '/' + str(i)
        save_url_to_file(session, url, filename)

def get_max_page_number(link, session):
    page = session.get(link)
    soup = BeautifulSoup(page.content)
    links = soup.find_all(href=re.compile('przeczytane'), text=re.compile('^[0-9]*$'))
    # if there is only one site with read books
    if len(links) == 0:
        return 1
    max_page_number = links[-1].text
    return int(max_page_number);

def save_url_to_file(session, url, filename):
    print "Saving: " + url
    # be polite to the server
    time.sleep(random.uniform(0,2))

    page = session.get(url)
    file = open(filename, 'w')
    file.write(page.content)
    file.close()

def main():
    start_user_id = 100000
    end_user_id = 100500
    session = login()
    for i in range(start_user_id, end_user_id):
        collect_user_page(session, 'http://lubimyczytac.pl/profil/', str(i))
        collect_read_books(session, 'http://lubimyczytac.pl/profil/', str(i))

if __name__ == '__main__':
    main()

