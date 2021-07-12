import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import RPi.GPIO as GPIO
import smbus
from time import sleep
import Adafruit_DHT


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)



# Necessary declarations for SMBUS/DHT11
sensor = Adafruit_DHT.DHT11
gpio=4  #dht11 pin

# Necessary declarations for RAINDROP SENSOR
rain = 11
GPIO.setup(rain, GPIO.IN)


# Necessary declarations for SOIL MOISTURE SENSOR
bus= smbus.SMBus(1)
ADDRESS = 0X48

# Logic for Rain sensor
def Rain():
    state = GPIO.input(rain)
    if state==1:
        print("NO RAIN")
        publish.single("CoreElectronics/topic", " NO RAIN  ", hostname="test.mosquitto.org")
        sleep(2)
    else:
        print("RAIN RAIN RAIN")
        publish.single("CoreElectronics/topic", " RAIN RAIN RAIN  ", hostname="test.mosquitto.org")
        sleep(2)


# Logic for DHT11
def HumidTemp():
    humidity, temperature = Adafruit_DHT.read_retry(sensor,gpio)
    if humidity is not None and temperature is not None:      
        print('Temp = {0:0.1f}*c      Humidity = {1:0.1f}%'.format(temperature, humidity))
        publish.single("CoreElectronics/topic", str('Temp = {0:0.1f}*c      Humidity = {1:0.1f}%'.format(temperature, humidity)), hostname="test.mosquitto.org")
    else:
        print("Failed !")
        publish.single("CoreElectronics/topic", "FAILED", hostname="test.mosquitto.org")


# Logic for SoilMoisture sensor
def SoilMoisture():
    soilm = bus.read_byte(ADDRESS)
    soilm = float(soilm)
    print("value ",soilm)
    Val = "Soil moisture is "+str(soilm)
    publish.single("CoreElectronics/topic",str(Val),hostname="test.mosquitto.org")
    
    sleep(3)



    






def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
 
    # Subscribing in on_connect() - if we lose the connection and
    # reconnect then subscriptions will be renewed.
   # client.subscribe("CoreElectronics/topic")
    client.subscribe("CoreElectronics/topic")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

    if msg.payload == "Rain":
        print("Invoking RainDrop Sensor....")
        Rain()


    if msg.payload == "TH":
        print("Invoking DHT11 Sensor.....")
        HumidTemp()

    if msg.payload =="Soil":
        print("Invoking Soil Moisture Sensor....")
        SoilMoisture()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
 
client.connect("test.mosquitto.org", 1883, 60)
client.loop_forever()