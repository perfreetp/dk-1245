import os
import time

try:
    os.remove("c:/TraeProjects/1245/running_training.db")
    print("Database deleted successfully")
except Exception as e:
    print(f"Error: {e}")

time.sleep(2)
