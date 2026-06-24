from fastapi import FastAPI, Depends, status
from fastapi.responses import JSONResponse
from fastapi_swagger import patch_fastapi
from fastapi.exceptions import RequestValidationError
from starlette.middleware import Middleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from account.routes.auth import router as account_auth_router
from account.routes.token import router as account_token_router
from cost.routes import router as cost_router
from middleware.i18n_middleware import I18nMiddleware
from dependencies.translation import get_translation_function
from config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_pool = aioredis.from_url(settings.REDIS_URL)
    FastAPICache.init(RedisBackend(redis_pool), prefix="fastapi-cache")
    print("Redis cache initialized.")
    yield
    # پاکسازی در shutdown
    if redis_pool:
        await redis_pool.close()
        print("Redis connection closed.")



app = FastAPI(lifespan=lifespan, docs_url=None, swagger_ui_oauth2_redirect_url=None)
patch_fastapi(app, docs_url="/swagger")


app.include_router(account_auth_router)
app.include_router(account_token_router)
app.include_router(cost_router)

middleware = [
    Middleware(I18nMiddleware, default_locale="en", locale_dir="locales")
]

app.add_middleware(I18nMiddleware, default_locale="en", locale_dir="locales")



@app.exception_handler(StarletteHTTPException)
async def http_exception_nandler(request, exc):
    error_response = {
        "success": False, 
        "status_code": exc.status_code, 
        "message": str(exc.detail),
        "path": request.url.path 

    }
    return JSONResponse(status_code=exc.status_code, content=error_response)



@app.exception_handler(RequestValidationError)
async def http_exception_nandler(request, exc):
    errors_details = []
    for error in exc.errors():
        errors_details.append({
            "field": ".".join(map(str, error["loc"])),
            "message": error["msg"], 
            "type": error["type"]
        })

    custom_error_body = {
        "success": False, 
        "message": "Data is not valid",
        "details": errors_details,
        "path": request.url.path 
    }
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=custom_error_body,
    )





@app.get("/translation/1")
def translation_test_1(get_text=Depends(get_translation_function)):
    return JSONResponse({"message": get_text("greeting")})


@app.get("/translation/2")
def translation_test_2(get_text=Depends(get_translation_function)):
    return JSONResponse({"message": get_text("farewell")})

