import RPi.GPIO as GPIO
import time
from time import sleep
from threading import Thread
import queue

from hal import hal_led as led
from hal import hal_lcd as LCD
from hal import hal_adc as adc
from hal import hal_buzzer as buzzer
from hal import hal_keypad as keypad
from hal import hal_moisture_sensor as moisture_sensor
from hal import hal_input_switch as input_switch
from hal import hal_ir_sensor as ir_sensor
from hal import hal_rfid_reader as rfid_reader
from hal import hal_servo as servo
from hal import hal_temp_humidity_sensor as temp_humid_sensor
from hal import hal_usonic as usonic
from hal import hal_dc_motor as dc_motor
from hal import hal_accelerometer as accel

from pid import PID
from server import run_server, initialize_database

# PID parameters
Kp = 2
Ki = 0.2
Kd = 0.01
output_limits = (-255, 0)  # limits for the fan speed

desired_temp = 30  # update later

pid = PID(Kp, Ki, Kd, desired_temp, output_limits)

#Empty list to store sequence of keypad presses
shared_keypad_queue = queue.Queue()

#Call back function invoked when any key on keypad is pressed
def key_pressed(key):
    shared_keypad_queue.put(key)


def main():
    # initialize the database
    initialize_database() # TODO: make this only run once
    # start the dashboard
    run_server()

    #initialization of HAL modules
    led.init()
    adc.init()
    buzzer.init()

    moisture_sensor.init()
    input_switch.init()
    ir_sensor.init()
    reader = rfid_reader.init()
    servo.init()
    temp_humid_sensor.init()
    usonic.init()
    dc_motor.init()
    accelerometer = accel.init()

    # EC Sensor = Pin 18
    # pH Sensor = Pin 27

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(18, GPIO.input)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(27, GPIO.input)


    keypad.init(key_pressed)
    keypad_thread = Thread(target=keypad.get_key)
    keypad_thread.start()

    lcd = LCD.lcd()
    lcd.lcd_clear()

    lcd.lcd_display_string("Mini-Project", 1)
    lcd.lcd_display_string("Dignostic Tests", 2)

    time.sleep(3)

    print("press 0 to test accelerometer")
    print("press 1 to test LED")
    print("press 2 to test potentiometer")
    print("press 3 to test buzzer")
    print("press 4 to test moizture sensor")
    print("press 5 to test ultrasonic sensor")
    print("press 6 to test rfid reader")
    print("press 7 to test LDR")
    print("press 8 to test servo & DC motor")
    print("press 9 to test temp & humidity")
    print("press # to test slide switch")
    print("print * to test IR sensor")

    def maintain_airtemp():
        airtemp = temp_humid_sensor.read_temp_humidity()[0]

        if airtemp < 0:
            return False

        while 25 <= airtemp <= 27:
            dc_motor.set_motor_speed(15)
            return True

        while 28 <= airtemp <= 30:
            dc_motor.set_motor_speed(30)
            return True

        while 31 <= airtemp <= 35:
            dc_motor.set_motor_speed(50)
            return True

    # Thread to monitor and maintain air temperature in background
    airtemp_thread = Thread(target = maintain_airtemp)
    airtemp_thread.start()

    def monitor_humidity():
        humidity = temp_humid_sensor.read_temp_humidity()[1]
        if humidity < 0 or humidity > 100:
            return False

        while 0 <= humidity <= 100:
            print("The relative humidity is " + str(humidity) + "%")
            sleep(1.5)
            return True


    # Thread to monitor relative humidity in background
    humidity_thread = Thread(target = monitor_humidity)
    humidity_thread.start()

    def maintain_ec():
        ec_level = GPIO.input(18)
        if ec_level < 0: # Checks for negative EC Level that could be due to a malfunction
            return False
        else:
            ec_lowerlimit = 1
            servo1 = GPIO.PWM(37, 50)
            while 0 <= ec_level <= ec_lowerlimit:
                i=0
                for i in range(180):
                    servo.set_servo_position(i)
                    i+=1
                    sleep(0.01)
            return True

    # Thread to monitor and maintain electrical conductivity in background
    ec_thread = Thread(target = maintain_ec)
    ec_thread.start()

    def monitor_ph():
        ph = GPIO.input(27)
        if ph < 0 or ph > 14:
            return False

        while 0 <= ph < 7:
            print("The solution is more acidic, with a pH of " + str(ph))
            sleep(1)
            return True

        while ph == 7:
            print("The solution is neutral, with a pH of " + str(ph))
            sleep(1)
            return True

        while 7 < ph <= 14:
            print("The solution is more acidic, with a pH of " + str(ph))
            sleep(1)
            return True

    # Thread to monitor pH level in background
    ph_thread = Thread(target = monitor_ph)
    ph_thread.start()

    def maintain_light():
        if ir_sensor.get_ir_sensor_state==0:
            return False

        while ir_sensor.get_ir_sensor_state():
            led.set_output(1)
            return True

    # Thread to monitor and maintain light intensity in background
    light_thread = Thread(target = maintain_light)
    light_thread.start()

    while(True):
        lcd.lcd_clear()
        lcd.lcd_display_string("press any key!", 1)


        print("wait for key")
        keyvalue= shared_keypad_queue.get()

        print("key value ", keyvalue)


        if(keyvalue == 1):
            lcd.lcd_display_string("key pressed "  +str(keyvalue), 1)
            lcd.lcd_display_string("LED TEST ", 2)
            led.set_output(1, 1)
            time.sleep(2)
            led.set_output(1, 0)
            time.sleep(2)

        elif (keyvalue == 2):
            pot_val = adc.get_adc_value(1)
            lcd.lcd_display_string("key pressed "  +str(keyvalue), 1)
            lcd.lcd_display_string("potval " +str(pot_val), 2)
            time.sleep(2)

        elif (keyvalue == 3):
            lcd.lcd_display_string("key pressed "  +str(keyvalue), 1)
            lcd.lcd_display_string("Buzzer TEST ", 2)
            buzzer.beep(0.5, 0.5, 1)

        elif (keyvalue == 4):
            lcd.lcd_display_string("key pressed "  +str(keyvalue), 1)
            sensor_val = moisture_sensor.read_sensor()
            lcd.lcd_display_string("moisture " +str(sensor_val), 2)
            time.sleep(2)

        elif (keyvalue == 5):
            lcd.lcd_display_string("key pressed "  +str(keyvalue), 1)
            sensor_val = usonic.get_distance()
            lcd.lcd_display_string("distance " +str(sensor_val), 2)
            time.sleep(2)

        elif (keyvalue == 6):
            lcd.lcd_display_string("key pressed "  +str(keyvalue), 1)
            id = reader.read_id_no_block()
            id = str(id)

            if id != "None":
                print("RFID card ID = " + id)
                # Display RFID card ID on LCD line 2
                lcd.lcd_display_string(id, 2)
            time.sleep(2)

        elif (keyvalue == 7):
            lcd.lcd_display_string("key pressed "  +str(keyvalue), 1)
            pot_val = adc.get_adc_value(0)
            lcd.lcd_display_string("LDR " +str(pot_val), 2)
            time.sleep(2)

        elif (keyvalue == 8):
            lcd.lcd_display_string("key pressed "  +str(keyvalue), 1)
            lcd.lcd_display_string("servo/DC test ", 2)
            servo.set_servo_position(20)
            time.sleep(1)
            servo.set_servo_position(80)
            time.sleep(1)
            servo.set_servo_position(120)
            time.sleep(1)
            dc_motor.set_motor_speed(50)
            time.sleep(4)
            dc_motor.set_motor_speed(0)
            time.sleep(2)

        elif (keyvalue == 9):
            temperature, humidity = temp_humid_sensor.read_temp_humidity()
            lcd.lcd_display_string("Temperature "  +str(temperature), 1)
            lcd.lcd_display_string("Humidity "  +str(humidity), 2)
            time.sleep(2)

        elif (keyvalue == "#"):
            sw_switch = input_switch.read_slide_switch()
            lcd.lcd_display_string("key pressed "  +str(keyvalue), 1)
            lcd.lcd_display_string("switch "  +str(sw_switch), 2)
            time.sleep(2)

        elif (keyvalue == "*"):
            ir_value = ir_sensor.get_ir_sensor_state()
            lcd.lcd_display_string("key pressed "  +str(keyvalue), 1)
            lcd.lcd_display_string("ir sensor "  +str(ir_value), 2)
            time.sleep(2)

        elif (keyvalue == 0):
            x_axis, y_axis, z_axis = accelerometer.get_3_axis_adjusted()
            lcd.lcd_display_string("key pressed "  +str(keyvalue), 1)
            lcd.lcd_display_string("x " +str(x_axis), 2)
            time.sleep(2)
            lcd.lcd_clear()
            lcd.lcd_display_string("y " +str(y_axis), 1)
            lcd.lcd_display_string("z " +str(z_axis), 2)
            print(x_axis)
            print(y_axis)
            print(z_axis)
        time.sleep(2)


        time.sleep(1)

GPIO.cleanup




if __name__ == '__main__':
    main()