# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod, abstractproperty
from datetime import datetime
import calendar
import collections
import xml.etree.ElementTree as etree

class AbstractParser(object):
    __metaclass__=ABCMeta

    @abstractmethod
    def parse(self, content):
        """Parse organization's news feed"""


class RssParser(AbstractParser):

    def parse(self, content):
        """Parse RSS feed"""
        parser = etree.XMLParser()
        parser.parser.UseForeignDTD(True)
        parser.entity = collections.defaultdict(str)

        root = etree.fromstring(content, parser=parser)

        parsed = []
        for item in root.findall('./channel/item'):
            link = {}
            link["url"] = item.find('link').text
            link["date"] = calendar.timegm(
                datetime.strptime(
                    item.find('pubDate').text[0: -6],
                    "%a, %d %b %Y %H:%M:%S").utctimetuple())

            link["title"] = item.find('title').text
            parsed.append(link)

        return parsed