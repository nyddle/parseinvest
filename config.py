# -*- coding: utf-8 -*-
import json

rest_api = "http://pereborstudio.com/investeka.php"
sources_file = "sources.json"
orgs = json.loads(open(sources_file, "r").read())