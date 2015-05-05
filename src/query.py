#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import time
import sys
from bson.code import Code
import pymongo
from pygeocoder import Geocoder, GeocoderError
from collections import defaultdict
from geojson import dumps, Feature, Point, FeatureCollection

__author__ = 'krris'

# min book rating
min_rating = 6


def query_db(book_title='', book_author=''):
    connection = pymongo.MongoClient('localhost', 27017)
    db = connection.TASS_DB
    map = Code('function() { emit(this.city, 1);}')
    reduce = Code('function(key, values) {return Array.sum(values)}')

    if book_title:
        # count cities with users who read a book with a title given by user
        db.users.map_reduce(map, reduce, 'cities_by_title', query={'title': book_title})
        results = db.cities_by_title.find().sort("value", pymongo.DESCENDING)
    elif book_author:
        # count cities with users who read a book with an author given by user
        db.users.map_reduce(map, reduce, 'cities_by_author', query={'authors': book_author})
        results = db.cities_by_author.find().sort("value", pymongo.DESCENDING)

    return results


def count_cities(results):
    cities_counter = defaultdict(int)

    for r in results:
        city = r['_id']
        users_counter = r['value']
        time.sleep(random.uniform(0.1, 0.2))
        try:
            geo_results = Geocoder.geocode(city + ', Poland')
        except GeocoderError:
            print "Wrong city name: " + city
            continue
        coordinates = geo_results.coordinates
        cities_counter[coordinates] += users_counter
        print city
        print coordinates
    return cities_counter


def save_to_json(cities_counter):
    features = []
    for coordinates, counter in cities_counter.iteritems():
        fixed_coords = (coordinates[1], coordinates[0])
        my_feature = Feature(geometry=Point(fixed_coords), properties={'counter': counter})
        features.append(my_feature)

    featureCollection = FeatureCollection(features)
    json = dumps(featureCollection)

    file = open('../maps/readers_in_cities.json', 'w')
    file.write(json)
    file.close()


if __name__ == '__main__':
    print sys.argv
    book_author = ''
    book_title = ''
    if '-author' == sys.argv[1]:
        book_author = ' '.join(sys.argv[2:])
    elif '-title' == sys.argv[1]:
        book_title = ' '.join(sys.argv[2:])
    else:
        print 'Usage: [-author | -book] arg'
        exit()

    results = query_db(book_title=book_title, book_author=book_author)
    cities_counter = count_cities(results)
    save_to_json(cities_counter)



