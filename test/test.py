import requests
import json
import os
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import argparse
URL = "http://127.0.0.1:8089"


def upload_monitor(monitor):
    ...


def foo():
    filename = "station01.csv"
    filepath = "./station01.csv"
    data = MultipartEncoder(fields={
        "file": (filename, open(filepath, 'rb')),
        "size": str(os.path.getsize(filepath)),
    })
    data = MultipartEncoderMonitor(data, upload_monitor)
    headers = {"Content-Type": data.content_type}
    with requests.post(f"{URL}/upload-file/", data=data, headers=headers) as res:
        res.status_code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')           # positional argument
    parser.add_argument('-c', '--count')      # option that takes a value
    parser.add_argument('-v', '--verbose',
                        action='store_true')
    
    args = parser.parse_args(["abc.py", "-c", "100"])
    ...


if __name__ == "__main__":
    main()
