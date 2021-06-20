from project.tests.BaseCase import BaseCase


class VotingTest(BaseCase):
    def test_voting(self):
        endpoint_login = self.base_url + "/auth/pemilih/login"
        payload_login = {
            "username": "pemilihsatu",
            "password": "pemilihsatu",
        }
        login_response = self.app.post(
            endpoint_login, json=payload_login
        )
        jwt_token = login_response.json["data"]["access_token"]

        # voting test
        endpoint = self.base_url + "/voting/kandidat"
        payload = {"kandidatId": 1}
        response = self.app.post(
            endpoint,
            headers={"Authorization": f"Bearer {jwt_token}"},
            json=payload,
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Berhasil", response.json["status"])

    def test_quick_count(self):
        endpoint_login = self.base_url + "/auth/pemilih/login"
        payload_login = {
            "username": "pemilihsatu",
            "password": "pemilihsatu",
        }
        login_response = self.app.post(
            endpoint_login, json=payload_login
        )
        jwt_token = login_response.json["data"]["access_token"]

        # test quick count
        endpoint = self.base_url + "/voting/quickcount"
        response = self.app.get(
            endpoint, headers={"Authorization": f"Bearer {jwt_token}"}
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.json[0]["nomor_urut"])
        self.assertEqual(1, response.json[0]["total_suara"])
