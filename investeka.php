<?php
if (isset($_GET['action'])) {
    switch ($_GET['action']) {
        case 'push_links':
            if (isset($_POST)) {
                var_dump($_POST);
            }
        break;
        case 'check_sources_update':
            $changes = mt_rand(0, 100) > 80;

            if (!$changes) {
                $json = '{ "changes": false }';
            } else {
                $json = '{ "changes": true, "sources": [
                    { "id": "e3a5a30fd77be6ef1dcf6494403d11e9", "name": "Альфа капитал", "link": "http://www.alfacapital.ru/rss/news/", "feedtype": "rss" },
                    { "id": "b955b65af9c836302de64f6a81a0ff09", "name": "ItInvest", "link": "http://www.itinvest.ru/rss/news/", "feedtype": "rss" }
                ] }';
            }
            echo $json;
        break;
    }
}