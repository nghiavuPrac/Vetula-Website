# Vetula Website

Django web app searching recipe base on ingredients

---

## Reference
api searching
https://github.com/SkyinScotlandCodes/searchproject-python/blob/main/add_ingredients.py 

search with url
https://github.com/SkyinScotlandCodes/searchproject-python/blob/main/searchproject.py 

```
url = f"https://api.edamam.com/search?q={inputIngredient}&cuisineType={inputCuisineType}&{includeAppId}&{includeAppKey}&from={startPagination}&to={endPagination}"
print(f"Showing recipe results from {startPagination} to {endPagination}")
r = requests.get(url)
```

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

### Screenshots
![](https://i.ibb.co/vmzxDqT/screencapture-127-0-0-1-8000-guacamole-3-2020-12-19-21-47-00.png)
![](https://i.ibb.co/yNttGBq/screencapture-127-0-0-1-8000-search-2020-12-19-21-46-38.png)
![](https://i.ibb.co/4F3Vz6s/screencapture-127-0-0-1-8000-2020-12-19-21-46-12.png)

---

[Tutorial On Youtube](https://youtu.be/nPusaqAbiGE)

