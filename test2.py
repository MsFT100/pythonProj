import socket
import json
import time
import mysql.connector

# Constants
RPT_INTERVAL_ON = 30   # Report interval in seconds when the engine is on
SLP_INTERVAL_OFF = 180  # Sleep interval in seconds when the engine is off

def handle_sms_command(command):
    response = None
    if command.startswith('111111ADD'):
        # Implement the logic to get the real physical address
        response = "City: New York, Street: Example Street"
    elif command.startswith('111111PSW'):
        # Implement the logic to change user password
        response = "Password changed successfully"
    # Implement other features

    return response

def handle_client(client_socket, db):
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if data:
                parsed_data = json.loads(data)
                if 'type' in parsed_data:
                    if parsed_data['type'] == 'can_data':
                        process_can_data(parsed_data, db)
                    elif parsed_data['type'] == 'sms_command':
                        response = handle_sms_command(parsed_data['command'])
                        client_socket.send(response.encode())
                    elif parsed_data['type'] == 'location_data':
                        process_location_data(parsed_data, db)
        except:
            client_socket.close()
            break

def process_can_data(data, db):
    print("Received CAN-BUS data:", data)
    cursor = db.cursor()
    
    # Check ignition status to determine engine state
    if data['data']['ignition_status'] == 'on':
        engine_state = 'on'
        rpt_interval = RPT_INTERVAL_ON
    else:
        engine_state = 'off'
        rpt_interval = SLP_INTERVAL_OFF
    
    sql = "INSERT INTO device_data (imei, engine_state, fuel_level, mileage, speed, rpm, engine_temperature, battery_voltage, throttle_opening, rpt_interval) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (data['imei'], engine_state, data['data']['fuel_level'], data['data']['mileage'], data['data']['speed'], data['data']['rpm'], data['data']['engine_temperature'], data['data']['battery_voltage'], data['data']['throttle_opening'], rpt_interval)
    
    cursor.execute(sql, values)
    db.commit()

def process_location_data(data, db):
    print("Received location data:", data)
    cursor = db.cursor()
    sql = "INSERT INTO location_data (imei, latitude, longitude) VALUES (%s, %s, %s)"
    values = (data['imei'], data['latitude'], data['longitude'])
    cursor.execute(sql, values)
    db.commit()

def main():
    server_ip = '172.31.40.67' 
    server_port = 8000

    db = mysql.connector.connect(
        host="demo-db.cmdsvmbxwqo9.eu-north-1.rds.amazonaws.com",
        user="admin",
        database="vehicleTelematicsDB",
        password="demo1234"
    )

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)

    print(f"Listening on {server_ip}:{server_port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
        
        handle_client(client_socket, db)
        
        client_socket.close()

if __name__ == "__main__":
    main()