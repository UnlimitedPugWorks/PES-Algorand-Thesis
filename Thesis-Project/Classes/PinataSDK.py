import requests
import json

BASE_URL = "https://api.pinata.cloud"


class PinataSDK:
    def __init__(self, API_key, API_secret):
        self.API_key = API_key
        self.API_secret = API_secret

    '''
    Gets Headers
    '''

    def get_headers(self) -> dict:
        headers = {
            'pinata_api_key': self.API_key,
            'pinata_secret_api_key': self.API_secret
        }
        return headers

    '''
    Tests if the authentication is working. If it is, it returns 200
    '''

    def test(self) -> int:
        request_url = BASE_URL + "/data/testAuthentication"
        payload = {}
        response = requests.get(
            request_url, headers=self.get_headers(), data=payload)

        return response.status_code

    '''
    Pins a file to IPFS.
    '''

    def pin_file(self, file_name: str, file_path: str) -> dict:

        request_url = BASE_URL + "/pinning/pinFileToIPFS"

        payload = {
            'pinataOptions': '{"cidVersion": 1}',
            'pinataMetadata': '{"name": "MyFile", "keyvalues": {"company": "Pinata"}}'
        }

        files = [('file', (file_name, open(
            file_path, "rb")))]

        response = requests.request(
            "POST", request_url, headers=self.get_headers(), data=payload, files=files)

        return json.loads(response.text)

    def pin_json(self, json_name: str, json_to_pin: str):

        request_url = BASE_URL + "/pinning/pinFileToIPFS"

        payload = {
            'pinataOptions': '{"cidVersion": 1}',
            'pinataMetadata': '{"name": "MyFile", "keyvalues": {"company": "Pinata"}}'
        }

        files = [('file', (json_name, json_to_pin))]

        response = requests.request(
            "POST", request_url, headers=self.get_headers(), data=payload, files=files)

        return json.loads(response.text)

    def pin_folder(self, folder_name: str, folder_path: str):

        request_url = BASE_URL + "/pinning/pinFileToIPFS"

        payload = {
            'pinataOptions': '{"cidVersion": 1}',
            'pinataMetadata': '{"name": "MyFile", "keyvalues": {"company": "Pinata"}}'
        }

        files = [('file', (file_name, open(
            file_path, "rb")))]

        response = requests.request(
            "POST", request_url, headers=self.get_headers(), data=payload, files=files)

        return json.loads(response.text)       




'''
API Key: 701eb0b47f41e945a859
API Secret: caf08886c4b2dde12a3946b5ffebf94677cc941ca8b4cf414364da6570057c81
JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiI5NTk4MjY5Ni0zODZhLTQ2NDctYWZmNS02MTJhN2JkZGY4OTgiLCJlbWFpbCI6InRoZWJpcmRwYXRhcG9uQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaW5fcG9saWN5Ijp7InJlZ2lvbnMiOlt7ImlkIjoiRlJBMSIsImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxfSx7ImlkIjoiTllDMSIsImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxfV0sInZlcnNpb24iOjF9LCJtZmFfZW5hYmxlZCI6ZmFsc2UsInN0YXR1cyI6IkFDVElWRSJ9LCJhdXRoZW50aWNhdGlvblR5cGUiOiJzY29wZWRLZXkiLCJzY29wZWRLZXlLZXkiOiI3MDFlYjBiNDdmNDFlOTQ1YTg1OSIsInNjb3BlZEtleVNlY3JldCI6ImNhZjA4ODg2YzRiMmRkZTEyYTM5NDZiNWZmZWJmOTQ2NzdjYzk0MWNhOGI0Y2Y0MTQzNjRkYTY1NzAwNTdjODEiLCJpYXQiOjE2NjUwNjU1MDB9.2E0sIqA0RGsYlGk3OELN9mPHjVzsQHHOC0DwrvI-g2A
'''
