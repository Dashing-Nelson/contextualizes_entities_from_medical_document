import uvicorn

from app.main import app
from app.util.config import http_port

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=http_port)
