import argparse
import random
import time
import httpx

URL = "http://localhost:8080/authorize"   # via kubectl port-forward svc/payment-auth 8080:80

def normal():
    return {
        "card_token": f"tok_{random.randint(1, 50)}",
        "amount": random.randint(10, 500),
        "merchant_id": f"m{random.randint(1, 5)}",
    }

def chaos():
    # Same card repeatedly (trips velocity) + big amounts (trips amount rule) -> declines.
    return {"card_token": "tok_chaos", "amount": random.randint(6000, 9000), "merchant_id": "m1"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chaos", action="store_true")
    parser.add_argument("--rps", type=int, default=5)
    args = parser.parse_args()

    make = chaos if args.chaos else normal
    with httpx.Client(timeout=5) as client:
        while True:
            try:
                r = client.post(URL, json=make())
                print(r.status_code, r.json().get("decision"))
            except Exception as e:
                print("error:", e)
            time.sleep(1 / args.rps)

if __name__ == "__main__":
    main()