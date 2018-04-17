import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

review_url = 'https://www.amazon.com/RockBirds-Flashlights-Bright-Aluminum-Flashlight/product-reviews/B00X61AJYM/ref=cm_cr_getr_d_paging_btm_{}?pageNumber={}&reviewerType=avp_only_reviews'


PRETEND_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0'
whole = []
for i in range(1,129):
    url = review_url.format(i,i)
    content = requests.get(url, headers={'User-Agent': PRETEND_AGENT}).content
    soup = BeautifulSoup(content,"html5lib")
    reviews = soup.find_all('div',{'class':'a-section review'})
    print('Processing Page ',i)
    for review in reviews:
        row=[]
        #star
        row.append(review.find('a',{'class':'a-link-normal'}).text)
        #author
        row.append(review.find('a',{'class':'a-size-base a-link-normal author'}).text)
        #image
        image = 0
        if review.find('div', {'class': 'review-image-tile-section '}):
            image =1
        row.append(image)

        #subject
        row.append(review.find('a',{'class':'a-size-base a-link-normal review-title a-color-base a-text-bold'}).text)
        #review date
        row.append(review.find('span',{'class':'a-size-base a-color-secondary review-date'}).text)
        #review status(verified)
        row.append(review.find('span',{'class':'a-size-mini a-color-state a-text-bold'}).text)
        #review
        row.append(review.find('span',{'class':'a-size-base review-text'}).text.replace("\xa0",""))
        whole.append(row)
    time.sleep(0.2)
    print('Page {} complete.'.format(i))

column=['Star','author','Image','Subject','Date','Status','Review']
df = pd.DataFrame(whole,columns=column)
df.to_json('reviews.json')
print('Complete.....')