import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import json
import copy
import random, time


## FUNTCTION TO DOWNLOAD THE IMAGE TO THE FOLDER
def downloadimage(url):
    save_directory = "./images"
    response = requests.get(url)
    time.sleep(random.randint(1,2))

    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image_filename = url.split('/')[-1]
        save_path = f"{save_directory}/{image_filename}"
        image.save(save_path)
        return save_path
    else:
        return ''
    
## FUNCTION TO GET EACH PRODUCT DATA
def getproductdata(product):
    return {
        "ItemTitle": product.select_one('h5.product-name').text.strip(),
        "ItemImageURL": "https:" + product.find('img').get('src'),
        "ImagePath":downloadimage("https:" + product.find('img').get('src')),
        "ItemPrice": product.select_one('span.price.product-price').text.strip(),
    }


## CODE STARTS FROM HERE...
root_domain = 'https://almeera.online/'
response = requests.get(root_domain)
if(response.status_code == 200):
    soup = BeautifulSoup(response.text, 'html.parser')

    ## Getting categories and iterating over each category
    categories = soup.select('ul.subcategory-view-icons li')
    data = []

    for catindex,category in enumerate(categories):
        print(f"\nCat: doing {catindex+1}.{category.text.strip()} out of {len(categories)}")
        category_data = {
            "CategoryTitle": category.select_one('span.subcategory-name').text.strip(),
            "CategoryImageURL": 'https:' + category.find('img')['src'],
            "ImagePath" : downloadimage('https:' + category.find('img')['src']),
            "Subcategories": []
        }

        ## Opening each category link and extracting subcategories.
        response = requests.get(root_domain + category.find('a').get('href'))
        time.sleep(random.randint(1,2))
        soup = BeautifulSoup(response.text, 'html.parser')
        subcategories = soup.select('ul.subcategory-view-icons li')
        
        ## iterating over each subcategory
        for subindex,subcategory in enumerate(subcategories):
            print(f"Subcat: doing {subindex+1}.{subcategory.text.strip()} out of {len(subcategories)}")
            subcategory_data = {
                "SubcategoryTitle": subcategory.text.strip(),
                "Products": []
            }

            ## Getting 5 products from the first two pages of each subcategory
            for i in range(1, 3):
                response = requests.get(f"{root_domain}{subcategory.find('a').get('href')}?pageId={i}")
                time.sleep(random.randint(1,2))
                soup = BeautifulSoup(response.text, 'html.parser')
                try:
                    list_header = soup.find('div', class_='list-header')
                    products_div = list_header.find_next_sibling('div', class_='products')
                    products = products_div.select('li.product-cell.box-product')

                    for product in products[:5]:
                        subcategory_data["Products"].append(getproductdata(product))
                except:
                    print('no products found')
                try:
                    products_displaying = int(soup.select_one('span.end-record-number').text.strip())
                except:
                    products_displaying = 0
                if products_displaying != 39:
                    break

            category_data["Subcategories"].append(subcategory_data)

        data.append(category_data)


    #Saving data to the json file
    with open('output.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
else:
    print("Failed to connect to the website")
