import os

import uvicorn
from app.main import app as fastapi_app


def main():
    host = os.environ.get("CVALGOVIS_HOST", "127.0.0.1")
    port = int(os.environ.get("CVALGOVIS_PORT", "18000"))
    uvicorn.run(fastapi_app, host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
