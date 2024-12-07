import serial
import time

class USBSerial:
    def __init__(self, port='/dev/ttyACM0', baudrate=9600, timeout=1):
        """
        Initialize USB Serial communication.
        :param port: Serial port to use (e.g., '/dev/ttyACM0').
        :param baudrate: Communication speed in baud.
        :param timeout: Read timeout in seconds.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

    def open(self):
        """Open the serial port."""
        try:
            self.ser = serial.Serial(self.port, baudrate=self.baudrate, timeout=self.timeout)
            print(f"Serial port {self.port} opened successfully.")
        except serial.SerialException as e:
            print(f"Failed to open serial port {self.port}: {e}")
            raise

    def close(self):
        """Close the serial port."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"Serial port {self.port} closed.")

    def send(self, data):
        """
        Send data through the serial port.
        :param data: String data to send.
        """
        if self.ser and self.ser.is_open:
            self.ser.write(data.encode())
            print(f"Sent: {data}")
        else:
            print("Serial port is not open. Cannot send data.")

    def receive(self):
        """
        Receive data from the serial port.
        :return: Received string data, or None if no data is available.
        """
        if self.ser and self.ser.is_open:
            if self.ser.in_waiting > 0:
                received_data = self.ser.readline().decode('utf-8', errors='ignore').strip()
                return received_data
            else:
                return None
        else:
            print("Serial port is not open. Cannot receive data.")
            return None

    def listen(self, delay=1):
        """
        Continuously listen for data on the serial port.
        :param delay: Delay between read attempts (in seconds).
        """
        print("Listening for data...")
        try:
            while True:
                received_data = self.receive()
                if received_data:
                    print(f"Received: {received_data}")
                time.sleep(delay)
        except KeyboardInterrupt:
            print("Listening stopped by user.")

# Example usage
if __name__ == "__main__":
    usb_serial = USBSerial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
    try:
        usb_serial.open()
        usb_serial.send("Hello ACM UART!")
        usb_serial.listen()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        usb_serial.close()
