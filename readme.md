Sumbrine Project software.

# Folder tree
```
demo.py
    |-- uwbot.py
        |-- sensor.py
        |      |-- MPU6050.py
        |      |-- bottom_distance_sensor.py
               |-- DHT11.py
               |-- water_depth_sensor.py
    |-- output.propeller.py
        |-- Lights.py
        |-- PCA9685.py
        |-- propeller.py
    |-- peripheral.py
        |-- sensor.water_depth_sensor.py
        |-- propeller.py
        |-- Lights.py
    |-- test_GPIO.py
        
       
```


# Instruction in Terminal
```
sudo chmod 777 /dev/ttyTHS1
cd ~/Sumbrine
python3 demo.py
```

# Userful commands
* Detect I2C devices
` sudo i2cdetect -r -y 0 `
* Check embedded system performance
` jtop`

# Demo instruction

```
sudo chmod 777 /dev/ttyTHS1
cd ~/Sumbrine
sudo python3 demo.py

```

