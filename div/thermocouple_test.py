from max6675 import MAX6675

cs_pin = 38
clock_pin = 36
data_pin = 37
units = "c"
print('script started')
thermocouple = MAX6675(cs_pin, clock_pin, data_pin, units)
print(thermocouple.get())
thermocouple.cleanup()