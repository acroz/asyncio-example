from flask import Flask, request


app = Flask(__name__)


@app.route("/status", methods=["PUT"])
def status():
    body = request.get_json(force=True)
    print(f"Received status {body['status']}")
    return "", 200


@app.route("/heartbeat", methods=["PUT"])
def heartbeat():
    print("Received heartbeat")
    return "", 200


if __name__ == "__main__":
    app.run()
