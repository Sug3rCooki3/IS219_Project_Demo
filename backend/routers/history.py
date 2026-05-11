from fastapi import APIRouter

import database


router = APIRouter()


@router.get("/history")
async def get_history():
    return {"sessions": database.get_all_sessions()}
