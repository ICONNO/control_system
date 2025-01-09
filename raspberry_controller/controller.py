import psutil
import threading

class RaspberryController:
    def __init__(self):
        self.system_health = 100.0
        self.error_count = 0
        self.last_error_time = 0
        
        self.check_system_health()
        
    def check_system_health(self):
        """
        Monitor system health and attempt recovery if needed
        """
        cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        
        if cpu_usage > 80 or memory_info.percent > 80:
            self.system_health = max(0, self.system_health - 10)
            self.log_message(f"High resource usage detected: CPU {cpu_usage}%, Memory {memory_info.percent}%", color="red")
        
        if self.error_count > 5:
            self.system_health = max(0, self.system_health - 10)
            self.attempt_system_recovery()
        
        threading.Timer(5.0, self.check_system_health).start()
        
