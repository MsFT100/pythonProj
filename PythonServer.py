import socket
import threading
import re

HOST = ''  # Listening to any
PORT = 8000  # The port number of the server

exit_flag = threading.Event()  # Event for indicating when to exit

# Create a socket using IPv4 and TCP protocol
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        # Bind the socket to the specified IP address and port
        s.bind((HOST, PORT))

        # Listen for incoming connections
        s.listen(1)
        print(f"TCP Server is listening on {HOST}:{PORT}")

        # Accept a client connection
        conn, addr = s.accept()
        print(f"Connected by {addr}")

        with conn:
            while not exit_flag.is_set():
                # Receive data from the client using ASCII encoding
                data = conn.recv(1024)
                if not data:
                    break

                decoded_data = data.decode('utf-8', errors='ignore')
                print(f'Received data from GPS Tracker: {decoded_data}')

                # Split the GPS data packet
                data_parts = re.split(',|\|', decoded_data)
            # Check the number of data parts
            if len(data_parts) > 15:
                # Extracting information from each data parts
                protocol_header = data_parts[0]
                gps_signal_status = data_parts[1]
                latitude = data_parts[2] + data_parts[3]  
                longitude = data_parts[4] + data_parts[5]   
                speed_knots = data_parts[6]
                course_degrees = data_parts[7]
                timestamp = data_parts[8]
                magnetic_variation = data_parts[9]
                ew_indicator = data_parts[10]
                gps_fix = data_parts[11]
                horizontal_dilution = data_parts[12]
                altitude_meters = data_parts[13]
                input_output_status = data_parts[14]
                analog_data_1 = data_parts[15]
                analog_data_2_hex = data_parts[16]  # Hexadecimal format

                # Convert hexadecimal analog_data_2 to decimal
                try:
                    analog_data_2_decimal = int(analog_data_2_hex, 16)
                    # Calculate external car battery voltage in volts
                    battery_voltage = (analog_data_2_decimal * 6) / 1024
                except ValueError:
                    analog_data_2_decimal = None
                    battery_voltage = None

                odometer_meters = data_parts[17]
                rfid = data_parts[18]

                # Check if input and output status is "0000" to determine device activity
                device_active = input_output_status != "0000"
                
                # Print the extracted information
                print("Protocol Header:", protocol_header)
                print("GPS Signal Status:", "Valid" if gps_signal_status == "S" else "Invalid")
                print("Latitude:", latitude)
                print("Longitude:", longitude)
                print("Speed (knots):", speed_knots)
                print("Course (degrees):", course_degrees)
                # Format timestamp as DD/MM/YYYY
                timestamp_parts = [timestamp[0:2], timestamp[2:4], "20" + timestamp[4:6]]
                formatted_timestamp = "/".join(timestamp_parts)
                print("Timestamp (DD/MM/YYYY):", formatted_timestamp)
                print("Magnetic Variation:", magnetic_variation)
                print("East/West Indicator:", "East" if ew_indicator == "E" else "West")
                print("GPS Fix:", "Valid" if gps_fix == "A" else "Invalid")
                print("Horizontal Dilution:", horizontal_dilution)
                print("Altitude (meters):", altitude_meters)
                print("Input/Output Status:", input_output_status)
                print("Device Active:", "Yes" if device_active else "No")
                print("Analog Data 1:", analog_data_1)
                print("Analog Data 2 (Hexadecimal):", analog_data_2_hex)
                # Check if analog_data_2 was successfully converted to decimal
                if analog_data_2_decimal is not None:
                    print("External Car Battery Voltage:", battery_voltage, "Volts")
                else:
                    print("External Car Battery Voltage: Invalid Data")
                print("Odometer (meters):", odometer_meters)
                print("RFID:", rfid)
            else:
                 # Print the protocol header even when the number of data parts is not 18
                print("Protocol Header Only Received")

                # Send the received data back to the client using ASCII encoding
                conn.sendall(data)

    except Exception as e:
        print(f"An error occurred: {e}")

print("Server has closed.")