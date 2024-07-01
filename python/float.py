print("float(10):", float(10))  # Converting integer to float
print("float(10 + 5j):")  # Error: complex cannot be converted to float
try:
  print(float(10 + 5j))
except TypeError as e:
  print(e)

print("float(True):", float(True))  # Converting boolean to float (True -> 1.0)
print("float(False):", float(False))  # Converting boolean to float (False -> 0.0)

print("float('10'):", float("10"))  # Converting string (digits) to float
print("float('10.5'):", float("10.5"))  # Converting string (digits with decimal) to float

print("float('ten'):")  # Error: cannot convert string to float
try:
  print(float("ten"))
except ValueError as e:
  print(e)

print("float('0B1111'):")  # Error: cannot convert binary string to float
try:
  print(float("0B1111"))
except ValueError as e:
  print(e)
