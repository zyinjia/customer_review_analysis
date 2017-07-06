import requests
from bs4 import BeautifulSoup
from retrying import retry
import pandas as pd
import os

@retry
def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup( response.text, 'lxml' )
    return soup

@retry
def get_brand_links():
    url = "https://www.amazon.com/unlocked-cell-phones/b/ref=sv_cps_1?ie=UTF8&node=2407749011"
    soup = get_soup(url)
    links = soup.find_all('div', attrs={"class":"acsUxWidget"})[2].find_all('a')
    return links

@retry
def get_phone_link(link):
    soup = get_soup(link)
    links = soup.find('ul', {'id':'s-results-list-atf'}).find_all('a', attrs={'class':'a-link-normal s-access-detail-page s-color-twister-title-link a-text-normal'})
    return links

@retry
def get_nextpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    next_url = soup.find( 'a', attrs={'title':'Next Page', 'class':'pagnNext'} )
    return next_url

def check_length(lists):
    l = len(lists[0])
    for alist in lists:
        if len(alist) != l:
            return False
    return True

@retry
def get_reviews(url):
    soup = get_soup(url)
    reviews = soup.find_all('div', attrs={'class':'a-row review-data'})
    stars = soup.find('div', {'id':'cm_cr-review_list'}).find_all('i', attrs={'data-hook':'review-star-rating'})
    
    votes_parent = soup.find_all('span', attrs={'class':'cr-vote-buttons cr-vote-component'})    
    votes = []
    for item in votes_parent:
        vote = item.find('span', attrs={'data-hook':'helpful-vote-statement'})
        try:
            if 'One' in vote.text.split():
                votes.append(1)
            else:
                votes.append( int(vote.text.split()[0]) )
        except:
            votes.append(0)
    
    try: 
        price = soup.find('span', {'class':'a-color-price arp-price'}).text
        try:
            price = float( price.strip('$').split("$")[0].split()[0] )
        except:
            price = 0.0
    except:
        price = 0.0

    if check_length([reviews, stars, votes]):
        return [tag.text for tag in reviews], \
               [int(tag.text.split('.')[0]) for tag in stars], \
               votes, \
               [price]*len(reviews)
    raise Exception('Lengths do not match in reviews, stars and votes!')

@retry
def get_page_number(url):
    soup = get_soup(url)
    page_button = soup.find_all('li', attrs={'data-reftag':'cm_cr_arp_d_paging_btm', 'class':'page-button'})
    try:
        page_num = page_button[-1].find('a')
        return int(page_num.text)
    except:
        return 1

def save_data(brand, product_name, 
              reviews, stars, votes, prices,
              path):    
    df = pd.DataFrame({'Brand': [brand]*len(prices),
                       'Product_name': product_name,
                       'Price': prices,
                       'Rating': stars,
                       'Reviews': reviews,                    
                       'Review Votes': votes})
    df.to_csv( os.path.join(path, '%s-%s.csv' %(brand,product_name)),
              encoding = 'utf-8' )

def modify_name(name):
    if '/' in name:
        return name.replace('/', '-')
    return name

def scrape(links):
    all_reviews = []
    all_stars = []
    all_votes = []
    all_prices = []
    product_names = []
    for link in links:
        product_name = link['title']
        product_name = modify_name(product_name)
        print product_name
        if not os.path.exists( os.path.join(path, '%s-%s.csv' %(brand,product_name)) ):
            urlbase = link['href'].replace( '/dp/', '/product-reviews/' )
            urladd = "/ref=cm_cr_getr_d_paging_btm_%d?ie=UTF8&reviewerType=avp_only_reviews&pageNumber=%d" %(1, 1)
            page_num = get_page_number(urlbase+urladd)     
            for i in range( 1, page_num ):
                urladd = "/ref=cm_cr_getr_d_paging_btm_%d?ie=UTF8&reviewerType=avp_only_reviews&pageNumber=%d" %(i, i)
                reviews, stars, votes, prices = get_reviews( urlbase+urladd )
                all_reviews.extend(reviews)
                all_stars.extend(stars)
                all_votes.extend(votes)
                all_prices.extend(prices)
                product_names.extend( [product_name]*len(reviews) )
            save_data(brand, product_name, 
                      all_reviews, all_stars, all_votes, all_prices,
                      path)


if __name__ == "__main__":
    
    brand_links = get_brand_links()
    brand_names = ['Apple',
                   'Asus',
                   'Samsung',
                   'LG',
                   'Alcatel',
                   'Huawei',
                   'BLU',
                   'Motorola',
                   'Sony',
                   'ZTE']
    brands = { a:b for a,b in zip(brand_names, brand_links) }
    
    path = '../'
    amazon_url = 'https://www.amazon.com'
    
    for brand in brand_names:
        page = brands[brand]['href']
        next_page = True
        cnt = 0
        while next_page:
            if cnt != 0:
                page = amazon_url + next_page['href']
            scrape( get_phone_link(page) )
            next_page = get_nextpage(page)
            cnt += 1                        