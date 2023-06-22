# Vetula Website

Django web app searching recipe base on ingredients
- Sound effect credit: Sound Effect by <a href="https://pixabay.com/users/soundsforyou-4861230/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=127856">SoundsForYou</a> from <a href="https://pixabay.com/sound-effects//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=127856">Pixabay</a> 

---

## Reference
- Paypal integration:
https://overiq.com/django-paypal-integration-with-django-paypal/ , https://www.youtube.com/watch?v=8rMfW4wO-vU&t=156s , 
- paypal layout:
https://github.com/paypaldev/PayPal-Advanced-Checkout-Tutorial/blob/main/index.html  

- api searching
https://github.com/SkyinScotlandCodes/searchproject-python/blob/main/add_ingredients.py 

- search with url
https://github.com/SkyinScotlandCodes/searchproject-python/blob/main/searchproject.py 

```
url = f"https://api.edamam.com/search?q={inputIngredient}&cuisineType={inputCuisineType}&{includeAppId}&{includeAppKey}&from={startPagination}&to={endPagination}"
print(f"Showing recipe results from {startPagination} to {endPagination}")
r = requests.get(url)
```

[Tutorial On Youtube](https://youtu.be/nPusaqAbiGE)

---
## Prerequisite
- dev-env: python 3.11
- edamam aplication api: https://developer.edamam.com/admin/applications
- create "./main/api_config.py" file and pass Application ID and key with the following line:
    ```
        # Replace <> with code on the above link
        recipes_appid='<Application ID>'
        recipes_appkey='<Application Keys>'    
    ```
---

## Installation:

Update pip:
```
    pip install --upgrade pip
```

Create and start virtual environments:
```
    pip install virtualenv
    python -m venv env
    
    # Windows activate
    env\Scripts\activate
    deactivate

    # Linux activate
    source env/bin/activate
    deactivate
```

Installing required packages:
```
    pip install -r requirements.txt
```

DownLoad data
```
    python main/food_extraction/Utils.py download_data
```

Download 'punkt' - a nltk library
```
    python main/food_extraction/Utils.py download_punkt

```


# Test Food extraction 
### From command line
```    
    $ # Entity extraction
    python main/food_extraction/Ner.py "Today i have some beef, chicken and eggs, what i can do with it"
    ['today', 'beef', 'chicken', 'eggs']
```


# Usage
### From command line
```    
    python manage.py runserver
```

