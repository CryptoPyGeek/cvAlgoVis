import os

import uvicorn


def main():
    host = os.environ.get("CVALGOVIS_HOST", "127.0.0.1")
    port = int(os.environ.get("CVALGOVIS_PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
