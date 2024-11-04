from locust import HttpUser, task, between
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserBehavior(HttpUser):
    # Wait between 1 to 3 seconds between tasks
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_response_times = []

    def on_start(self):
        """Initialize user session"""
        logger.info("A new user is starting...")

    @task(2)
    def get_user_by_id(self):
        """Test endpoint to get user details"""
        user_id = 1  # Example user ID
        start_time = time.time()
        
        with self.client.get(f"/users/{user_id}", catch_response=True) as response:
            duration = time.time() - start_time
            self.total_response_times.append(duration)
            
            try:
                if response.status_code == 200:
                    logger.info(f"Successfully retrieved user {user_id}. Response time: {duration:.2f}s")
                    
                    # Monitor for potential bottlenecks
                    if duration > 2.0:  # Alert if response takes more than 2 seconds
                        logger.warning(f"High response time detected: {duration:.2f}s")
                else:
                    logger.error(f"Failed to get user {user_id}. Status code: {response.status_code}")
                    response.failure(f"Got wrong response code: {response.status_code}")
            except Exception as e:
                logger.error(f"Error during request: {str(e)}")
                response.failure(f"Request failed: {str(e)}")

    @task(1)
    def monitor_system_health(self):
        """Test endpoint to check system health"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                logger.info("System health check passed")
            else:
                logger.warning(f"System health check failed: {response.status_code}")

    def on_stop(self):
        """Calculate and log performance metrics"""
        if self.total_response_times:
            avg_response_time = sum(self.total_response_times) / len(self.total_response_times)
            max_response_time = max(self.total_response_times)
            
            logger.info(f"""
Performance Summary:
-------------------
Average Response Time: {avg_response_time:.2f}s
Maximum Response Time: {max_response_time:.2f}s
Total Requests: {len(self.total_response_times)}
            """)

# Locust settings in code (can be overridden by command line)
class Settings:
    host = "https://jsonplaceholder.typicode.com"
    users = 10
    spawn_rate = 1
    run_time = "1m"