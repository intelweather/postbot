from fastapi import FastAPI
import os
import tweepy
import requests
import json
from gtts import gTTS
from fastapi.responses import FileResponse

app = FastAPI()


def get_image(today_data):
  forecast = today_data["shortForecast"]
  forecast = list(forecast.split(" then "))[0].lower()
  forecast = forecast.replace(" ", "")
  forecast = forecast.replace("patchy", "")
  forecast = forecast.replace("mostly", "")
  forecast = forecast.replace("partly", "")
  forecast = forecast.replace("chance", "")
  forecast = forecast.replace("showers", "")
  forecast = forecast.replace("slight", "")
  forecast = forecast.replace("isolated", "")
  forecast = forecast.replace("light", "")
  forecast = forecast.replace("likely", "")
  forecast = forecast.replace("andthunderstorms", "rainy");
  forecast = forecast.replace("rainy", "rain")
  forecast = forecast.replace("rain", "rainy")
  forecast = forecast.replace("fog", "cloudy")
  forecast = forecast.replace("drizzle", "rainy")

  forecast = forecast + ".png"

  return forecast


def get_compass(letter):
  letter = letter.replace("N", "North") \
                 .replace("NW", "Northwest") \
                 .replace("W", "West") \
                 .replace("SW", "Southwest") \
                 .replace("S", "South") \
                 .replace("SE", "Southeast") \
                 .replace("E", "East") \
                 .replace("NE", "Northeast")

  return letter

@app.get("/fetchvideo/")
def fetch_video():
  return FileResponse("bot.mp4")


@app.get("/video/{password}/")
def video(password: str):
  if password != os.environ['PASSWORD']:
    return {"Error": "403"}

  text = requests.get("https://api.weather.gov/gridpoints/SGX/42,51/forecast").text
  data = json.loads(text)["properties"]["periods"][0]
  message = f"Good morning Saint Anne School., you are going to be experiencing {data['shortForecast'].lower()} weather. Todays temperature will be around {data['temperature']} Fahrenheit. Expect wind from the {get_compass(data['windDirection'])} at around {data['windSpeed']}. Thank you for visiting Intelweather!"

  speach = gTTS(text=message, lang="en", slow=False)
  speach.save("weather.mp3")

  try:
    os.remove("bot.mp4")
  except FileNotFoundError:
    print("bot.mp4 not found")

  try:
    os.remove("output.mp4")
  except FileNotFoundError:
    print("output.mp4 not found")

  os.system(
      f'ffmpeg -loop 1 -framerate 1 -i {get_image(data)} -i weather.mp3 -map 0 -map 1:a -c:v libx264 -preset ultrafast -tune stillimage -vf fps=10,format=yuv420p -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -c:a copy -shortest bot.mp4'
  )

  return {"Succes": "Produced"}


@app.get("/x/{password}/")
def x(password: str):
  if password != os.environ['PASSWORD']:
    return {"Error": "403"}

  data = json.loads(requests.get("https://api.weather.gov/gridpoints/SGX/42,51/forecast").text)["properties"]["periods"][0]
  message = f"Good morning, you are going to be experiencing {data['shortForecast'].lower()} weather at Saint Anne School. Todays temperature will be around {data['temperature']} Fahrenheit. Expect wind from the {data['windDirection']} at around {data['windSpeed']}. View more at https://weather.sasmlange.repl.co/forecast.php. #weather #intelweather #dailyweather"

  x_key = os.environ['XKEY']
  x_secret = os.environ['XSECRET']
  x_access = os.environ['XACCESS']
  x_access_secret = os.environ['XACCESSSECRET']
  x_bearer = os.environ['XBEARER']

  api = tweepy.Client(x_bearer, x_key, x_secret, x_access, x_access_secret)

  api.create_tweet(text=message)

  return {"Succes": "Published"}
