from fastapi import FastAPI
import api.token as token_module


def create_app() -> FastAPI:
    app = FastAPI(
        title='access-token-service',
        debug=True
    )

    app.include_router(token_module.router)

    return app

app = create_app()
