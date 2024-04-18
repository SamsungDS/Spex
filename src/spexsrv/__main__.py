from os import environ

from spexsrv.application.app import app


def main():
    app.run(port=int(environ.get("SPEXSRV_PORT", 5050)), debug=True)


if __name__ == "__main__":
    main()
