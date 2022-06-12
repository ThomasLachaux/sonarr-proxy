from mitmproxy import http, exceptions
import json
import requests
from bs4 import BeautifulSoup
from os import environ


for key in ("SONARR_HOST", "SONARR_API_KEY"):
    if key not in environ:
        raise exceptions.OptionsError(f'ERROR : {key} does not exists')


def inject_fr_titles(mapping):
    # Load cache
    f = open('cache.json', 'r')
    cache = json.load(f)
    f.close()

    # Retreives series watched
    print('Get personal series')
    request = requests.get(f"{environ['SONARR_HOST']}/api/v3/series?apikey={environ['SONARR_API_KEY']}")
    request.raise_for_status()
    series = request.json()

    for serie in series:
        tvdbId = str(serie['tvdbId'])

        # Check if the title exists in the cache
        if tvdbId in cache:
            fr_title = cache[tvdbId]
            print(f"[{serie['titleSlug']}] {fr_title} is in cache. Skipping fetcing")
            
        else:
            print(f"[{serie['titleSlug']}] Get TVDB page")
            request = requests.get(f"http://www.thetvdb.com/?tab=series&id={tvdbId}")
            html = request.text

            soup = BeautifulSoup(html, 'html.parser')
            fr_title = soup.find('div', attrs={"class": "change_translation_text", "data-language": "fra"}).attrs['data-title']
            print(f"[{serie['titleSlug']}] Found french title {fr_title}")

        # Retreive existing names
        titles = [x['title'] for x in mapping if x['title'] == fr_title and x['tvdbId'] == tvdbId]

        # Check if we need to append the french name
        if len(titles) == 0:
            print(f"[{serie['titleSlug']}] Append french title {fr_title}")
            new_mapping = {'title': fr_title, 'searchTitle': fr_title, 'season': -1, 'tvdbId': tvdbId}
            mapping.append(new_mapping)
            cache[tvdbId] = fr_title

    f = open('cache.json', 'w')
    json.dump(cache, f, indent=4)
    f.close()

    return mapping

class InjectFrShows:

    def response(self, flow: http.HTTPFlow) -> None:
        print(flow.request.pretty_url)
        if flow.request.pretty_url == "https://services.sonarr.tv/v1/scenemapping":
            mapping = json.loads(flow.response.content)
            new_mapping = inject_fr_titles(mapping)
            flow.response.content = json.dumps(new_mapping).encode()


addons = [InjectFrShows()]