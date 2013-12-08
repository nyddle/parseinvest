#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import pickledb
import logging
import json
import time

import config
import FeedParser

def main():
    """Inspect updates in organizations' feeds, find news'
    links and titles and post them one by one to REST API"""
    change_db = pickledb.load('org_changed.db', True)

    result = []

    # Update config file
    logging.info("Checking source updates at %s",
                 config.rest_api + "?action=check_source_update")

    r = requests.get(config.rest_api + "?action=check_source_update")
    logging.debug("Server responded:\n%s", r.content)
    source_state = r.json()

    if source_state["changes"]:
        logging.info("Checking source updates at %s",
                     config.rest_api + "?action=check_source_update")

        r = requests.get(config.rest_api + "?action=get_source_update")
        logging.debug("Server responded:\n%s", r.content)
        config.orgs = r.json()
        f = open(config.sources_file, "w")
        logging.debug("Saving new list of sources to file '%s'", config.sources_file)
        f.write(json.dumps(config.orgs))

    else:
        logging.info("No changes found")

    # Parse organization's feeds
    for org in config.orgs:

        logging.info("Downloading %s as '%s' feed", org["link"], org["name"])
        r = requests.get(org["link"])

        if org["feedtype"] == "rss":
            logging.debug("Creating new %s instance", 'RssParser')
            p = FeedParser.RssParser()

        org_id = org["id"]
        date_changed = change_db.get(org_id)

        logging.debug("Timestamp of last recorded item from '%s' feed: %s",
                      org["name"], date_changed)

        max_date = date_changed

        parsed = p.parse(r.content)
        logging.info("Found %s links in feed", len(parsed))

        new_item_qty = 0
        for link in parsed:
            if not date_changed or date_changed < link["date"]:

                link["org_id"] = org["id"]

                result.append(link)
                new_item_qty += 1

                if max_date < link["date"]:
                    max_date = link["date"]

        logging.info("Found %s new links since last record", new_item_qty)
        logging.debug("Timestamp of last recorded item from '%s' feed is now %s",
                      org["name"], max_date)

        change_db.set(org_id, max_date)

    # TODO: Post to an API link defined in config.py
    for link in result:
        logging.info("Sending link '%s' to %s", link["url"],
                     config.rest_api + "?action=push_links")

        r = requests.post(config.rest_api + "?action=push_links", data=link)
        logging.debug("Server responded:\n%s", r.content)
        time.sleep(0.2)

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
                    level=logging.DEBUG)

if __name__ == '__main__':
    main()