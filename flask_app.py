import os
import requests
from flask import Flask
from flask_restx import Api, Resource
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
api = Api(app, doc='/docs', version='1.0', title='Agent With LangChain for Weather')

ns = api.namespace("weather", description="Weather related operations")

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"


@ns.route("/<string:city>")
class Weather(Resource):
    def get(self, city):
        """
        Retorna o clima ATUAL para uma cidade
        """
        if not API_KEY:
            return {"error": "Chave da API do OpenWeather não configurada no .env"}, 500

        # Monta a URL para o clima atual
        url = f"{BASE_URL}/weather?q={city}&appid={API_KEY}&units=metric&lang=pt_br"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return {"error": data.get("message", "Erro ao buscar cidade")}, response.status_code

        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"]
        }


@ns.route("/forecast/<string:city>")
class Forecast(Resource):
    def get(self, city):
        """
        Retorna a PREVISÃO DO TEMPO para amanhã em uma cidade
        """
        if not API_KEY:
            return {"error": "Chave da API do OpenWeather não configurada no .env"}, 500

        # Monta a URL para a previsão (forecast)
        url = f"{BASE_URL}/forecast?q={city}&appid={API_KEY}&units=metric&lang=pt_br"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return {"error": data.get("message", "Erro ao buscar cidade")}, response.status_code

        forecast_list = data.get("list", [])

        if not forecast_list:
            return {"error": "Previsão indisponível"}, 404

        target_forecast = forecast_list[8] if len(forecast_list) > 8 else forecast_list[0]

        return {
            "city": data["city"]["name"],
            "forecast": target_forecast["weather"][0]["description"],
            "temperature": target_forecast["main"]["temp"],
            "date_time": target_forecast["dt_txt"]
        }


if __name__ == '__main__':
    app.run(port=8000, debug=True)