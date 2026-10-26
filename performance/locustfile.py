from locust import HttpUser, between, task


class RegistrationPortalUser(HttpUser):
    wait_time = between(0.5, 1.0)

    @task(5)
    def retrieve_competitions(self):
        with self.client.post(
            "/showSummary",
            data={"email": "test@example.com"},
            name="POST /showSummary (competition list)",
            catch_response=True,
        ) as response:
            if response.status_code != 200 or "Test Competition" not in response.text:
                response.failure("Competition list was not returned")

    @task(1)
    def update_points(self):
        with self.client.post(
            "/purchasePlaces",
            data={
                "club": "Test Club",
                "competition": "Test Competition",
                "places": "1",
            },
            name="POST /purchasePlaces (points update)",
            catch_response=True,
        ) as response:
            if response.status_code != 200 or "Great-booking complete!" not in response.text:
                response.failure("Booking did not complete successfully")
