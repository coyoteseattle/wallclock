import time
import requests

class PirateWeather:

    icon_mapping={
            'clear-day': 'wi-day-sunny',
            'clear-night': 'wi-night-clear',
            'rain': 'wi-rain',
            'snow': 'wi-snow',
            'sleet': 'wi-sleet',
            'wind': 'wi-windy',
            'fog': 'wi-fog',
            'cloudy': 'wi-cloudy',
            'partly-cloudy-day': 'wi-day-cloudy',
            'partly-cloudy-night': 'wi-night-alt-cloudy'
            }

    def __init__(self,URL,logger):
        self.URL=URL
        self.logger=logger
        self.last_update=0
        self.last_data='<div class="weather error">No weather data</div>'
        self.alerts=[]

    @staticmethod
    def format_alerts(alerts):
        now = time.time()
        output = '<div class="weather-alerts">'
        for alert in alerts:
            try:
                if alert['time']<=now<alert['expires']:
                    output +=('<div class="weather-alert-%s">%s</div><br>'%(alert['severity'].lower(),alert['title']))
            except Exception as e:
                self.logger.exception(f'Error parsing alert: {alert}')
        output+='</div>'
        return output

    @staticmethod
    def format_weather(weather_data,style):
        return (f'<div class="{style}"><figure><figcaption class="weather-time">{time.strftime("%H:%M",time.localtime(weather_data["time"]))}</figcaption>'
            f'<figcaption class="wi wi-thermometer">{weather_data["temperature"]:.1f}</figcaption>'
            f'<figcaption class="wi wi-humidity">{weather_data["humidity"]:.0%}</figcaption>'
            f'<i class="wi {PirateWeather.icon_mapping[weather_data["icon"]]}"></i>'
            f'<figcaption class="weather-chance">{weather_data["precipProbability"]*100}</figcaption></figure></div>')

    @staticmethod
    def forecast_block(weather_data):
        hours=sorted(weather_data['hourly']['data'],key=lambda x:x['time'])[1:6]
        formatted_hours=[]
        for hour in hours:
            formatted_hours.append(PirateWeather.format_weather(hour,style="weather-hourly"))
        return '<div class="weather-forecast">'+('<div class="weather-divider"></div>'.join(formatted_hours))+'</div>'

    @staticmethod
    def return_error():
        if time.time() - self.last_update > 1800:
            self.last_data='%s<div class="weather error">Weather fetch failure.</div>'%self.format_alerts(self.alerts)
        return self.last_data

    def get_data(self):
        try:
            r = requests.get(self.URL,timeout=30,stream=False)
            r.raise_for_status()
            weather_data = r.json()
        except Exception as e:
            self.logger.exception('Error during weather fetch')
            return self.return_error()
        self.alerts=weather_data['alerts']
        alerts=self.format_alerts(self.alerts)
        try:
            current=self.format_weather(weather_data['currently'],'weather-current')
        except Exception as e:
            self.logger.exception('Error drawing curent weather')
            return self.return_error()
        try:
            forecast=self.forecast_block(weather_data)
        except Exception as e:
            self.logger.exception('Error drawing forecast')
            forecast='<div class="error">Error parsing forecast data</div>'
        self.last_update=time.time()
        self.last_data=f'<div class="weather">{alerts}{current}{forecast}</div>'
        return self.last_data
