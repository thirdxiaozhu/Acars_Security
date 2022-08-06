from rtlsdr import RtlSdr

serial_numbers = RtlSdr.get_device_serial_addresses()
print(serial_numbers)
device_index = RtlSdr.get_device_index_by_serial('00000001')
print(device_index)