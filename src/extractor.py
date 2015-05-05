#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'krris'

from bs4 import BeautifulSoup
import os
from pymongo import MongoClient

connection = MongoClient('localhost', 27017)
db = connection.TASS_DB

data_dir = '../data/'
books_dir = 'books/'

def extract_username(soup):
    # check if profile was deleted
    if soup.find('head').title.text.startswith(u'Brak uprawnień'):
        return None

    # get profile header
    profile_header = soup.find(class_='profile-header')
    username = profile_header.find('h5').text
    return username

def extract_city(soup):
    profile_header = soup.find(class_='profile-header')
    profile_info = profile_header.find(class_='font-szary-a3').text
    details = profile_info.split(',')
    details = map(lambda  x: x.strip(), details)

    sex_id = 1
    status_id = 3
    # a city is always located between sex and status
    if ((details[sex_id] == u'mężczyzna' or
        details[sex_id] == u'kobieta') and
        details[status_id].startswith(u'status')):
        return details[2]

    return None

def extract_books(user_id):
    books_data = []
    books_path = data_dir + str(user_id) + '/' + books_dir
    max_page_id = len(os.listdir(books_path))

    for page_id in range(1, max_page_id + 1):

        filename = data_dir + str(user_id) + '/' + books_dir + str(page_id)
        content = read_file(filename)
        soup = BeautifulSoup(content)
        books = soup.find_all(class_='book')

        for i in range(len(books)):
            book_title = books[i].find(class_='bookTitle').text
            book_rating = len(books[i].find(class_='book-general-data').find_all(class_='rating-on'))
            book_authors_with_links = books[i].find(class_='book-general-data').find_all('a')[1:]
            book_authors = []
            for author_with_link in book_authors_with_links:
                book_authors.append(author_with_link.text)
            # print "Title: %s, rating: %s, authors: %s" % (book_title, book_rating, book_authors)
            book_data = {'title':book_title, 'rating':book_rating, 'authors':book_authors}
            books_data.append(book_data)

    return books_data


def read_file(filename):
    file = open(filename, 'r')
    content = file.read()
    file.close()
    return content


def main():
    for user_id in range(100000, 110000) + range(200000, 210000):
        # dict which will be insert into DB
        user_data = {}

        filename = data_dir + str(user_id) + '/' + 'user'
        if not os.path.exists(filename):
            continue

        user_page = read_file(filename)
        soup = BeautifulSoup(user_page)

        username = extract_username(soup)
        if username is not None:
            user_data['username'] = username
            city = extract_city(soup)
            if city is None:
                # user data doesn't contain information about city
                pass
            else:
                user_data['city'] = city
                books_data = extract_books(user_id)

                # insert data into DB
                for book in books_data:
                    db.users.insert_one(dict(user_data, **book))
        else:
            print 'Username [%s] profile deleted' % (str(user_id))


if __name__ == '__main__':
    main()


