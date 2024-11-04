from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5) # tunggu antara 1 hingga 5 detik sebelum request selanjutnya

    @task
    def get_users(self):
        self.client.get('/users')