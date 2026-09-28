from main import app
from support_api import router as support_router

app.include_router(support_router)
