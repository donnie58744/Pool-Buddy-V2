### Raspberry PI Only

#### Requirements
- python3
- pyqt5

#### Electronics
- Raspberry PI
- DS18B20 Waterproof Temperture sensor with a pullup resistor, Heres the one I [bought](https://www.amazon.com/BOJACK-Temperature-Waterproof-Stainless-Raspberry/dp/B09NVWNGLQ/ref=sr_1_1?sr=8-1)
- Any type of switch or button
- Any color LED

#### PI Setup
- DS18B20 Sensor
  - Connect **Power** to PI's **3v3 pin**
  - Connect **Data** to **GPIO 4**
- Connect **Button/Switch** to **GPIO 27**
- Connect **LED** to **GPIO 17**
- Make sure to ground everything to a ground pin on the PI

#### How To Run
- Create an account at [QuackyOS](https://QuackyOs.com), if you don't already have one
- Run the command ```python3 main.py```
- Login using your QuackyOS account, Pool Buddy will create a random seriel number linked to your account
- Back at [QuackyOS](https://QuackyOs.com), launch the Pool Buddy program and login, you should see that newly created seriel number on the devices page
- Done!
