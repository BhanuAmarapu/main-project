import os
from dotenv import load_dotenv
from pathlib import Path

# Create a temporary .env file
with open('test.env', 'w') as f:
    f.write("KEY1=VALUE1\n")
    f.write("KEY2='VALUE2'\n")
    f.write("KEY3 = 'VALUE3'\n")
    f.write("KEY4 = VALUE4\n")

load_dotenv('test.env')

print(f"KEY1: |{os.getenv('KEY1')}|")
print(f"KEY2: |{os.getenv('KEY2')}|")
print(f"KEY3: |{os.getenv('KEY3')}|")
print(f"KEY4: |{os.getenv('KEY4')}|")

os.remove('test.env')
