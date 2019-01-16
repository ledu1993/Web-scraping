import bs4 as bs
import urllib.request
import re

# original source
sauce = 'https://www.tescomobile.com'

# pay monhtly link
pm_sauce = urllib.request.urlopen('https://www.tescomobile.com/shop/pay-monthly').read()

# turn into beautiful soup object using the lxml parser
soup = bs.BeautifulSoup(pm_sauce, 'lxml')


# number of pages
page_urls = []
pages = soup.find('ul', class_='page-numbers ng-star-inserted')
links = pages.find_all('a')
for link in links:
    url = link.get('href')
    page_urls.append(url)

# tidy up links
# get rid of dupes
page_urls = list(set(page_urls))
page_urls = sorted(page_urls)
# add page 1
page1_url = page_urls[0].replace('2', '1')
page_urls.insert(0, page1_url)


# loop through all the pages and grab relevant info
products_list = []
ppm_list = []
length_list = []
ufc_list = []

for url in page_urls:
    go_to_page = sauce + url
    sauce_url = urllib.request.urlopen(go_to_page).read()
    soup_url = bs.BeautifulSoup(sauce_url, 'lxml')

    products = soup_url.find_all('h4', class_='product-tile__title')
    for product in products:
        product_txt = product.text
        product_txt = product_txt.replace('\n', '')
        products_list.append(product_txt)
    
    product_url = soup_url.find_all('a', class_='button button__cta ng-star-inserted')
    for url in product_url:
        go_to_product = sauce + url.get('href')
        sauce_product_url = urllib.request.urlopen(go_to_product).read()
        soup_product_url = bs.BeautifulSoup(sauce_product_url, 'lxml')
        tariff_url = soup_product_url.find_all('a', {'id': 'analytics-pdp-choose-tariff'})
        for url in tariff_url:
            # if contract length is 36 months, we need to modify the URLs so that data=1024 (i.e. 1GB)
            if('contractLength=36' in str(url)):
                go_to_tariff = sauce + re.sub('data=.*?&', 'data=1024&', url.get('href'), flags=re.DOTALL)
                sauce_tariff_url = urllib.request.urlopen(go_to_tariff).read()
                soup_tariff_url = bs.BeautifulSoup(sauce_tariff_url, 'lxml')
                print(soup_tariff_url.find('strong').text)
            # if contract length is 24 months modifying the URL doesn't work, so we have to manually select data
            else:
                go_to_tariff = sauce + url.get('href')
                sauce_tariff_url = urllib.request.urlopen(go_to_tariff).read()
                soup_tariff_url = bs.BeautifulSoup(sauce_tariff_url, 'lxml')
                print(re.sub('1GB.*?£', 'ppm_starts_here', str(soup_tariff_url.find_all('label')), flags=re.DOTALL))
#                resub('1GB', '', str(soup_tariff_url.find_all('label')))


#<label _ngcontent-c84="" class="tariff-row" for="tariff-351613">
#    <div _ngcontent-c84="" class="tariff-row__feature">
#        <div _ngcontent-c84="" class="tariff-row__value">1GB</div>
#            <div _ngcontent-c84="" class="tariff-row__label">Speedy 4G data</div>
#        </div>
#        <div _ngcontent-c84="" class="tariff-row__feature">
#            <div _ngcontent-c84="" class="tariff-row__value">500</div>
#            <div _ngcontent-c84="" class="tariff-row__label">Minutes</div>
#    </div>
#        <div _ngcontent-c84="" class="tariff-row__feature">
#            <div _ngcontent-c84="" class="tariff-row__value">5000</div>
#            <div _ngcontent-c84="" class="tariff-row__label">Text messages</div>
#</div>
#    <!---->
#        <div _ngcontent-c84="" class="tariff-row__feature tariff-row__feature--price">
#            <div _ngcontent-c84="" class="tariff-row__value">£9.00</div>
#            <div _ngcontent-c84="" class="tariff-row__label tablet-desktop-only">a month</div>
#            <div _ngcontent-c84="" class="tariff-row__label phone-only">Monthly cost</div>
#    </div>
#        <div _ngcontent-c84="" class="tariff-row__feature tariff-row__feature--cta">
#            <div _ngcontent-c84="" class="button">Choose this tariff</div>
#</div>
#    </label>



#    ppms = soup_url.find_all('span', class_='product-tile__info--bold product-tile__stand-out')
#    for ppm in ppms:
#        ppm_txt = ppm.text
#        ppm_txt = float(ppm_txt.replace('£',''))
#        ppm_list.append(ppm_txt)

    lengths = soup_url.find_all('span', class_='ng-star-inserted')
    for length in lengths:
        # delete banner-heading lines and redudant lines which contains upfront cost or APR info
        if 'banner-heading' not in str(length) and 'upfront' not in str(length) and '0%' not in str(length):
            length_txt = length.text
            # contract is 24 months if specified and 36 months if labelled 'phone credit contract'
            if '24 month' in length_txt:
                length_list.append(24)
            else:
                length_list.append(36)


print(products_list)
print(ppm_list)
print(length_list)
