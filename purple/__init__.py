import requests
import time

class PurpleSensor:
    def __init__(self,URL,logger):
        self.URL=URL
        self.logger=logger
        self.last_update=0
        self.last_aqi='<div style="color: rgb(255,0,0);">Unknown</div>'

    @staticmethod
    def average_colors(color1,color2):
        parsed_color1 = color1[4:-1].split(',')
        parsed_color2 = color2[4:-1].split(',')
        return 'rgb(%i,%i,%i)'%(
                PurpleSensor.avg(int(parsed_color1[0]),(int(parsed_color2[0]))),
                PurpleSensor.avg(int(parsed_color1[1]),(int(parsed_color2[1]))),
                PurpleSensor.avg(int(parsed_color1[2]),(int(parsed_color2[2])))
                )

    @staticmethod
    def avg(num1,num2):
        return (num1+num2)/2.0

    def get_data(self):
        try:
            r = requests.get(self.URL,timeout=30,stream=False)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            self.logger.exception('Error fetching purple sensor data')
            if time.time() - self.last_update>900:
                return '<div style="color: rgb(255,0,0);">Unknown</div>'
            else:
                return self.last_aqi
        if abs(data['pm2.5_aqi'] - data['pm2.5_aqi_b']) < 50:
            self.last_aqi='<div style="color: %s;">%i</div>'%(self.average_colors(data['p25aqic'],data['p25aqic_b']),PurpleSensor.avg(data['pm2.5_aqi'],data['pm2.5_aqi_b']))
        else:
            self.last_aqi='<div style="color: %s;">%i,%i</div>'%(self.average_colors(data['p25aqic'],data['p25aqic_b']),data['pm2.5_aqi'],data['pm2.5_aqi_b'])
        self.last_update=time.time()
        return self.last_aqi
