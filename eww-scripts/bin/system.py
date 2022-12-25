import time
import psutil


def get_network_speed() -> tuple:
    """
        The get_network_speed function returns the current network speed in bytes per second.
        The function takes no arguments and returns a tuple of four values:
        (sent_speed, sent_units, recv_speed, recv_units).
        The first two values are the speeds of data being sent by your computer.
        The second two values are the units for those speeds.
        
        :return: A tuple of four values:
    """
    
    initial_stats = psutil.net_io_counters()
    time.sleep(1)
    final_stats = psutil.net_io_counters()

    bytes_sent = final_stats.bytes_sent - initial_stats.bytes_sent
    bytes_recv = final_stats.bytes_recv - initial_stats.bytes_recv

    if bytes_sent > 1024**2:
        sent_units = "MB"
        sent_speed = bytes_sent / 1024**2
    elif bytes_sent > 1024:
        sent_units = "KB"
        sent_speed = bytes_sent / 1024
    else:
        sent_units = "B"
        sent_speed = bytes_sent
    if bytes_recv > 1024**2:
        recv_units = "MB"
        recv_speed = bytes_recv / 1024**2
    elif bytes_recv > 1024:
        recv_units = "KB"
        recv_speed = bytes_recv / 1024
    else:
        recv_units = "B"
        recv_speed = bytes_recv

    return (sent_speed, sent_units, recv_speed, recv_units)


def cpu_value():
    cpu_usage = psutil.cpu_percent(percpu=True)

    for i, usage in enumerate(cpu_usage):
        print(f'CPU {i}: {usage}%')


if __name__ == '__main__':
    cpu_value()
    