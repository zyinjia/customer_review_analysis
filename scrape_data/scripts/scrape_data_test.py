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

def get_brand_links():
    url = "https://www.amazon.com/unlocked-cell-phones/b/ref=sv_cps_1?ie=UTF8&node=2407749011"
    soup = get_soup(url)
    links = soup.find_all('div', attrs={"class":"acsUxWidget"})[2].find_all('a')
    return links

def get_phone_link(link):
    soup = get_soup(link)
    links = soup.find('ul', {'id':'s-results-list-atf'}).find_all('a', attrs={'class':'a-link-normal s-access-detail-page s-color-twister-title-link a-text-normal'})
    return links

def check_length(lists):
    l = len(lists[0])
    for alist in lists:
        if len(alist) != l:
            return False
    return True


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

    
    
if __name__ == "__main__":
    
    url = "https://www.amazon.com/Apple-iPhone-5C-16GB-White/product-reviews/B00O8EDU6U//ref=cm_cr_getr_d_paging_btm_2?ie=UTF8&reviewerType=avp_only_reviews&pageNumber=2"
    url1 = "https://www.amazon.com/Apple-iPhone-Dual-Core-Smartphone-Camera/product-reviews/B00NK332DG/ref=cm_cr_arp_d_paging_btm_2?ie=UTF8&reviewerType=avp_only_reviews&pageNumber=2"
#reviews, stars, votes, prices = get_reviews( url )
    soup = get_soup( url1 )
    aaa
    
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

    path = './scrape_data'
    
    brand = 'Apple'

    links = get_phone_link( brands[brand]['href'] )
    all_reviews = []
    all_stars = []
    all_votes = []
    all_prices = []
    product_names = []
    for link in links[4:5]:
        product_name = link['title']
        urlbase = link['href'].replace( '/dp/', '/product-reviews/' )
        urladd = "/ref=cm_cr_getr_d_paging_btm_%d?ie=UTF8&reviewerType=avp_only_reviews&pageNumber=%d" %(1, 1)
        page_num = get_page_number(urlbase+urladd)
        print page_num
        
        for i in range( 1, 2 ):
            "/ref=cm_cr_getr_d_paging_btm_%d?ie=UTF8&reviewerType=avp_only_reviews&pageNumber=%d" %(i, i)
            reviews, stars, votes, prices = get_reviews( urlbase+urladd )
            all_reviews.extend(reviews)
            all_stars.extend(stars)
            all_votes.extend(votes)
            all_prices.extend(prices)
            product_names.extend( [product_name]*len(reviews) )
            save_data(brand, product_names, 
                      all_reviews, all_stars, all_votes, all_prices,
                      path)
