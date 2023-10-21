from src.database import save_to_sql
from src.bluetooth import data_queue

def process_data():
    while True:
        mac_address, heartbeat_value = data_queue.get()
        save_to_sql(mac_address, heartbeat_value)


