import requests


def list_of_works():
    token = "Token f0ca41d626d86c10038a4fff19d69f31f1ad86e1"
    headers = {"Authorization": token}
    params = {}
    while True:
        try:
            response = requests.get("https://dvmn.org/api/long_polling",
                                    headers=headers,
                                    params=params,
                                    timeout=10
                                    )
            response.raise_for_status()
            print(response.json())
            if response.json()["status"] == "timeout":
                params = {"timestamp": response.json()["timestamp_to_request"]}

        except requests.exceptions.ReadTimeout:
            continue
        except ConnectionError:
            continue


def send_request():
    list_of_works()



if __name__ == '__main__':
    send_request()
