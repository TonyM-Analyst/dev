import requests

class WeatherReporter:

    def __init__(self, http_client=None): 
        self.http_client = http_client or self.default_http_client()


    def report(self, city):
        temperature = self.get_temperature(city)
        self.output(f"The temperature in {city} is {temperature}°C.")

    def get_temperature(self, city):
        response = self.http_client.get(f"http://weather.example.com/{city}")
        data = response.json()
        return data["temperature"]
    
    def output(self, message):
        print(message)

    def default_http_client(self):
        import requests
        return requests
