from locust import HttpUser, task, between
import random

class QuickTestUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        self.logged_in = False
        self.login()
    
    def login(self):
        login_data = {
            "username": "Test",
            "password": "Test@123456"
        }
        response = self.client.post("/account/auth/login", json=login_data)
        if response.status_code == 200:
            self.logged_in = True
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
    
    def ensure_logged_in(self):
        """اگر خارج شده‌اید، دوباره وارد شوید"""
        if not self.logged_in:
            self.login()
    
    @task(5)
    def list_costs(self):
        self.ensure_logged_in()
        self.client.get("/costs")
    
    @task(3)
    def add_cost(self):
        self.ensure_logged_in()
        self.client.post("/costs", json={
            "description": "quick test",
            "amount": 12345
        })
    
    
    @task(1)
    def do_logout(self):
        if self.logged_in:
            response = self.client.post("/account/auth/logout")
            if response.status_code == 200:
                self.logged_in = False  