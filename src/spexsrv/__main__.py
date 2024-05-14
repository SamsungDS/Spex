# SPDX-FileCopyrightText: 2023 Samsung Electronics Co., Ltd
#
# SPDX-License-Identifier: BSD-3-Clause


from os import environ

from spexsrv.application.app import app


def main() -> None:
    app.run(port=int(environ.get("SPEXSRV_PORT", 5050)), debug=True)


if __name__ == "__main__":
    main()
