from locust import HttpUser, TaskSet, task, between
import random
import string


class UserBehavior(TaskSet):
    def on_start(self):
        self.username = "".join(random.choices(string.ascii_lowercase, k=10))
        self.password = "Password123"
        self.email = f"{self.username}@example.com"

        response = self.client.post(
            "/api/register/client/",
            json={
                "user": {
                    "username": self.username,
                    "password": self.password,
                    "email": self.email,
                }
            },
        )

        if response.status_code != 201:
            print(f"Failed to register user: {response.status_code} {response.text}")
            return

        response = self.client.post(
            "/api/login/client/",
            json={"username": self.username, "password": self.password},
        )

        if response.status_code != 200:
            print(f"Failed to login: {response.status_code} {response.text}")
            return

        try:
            self.token = response.json().get("token")
        except ValueError:
            print(f"Failed to parse JSON response: {response.text}")
            return

    @task(1)
    def profile(self):
        if hasattr(self, "token"):
            self.client.get(
                "/api/profile/", headers={"Authorization": f"Token {self.token}"}
            )

    @task(2)
    def create_service(self):
        if hasattr(self, "token"):
            service_name = "".join(random.choices(string.ascii_lowercase, k=10))
            worker_ids = [1, 2, 3]
            response = self.client.post(
                "/api/services/",
                json={
                    "name": service_name,
                    "description": "Test service description",
                    "price": 100.00,
                    "workers": worker_ids,
                },
                headers={"Authorization": f"Token {self.token}"},
            )
            if response.status_code != 201:
                print(
                    f"Failed to create service: {response.status_code} {response.text}"
                )


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
