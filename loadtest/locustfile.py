"""Locust scenario for later controlled load tests.

Start a local app, then:
  locust -f loadtest/locustfile.py --host http://127.0.0.1:8000

Begin with a small user count and ramp gradually. Do not target infrastructure you do not own.
"""

from locust import HttpUser, between, task


class AutoScaleLabUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(5)
    def compute(self):
        self.client.get("/compute?iterations=250000", name="/compute")

    @task(2)
    def health(self):
        self.client.get("/health", name="/health")

    @task(1)
    def root(self):
        self.client.get("/", name="/")
