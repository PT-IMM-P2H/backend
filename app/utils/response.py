# app/utils/response.py
from typing import Any, Optional
from fastapi.responses import JSONResponse

def base_response(message: str, payload: Any = None, status_code: int = 200):
    """
    Fungsi helper untuk menyeragamkan output JSON seperti saran senior Anda.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success" if status_code < 400 else "error",
            "message": message,
            "payload": payload
        }
    )