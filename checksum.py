def calculate_checksum(data):
    checksum = 0xFFFF
    for byte in data:
        checksum ^= byte
        for _ in range(8):
            if checksum & 0x0001:
                checksum >>= 1
                checksum ^= 0xA001
            else:
                checksum >>= 1
    return checksum.to_bytes(2, byteorder='little')

# Example packet data
#packet_data = b'\x00\x11is\x10Q1\x80\x87P\x00'
packet_data = b'\x00\x11is\x10Q1\x80\x87P\x00'
checksum = calculate_checksum(packet_data)

print(f"Calculated Checksum: {checksum.hex()}")
