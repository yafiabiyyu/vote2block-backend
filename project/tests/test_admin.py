from project.tests.BaseCase import BaseCase
import json


class AdminTest(BaseCase):
    def test_admin_login(self):
        endpoint = self.base_url + "/auth/admin/login"
        payload = {"username": "admin", "password": "admin"}
        response = self.app.post(endpoint, json=payload)
        self.assertEqual(200, response.status_code)
        self.assertEqual("Berhasil", response.json["status"])

    def test_setup_waktu(self):
        # mendapatkan access token
        login_endpoint = self.base_url + "/auth/admin/login"
        payload_login = {"username": "admin", "password": "admin"}
        response = self.app.post(login_endpoint, json=payload_login)
        jwt_token = response.json["data"]["access_token"]

        # test endpoint setup waktu
        endpoint = self.base_url + "/admin/setting/waktu"
        payload = {
            "registerstart": "1623995040",
            "registerfinis": "1623995340",
            "votingstart": "1623995400",
            "votingfinis": "1623999000",
        }
        response = self.app.post(
            endpoint,
            headers={"Authorization": f"Bearer {jwt_token}"},
            json=payload,
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Berhasil", response.json["status"])

    def test_register_kandidat(self):
        # mendapatkan access token
        login_endpoint = self.base_url + "/auth/admin/login"
        payload_login = {"username": "admin", "password": "admin"}
        response = self.app.post(login_endpoint, json=payload_login)
        jwt_token = response.json["data"]["access_token"]

        # test register kandidat endpoint
        endpoint = self.base_url + "/admin/pendaftaran/kandidat"
        payload = {
            "kandidat_id": "1741720059",
            "nomor_urut": 1,
            "nama_kandidat": "Kandidat 1",
            "tanggal_lahir": "20/12/1998",
            "visi": "Lorem ipsum dolor",
            "misi": "Lorem ipsum dolor",
            "contact": {
                "email": "kandidat1@vote2block.eth",
                "phone": "085265341245",
            },
            "alamat": {
                "provinsi": "Jawa Timur",
                "kota": "Malang",
                "alamat_lengkap": "Jl Senggani No 40",
            },
            "image_url": "https://kandidatImage.eth",
        }
        response = self.app.post(
            endpoint,
            headers={"Authorization": f"Bearer {jwt_token}"},
            json=payload,
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Berhasil", response.json["status"])

    def test_register_pemilih(self):
        # mendapatkan access token
        login_endpoint = self.base_url + "/auth/admin/login"
        payload_login = {"username": "admin", "password": "admin"}
        response = self.app.post(login_endpoint, json=payload_login)
        jwt_token = response.json["data"]["access_token"]

        # test endpoint register pemilih
        endpoint = self.base_url + "/admin/pendaftaran/pemilih"
        payload = {
            "pemilih_id": "1741720099",
            "nama_lengkap": "Pemilih Stau",
            "tgl_lahir": "16/11/1998",
            "contact": {
                "email": "pemilihsatu@vote2block.eth",
                "phone": "082112410019",
            },
            "alamat": {
                "provinsi": "Banten",
                "kota": "Tangerang Selatan",
                "alamat_lengkap": "GRB Flamboyan Loka",
            },
        }
        response = self.app.post(
            endpoint,
            headers={"Authorization": f"Bearer {jwt_token}"},
            json=payload,
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual("Berhasil", response.json["status"])
