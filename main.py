import json

import nest_asyncio
import numpy as np
import requests
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pyngrok import ngrok

app = FastAPI()


templates = Jinja2Templates(directory="templates")

# @app.get("/location", response_class=HTMLResponse)
# async def location(request: Request):
#      return templates.TemplateResponse("location.html",{"request":request})
@app.get("/location",response_class=HTMLResponse)
async def location(request: Request):
     longitude = 120.21807459570014
     latitude = 22.995364310628513
     url = 'https://disco.deliveryhero.io/search/api/v1/feed'
     headers = {
    'content-type': "application/json",
     }
     payload = {
     'location': {
          'point': {
               'longitude':longitude ,  # 經度
               'latitude':latitude   # 緯度
          }
     },
     'config': 'Variant17',
     'vertical_types': ['restaurants'],
     'include_component_types': ['vendors'],
     'include_fields': ['feed'],
     'language_id': '6',
     'opening_type': 'delivery',
     'platform': 'web',
     'language_code': 'zh',
     'customer_type': 'regular',
     'limit': 100,  # 一次最多顯示幾筆(預設 48 筆)
     'offset': 0,  # 偏移值，想要獲取更多資料時使用
     'dynamic_pricing': 0,
     'brand': 'foodpanda',
     'country_code': 'tw',
     'use_free_delivery_label': False
     }

     rest, name, longitude, latitude, budget, cusine, promo, rating, code, link= list(),list(),list(),list(),list(),list(),list(),list(),list(),list()
     r = requests.post(url=url, data=json.dumps(payload), headers=headers)
     if r.status_code == requests.codes.ok:
          data = r.json()
     # print(data)
          restaurants = data['feed']['items'][0]['items']
     # print(len(restaurants))
          for restaurant in restaurants:
               name.append(restaurant['name'])
               longitude.append(restaurant['longitude'])
               latitude.append(restaurant['latitude'])
               budget.append(restaurant['budget'])
               cusine.append(restaurant['cuisines'][0]['name'])
               promo.append(restaurant['tag'])
               rating.append(restaurant['rating'])
               # print(restaurant)
               code.append(restaurant['code'])
               link.append(restaurant['hero_listing_image'])
     else:
          print('請求失敗')
     rest = np.stack(np.array([name,longitude,latitude,budget,cusine,promo,rating,code,link]),axis=-1)
     np.savetxt("rest.txt",rest,delimiter=",",fmt="%s")

     return templates.TemplateResponse("first1.html", {"request": request})
@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
     rest = np.loadtxt("rest.txt",delimiter=",",dtype=str)
     size = "400"
     names = rest[:5,0] # name of restaurant
     links = rest[:5,-1] # link of image
     promo = rest[:5,-4]
     rating = rest[:5,-3]
     print(type(names))
     print(links)
     # return templates.TemplateResponse("restaurant.html", {"request": request ,"names":names,"links":links,"size": size,"promo":promo,"rating":rating})
     return templates.TemplateResponse("Geo.html",{"request":request})

@app.post("/food", response_class=HTMLResponse)
async def food(request: Request):
     form_data  = await request.form()
     print(form_data)
     return templates.TemplateResponse("first1.html",{"request": request})
@app.post("/foodtype", response_class=HTMLResponse)
async def read_item(request: Request):
     # filter between main and desert
     form_data = await request.form()
     rest = np.loadtxt("rest.txt",delimiter=",",dtype=str)
     filter_desert = ['小吃','甜點','飲料','咖啡輕食']
     remove = list()
     if "left_button" in form_data:
          for i in range(len(rest)):
               for j in filter_desert:
                    if rest[i][4] == j: # if it is desert delete
                        remove.append(i)
                        break
     else:
         for i in range(len(rest)):
               check = 0 
               for j in filter_desert:
                    if rest[i][4] == j:
                         check=1
               if check == 0: # if its no desert delete
                    remove.append(i)
     rest = np.delete(rest,remove,0)
     np.savetxt("rest.txt",rest,delimiter=",",fmt="%s")
     return templates.TemplateResponse("budget.html",{"request": request})  
ngrok_tunnel = ngrok.connect(8000)
print('Public Url:',ngrok_tunnel.public_url)
nest_asyncio.apply()
uvicorn.run(app,port=8000)
