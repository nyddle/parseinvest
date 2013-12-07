#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import pickledb
import hashlib
import logging
import time

import config
import FeedParser

def main():
    """Inspect updates in organizations' feeds, find news'
    links and titles and post them one by one to REST API"""
    change_db = pickledb.load('org_changed.db', True)

    result = []

    for org in config.orgs:

        logging.info("Downloading %s as '%s' feed", org["link"], org["name"])
        r = requests.get(org["link"])

        if org["feedtype"] == "rss":
            logging.debug("Creating new %s instance", 'RssParser')
            p = FeedParser.RssParser()

        org_id = hashlib.md5(org["link"]).hexdigest()
        logging.debug("MD5 for '%s' is %s", org["link"], org_id)
        date_changed = change_db.get(org_id)

        logging.debug("Date of last recorded item from '%s' feed: %s",
                      org["name"], date_changed)

        max_date = date_changed

        parsed = p.parse(r.content)
        logging.info("Found %s links in feed", len(parsed))

        new_item_qty = 0
        for link in parsed:
            if not date_changed or date_changed < link["date"]:
                link["org"] = org
                result.append(link)
                new_item_qty += 1

                if max_date < link["date"]:
                    max_date = link["date"]

        logging.info("Found %s new links since last record", new_item_qty)
        logging.debug("Date of last recorded item from '%s' feed is now %s",
                      org["name"], max_date)

        change_db.set(org_id, max_date)

    # TODO: Post to an API link defined in config.py
    for link in result:
        logging.info("Sending link '%s' to %s", link["url"], config.rest_api)
        r = requests.post(config.rest_api, data=link)
        logging.debug("Server responded:\n%s", r.content)
        time.sleep(0.2)

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
                    level=logging.DEBUG)

if __name__ == '__main__':
    main()