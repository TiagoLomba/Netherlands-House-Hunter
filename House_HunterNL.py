import requests, re
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import create_engine

# Create lists to store the data
websites = []
prices = []
sizes = []
interiors = []
links = []


#Can be changed but needs to be always in this format
location = "den haag"
location = location.lower().replace(" ", "-")
budget = input("What is the max. value you want to pay: ")
distance = (input("Maximum distance from center: ")) + 'km'

###########################KAMERNET#######################
k_url = 'https://kamernet.nl/en/for-rent/rooms-' + location  
page = requests.get(k_url)

soup = BeautifulSoup(page.content, "html.parser")


# print('\033[1m' + "Kamernet:")
for i in soup.find_all(class_ = 'col s12 no-padding'):

  house_website = "Kamernet"
  house_price_text = i.find(class_= 'tile-rent').text.strip()
  # Use regular expressions to extract the price and remove extra text
  house_price = re.sub(r'[^\d]', '', house_price_text) + '€' 
  house_condition = i.find(class_ = 'tile-furnished').text
  house_type = i.find(class_ = 'tile-room-type').text

  #Just searching for Furnished Houses
  if 'Room' not in house_type and "Uncarpeted" not in house_condition: 
    
    house_size = i.find(class_= 'tile-surface').text
    link = i.find('a').get('href')

    websites.append(house_website)
    prices.append(house_price)
    sizes.append(house_size)
    interiors.append(house_condition)
    links.append(link)

    # #PRINTS
    # print(f"Price: {house_price}")
    # print(f"Size: {house_size}")
    # print(f"Interior: {house_condition}")
    # print('\033[0m' + f"Link: {link} \n")
 

###########################Huurwoningen#######################
hw_url = 'https://www.huurwoningen.nl/in/' + location + '/?price=700-' + budget

hwpage = requests.get(hw_url)
print("URL: ", hwpage)

soup = BeautifulSoup(hwpage.content, "html.parser")

for i in soup.find_all(class_='search-list__item--listing'):
    hw_listing_features = i.find('div', class_='listing-search-item__features')

    # Check if "Kaal" is in the interior features
    if "Kaal" in hw_listing_features.text:
        continue  # Skip this listing if "Kaal" is found in interior features

    # If not "Kaal," proceed with extracting and printing the details
    house_website = "Huurwoningen"
    hw_house_adress = i.find('div', class_="listing-search-item__sub-title'").text.strip()
    hw_house_price_text = i.find(class_='listing-search-item__price').text.strip()
    hw_house_price = re.sub(r'[^\d]', '', hw_house_price_text) + '€'
    hw_house_size = hw_listing_features.find('li', class_='illustrated-features__item--surface-area').text
    
    # Find the interior element and set it to "no info" if not found
    interior_element = hw_listing_features.find('li', class_='illustrated-features__item--interior')
    if interior_element:
        hw_interior = interior_element.text
        if "Gestoffeerd" in hw_interior:
           hw_interior = "Unfurnished"
        elif "Gemeubileerd" in hw_interior:
           hw_interior = "Furnished"
    else:
        hw_interior = "No Info"
    
    hw_link = 'https://www.huurwoningen.nl' + i.find('a').get('href')

    websites.append(house_website)
    prices.append(hw_house_price)
    sizes.append(hw_house_size)
    interiors.append(hw_interior)
    links.append(hw_link)
    
    # #PRINTS
    # print(f"Adress: {hw_house_adress}")
    # print(f"Price: {hw_house_price}")
    # print(f"Size: {hw_house_size}")
    # print(f"Interior: {hw_interior}")
    # print('\033[0m' + f"Link: {hw_link} \n")

data = {
       'Website': websites,
       'Price': prices,
       'Size': sizes,
       'Condition': interiors,
       'Link': links
       }

df = pd.DataFrame(data)

sorted_df = df.sort_values(by=['Price', 'Condition'], ascending=[True, True])
sorted_df=sorted_df.reset_index(drop=True)
print(sorted_df)

##Connect and save to database
sqlite_db = 'NLHouseDatabase.db'
engine = create_engine(f'sqlite:///{sqlite_db}')
sorted_df.to_sql('Houses in the Netherlands', con=engine, if_exists='replace',index=False)
