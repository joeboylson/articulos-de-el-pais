import requests
import json
import uuid
from bs4 import BeautifulSoup


def extractArticle(url):

  _title, _paragraphs = extractArticleInformation(url)

  _data = {
    "url": url,
    "title": _title,
    "paragraphs": _paragraphs
  }

  return _data


def saveJson(filename, data):
  with open(filename, 'w') as outfile:
    json.dump(data, outfile)



def slugify(text):
  non_url_safe = ['"', '#', '$', '%', '&', '+',
                  ',', '/', ':', ';', '=', '?',
                  '@', '[', '\\', ']', '^', '`',
                  '{', '|', '}', '~', "'"]

  non_safe = [c for c in text if c in non_url_safe]
  if non_safe:
      for c in non_safe:
          text = text.replace(c, '')
          text = text.lower()
  # Strip leading, trailing and multiple whitespace, convert remaining whitespace to _
  text = u'_'.join(text.split())
  return text


def extractArticleInformation(url):
  html_content = requests.get(url).text
  soup = BeautifulSoup(html_content, "lxml")

  _title = soup.title.text

  article = soup.find("div", attrs={"class": "article_body"})
  article_items = article.findChildren()

  _paragraphs = []

  for item in article_items:
    if (item.name == 'p'):
      _paragraphs.append(item.text)

  return [_title, _paragraphs]


def getArticleLinks():

  BASE_URL = "https://elpais.com/"

  html_content = requests.get(BASE_URL).text
  soup = BeautifulSoup(html_content, "lxml")

  links = soup.findAll("a", href=True)

  _article_links = []

  for link in links:
    link_href = link['href']

    if link_href.endswith(".html") and link_href.startswith("/"):

      try:
        _article = extractArticle("{}{}".format(BASE_URL, link_href))
      except:
        _article = None

      link_info = link_href.split('/')

      if len(link_info) == 4:
        _, category, date, filename = link_info 
      elif link_info == 5:
        _, _category, _subcategory, date, filename = link_info
        category = ' | '.join([_category, _subcategory])
      else:
        continue

      _article_links.append({
        "id": str(uuid.uuid4()),
        "title": link.text,
        "href": link_href,
        "category": category,
        "date": date,
        "filename": filename,
        "article": _article
      })

  return _article_links

# -----

article_links = getArticleLinks()
saveJson('data.json', article_links)
