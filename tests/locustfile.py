from locust import HttpUser, task, between


class RequestOnlyUser(HttpUser):
    # wait_time = between(1, 10)

    @task(weight=4)
    def benchmark(self):
        self.client.get("/benchmark")

    # @task(weight=2)
    # def profiles(self):
    #     self.client.get("/profiles")
    #
    # @task
    # def about(self):
    #     self.client.get("/about")
