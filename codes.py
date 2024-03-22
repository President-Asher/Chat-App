import random

# Generate 1000 random eight-digit codes
codes = [str(random.randint(10000000, 99999999)) for _ in range(1000)]

# Print the codes
for code in codes:
    print(code)
