from fastapi import APIRouter, FastAPI
from fastapi.responses import RedirectResponse
from app.api import auth, users, admin, webhooks

app = FastAPI(
    title="My REST API",
    description="API for managing users, accounts, and payments",
    version="1.0.0",
)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


# Define the API prefix
# Include routers with the specified prefix
router = APIRouter()

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(admin.router)
router.include_router(webhooks.router)

app.include_router(router)
