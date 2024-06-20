import re
from datetime import datetime
import secrets
import string
import base64

from fastapi import APIRouter, status, Body
from fastapi import Path as ApiPath

from typing import Dict

from starlette.responses import Response

from sqlalchemy import select, func

import db
from db.models import AccessToken

import config


router = APIRouter(prefix="/api")


@router.get("/tokens", status_code=status.HTTP_200_OK)
async def get_all_tokens(response: Response, session: db.CurrentSession, name: str = None):
    if name is not None:
        token = session.execute(select(AccessToken).where(AccessToken.name == name)).scalar()
        if token is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Token not found"}
        else:
            return token.to_dict()
    else:
        return session.scalars(select(AccessToken).order_by(AccessToken.expires)).all()


@router.get("/tokens/{token_id}", status_code=status.HTTP_200_OK)
async def get_token_details(response: Response, session: db.CurrentSession, token_id: str = ApiPath()):
    token = session.get(AccessToken, token_id)
    if token is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Token not found"}

    return token.to_dict()



@router.post("/tokens", status_code=status.HTTP_201_CREATED)
async def create_token(response: Response, session: db.CurrentSession, body: Dict = Body()):
    name = body["name"]
    email = body["email"]
    scopes = body["scopes"]

    if len(name) > config.TOKEN_NAME_LENGTH_LIMIT:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": f"The length of token name must not exceed 64 characters"}
    if not re.match(config.TOKEN_NAME_REGEX, name):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": f"Invalid token name"}

    if count_existing_token(session, email) >= config.MAXIMUM_TOKEN_NUMBER:
        response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
        return {"message": f"The number of existing tokens exceed the maximum allowed number"}

    if count_existing_token(session, email, name) >= 1:
        response.status_code = status.HTTP_409_CONFLICT
        return {"message": f"The token with this name already existed"}

    raw_token = "".join(
        (secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
    )
    hashed_token = config.PASSWORD_HASHER.hash(raw_token)
    token = AccessToken(
        name=name,
        token=hashed_token,
        email=email,
        expires=datetime.now() + config.TOKEN_TTL,
        created=datetime.now(),
        scopes=scopes
    )
    session.add(token)
    session.commit()
    encoded_token = base64.b64encode(f'{token.id}.{raw_token}'.encode("utf-8"))
    return {
        "id": token.id,
        "name": token.name,
        "token": encoded_token,
        "email": token.email,
        "expires": token.expires,
        "created": token.created,
        "last_used": token.last_used,
        "scopes": token.scopes
    }


@router.delete("/tokens/{token_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_token_by_id(response: Response, session: db.CurrentSession, token_id: str = ApiPath()):
    token = session.get(AccessToken, token_id)
    if token is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "Token not found"}

    session.delete(token)
    session.commit()
    return {"message": f"Successfully deleted the token with id {token.id}"}


@router.delete("/tokens", status_code=status.HTTP_202_ACCEPTED)
def delete_multiple_tokens(response: Response, session: db.CurrentSession, body: Dict = Body()):
    not_found_tokens = []
    deleted_tokens = []

    for token_id in body["ids"]:
        token = session.get(AccessToken, token)
        if token is None:
            not_found_tokens.append(token_id)
        else:
            deleted_tokens.append(token_id)
            session.delete(token)
            session.commit()
    if len(deleted_tokens) == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
    else:
        response.status_code = status.HTTP_202_ACCEPTED

    return {
        "deleted tokens": deleted_tokens,
        "not found tokens": not_found_tokens
    }


def count_existing_token(session, email: str, name: str = None):
    return session.execute(
        select(AccessToken)
        .where(AccessToken.email == email)
        .where(True if name is None else (AccessToken.name == name))
        .where(datetime.now() < AccessToken.expires)
        .with_only_columns(func.count())
    ).scalar()
