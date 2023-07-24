import serial
import time

arduino = serial.Serial(port='COM9', baudrate=9600, timeout=.1)

def write_read(x):
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = arduino.readline()
    return data

def blink_led():
    arduino.write(b'1')  # Sending '1' to the Arduino to trigger the LED blink
    time.sleep(0.05)
    data = arduino.readline()
    return data

def led_control(input_number):
    blinking_done = False

    while not blinking_done:
        random_value = '2'  # Change this to any random value other than '1'
        response = write_read(random_value)
        time.sleep(1)
        random_value = '2'  # Change this to any random value other than '1'
        response = write_read(random_value)
        time.sleep(1)
        print("Sent random value:", random_value)

        num = input_number
        time.sleep(1)
        if num == '1':
            response = blink_led()
            print("LED blinking:", response)
            blinking_done = True
        elif num == '0':
            response = write_read('0')
            print("LED Off:", response)
            blinking_done = True
        else:
            print("Invalid input. Only '1' or '0' triggers the LED action.")

def main():
    input_number = input("Enter a number (1 to blink the LED, 0 to turn off the LED): ")
    led_control(input_number)

if __name__ == "__main__":
    main()
