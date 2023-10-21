import requests
import time
from bs4 import BeautifulSoup
import pandas as pd

def process_raw_articles(base_soup, source):
  articles = []

  if source == "pv":
    raw_articles = base_soup.find_all('div', class_ = "post-entry-content")
    for article in raw_articles:
      title = article.find('a').text
      date = article.find('time')['datetime']
      url = article.find('a')['href']
      articles.append({
        'title': title,
        'date': date,
        'url': url,
      })

  elif source == "psb":
    raw_articles = base_soup.find_all('div', class_="wf-cell")
    for article in raw_articles:
      title = article.get('data-name')
      date = article.get('data-date')
      url = article.find('a')['href']
      articles.append({
        'title': title,
        'date': date,
        'url': url,
      })
  
  elif source == "mdb":
    raw_articles = base_soup.find_all('div', class_="card")
    for article in raw_articles:
      title = article.find('h3', class_="card__title").text
      date = article.find('div', class_="card__info").text.split("|")[1].strip()
      url = article.find('a')['href']
      articles.append({
        'title': title,
        'date': date,
        'url': url,
      })

  else:
    return False

  return articles

def get_articles_from_journal(source, page=1):
  if source == "pv":
    url = f'https://pv.org.br/noticias/page/{page}'
  elif source == "psb":
    url = f'https://psb40.org.br/noticias/page/{page}'
  elif source == "mdb":
    url = f'https://www.mdb.org.br/noticias/page/{page}/'
  else:
    return False

  response = requests.get(url, verify=False);
  soup = BeautifulSoup(response.content, 'html.parser')

  articles = process_raw_articles(soup, source)

  create_csv(articles, source)

def create_csv(articles, source):
  non_duplicates = pd.DataFrame()
  new_data = pd.DataFrame(articles)
  existing_data = pd.read_csv(f"{source}_output.csv")

  if not new_data.empty:
    non_duplicates = pd.concat([non_duplicates, new_data[~new_data['title'].isin(existing_data['title'])]], ignore_index=True)

  combined_data = pd.concat([existing_data, non_duplicates], ignore_index=True)

  if 'Unnamed: 0' in combined_data.columns:
    combined_data = combined_data.drop(columns=['Unnamed: 0'])

  combined_data.to_csv(f"{source}_output.csv", index=False)

def iterate_get_articles_from_journal(source, start_page, end_page):
  for current_page in range(start_page, end_page + 1):
    get_articles_from_journal(source, current_page)
    time.sleep(2)

def main():
  #generates csv from the first page
  #get_articles_from_journal("pv")

  #generates csv from the third page
  #get_articles_from_journal("psb", 3)

  #generates csv from the second page to the tenth page
  iterate_get_articles_from_journal("mdb", 2, 10)

if __name__ == "__main__":
  main()