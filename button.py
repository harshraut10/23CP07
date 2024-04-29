import lcddriver
import RPi.GPIO as GPIO
import time
import os

# Set up GPIO mode and pin number
button_pin = 16  # Replace 17 with the GPIO pin number you're using
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize LCD display
display = lcddriver.lcd()
display.lcd_display_string("Device is READY", 1)  # Display "Device READY" on the first line


def capture(cam):
	
    suffix = "_R" if cam == 1 else "_L"
    cmd = "libcamera-still -o capture%d%s.jpg" % (cam, suffix)
    os.system(cmd)
    print("Captured image")
    display.lcd_display_string(" " * 16, 1)  # Clear the first line
    display.lcd_display_string(" " * 16, 2)
    display.lcd_display_string("Image captured", 1)
    display.lcd_display_string("Waiting",2)
    time.sleep(8)
    display.lcd_display_string(" " * 16, 1)  # Clear the first line
    display.lcd_display_string(" " * 16, 2)

def button_callback(channel):
    global image_count
    if GPIO.input(button_pin) == GPIO.LOW:
        if image_count == 0:
            capture(1)
        elif image_count == 1:
            capture(2)
            GPIO.cleanup()
            
            raise SystemExit("Exiting...")
        image_count += 1
        print("Captured image")

# Add event detection for the button press
GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=button_callback, bouncetime=200)

image_count = 0  # Counter for number of images captured

try:
    print("Waiting for button press...")
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
    
if image_count > 0:
	display.lcd_display_string(" " * 16, 1)  # Clear the first line
	display.lcd_display_string(" " * 16, 2)
	display.lcd_display_string("Succesfully ", 1)
	display.lcd_display_string("Captured",2)

