import time
import requests
import bisect

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
    def color_temperature(temp):
        colors={
                10:(0,0,255),
                21:(0,255,0),
                26:(255,255,0),
                32:(255,0,0)
                }
        color_indices=sorted(colors)
        if temp in colors:
            return colors[temp]
        index=bisect.bisect(color_indices,temp)
        if index == 0:
            return colors[color_indices[0]]
        if index == len(color_indices):
            return colors[color_indices[-1]]
        color1=colors[color_indices[index-1]]
        color2=colors[color_indices[index]]
        delta_color=color_indices[index]-color_indices[index-1]
        delta_temp=temp-color_indices[index-1]
        ratio=delta_temp/delta_color
        return 'rgb('+','.join([str(int((color2[x]-color1[x])*ratio+color1[x])) for x in range(3)])+')'


    @staticmethod
    def format_weather(weather_data,style):
        temperature_color=PirateWeather.color_temperature(weather_data['temperature'])
        return (f'<div class="{style}"><div class="weather-time">{time.strftime("%H:%M",time.localtime(weather_data["time"]))}</div>'
            f'<div style="color: {temperature_color};" class="wi wi-thermometer">{weather_data["temperature"]:.1f}</div>'
            f'<div class="wi wi-humidity">{weather_data["humidity"]:.0%}</div>'
            f'<div class="weather-icon wi {PirateWeather.icon_mapping[weather_data["icon"]]}"></div>'
            f'<div class="weather-chance">{weather_data["precipProbability"]:.0%}</div></div>')

    @staticmethod
    def forecast_block(weather_data):
        hours=sorted(weather_data['hourly']['data'],key=lambda x:x['time'])[1:6]
        formatted_hours=[]
        for hour in hours:
            formatted_hours.append(PirateWeather.format_weather(hour,style="weather-hourly"))
        return '<div class="weather-forecast">'+('<div class="weather-divider"></div>'.join(formatted_hours))+'</div>'

    def return_error(self):
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
