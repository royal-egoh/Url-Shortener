from app.models.users import *
from app.models.short_link import *
from fastapi import APIRouter, Depends, HTTPException, status, Header, Cookie, Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.schemas.schemas import *
from app.database import get_db
import hashlib
import secrets
import string

ALPHABET = string.ascii_letters + string.digits


def generate_code(length: int = 7) -> str:
    return "".join(secrets.choice(ALPHABET) for i in range(length))


def hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def get_current_key(x_api_key: str = Header(default=None), db: Session = Depends(get_db), api_key: str | None = Cookie(default=None)):
    raw = x_api_key or api_key
    if raw is None:
        raise HTTPException(401, "Missing API key")
    key = db.scalars(select(Users).where(Users.api_key == hash_key(raw))).one_or_none()
    if key is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key


def create_key(response: Response, db: Session):
    key = "sk_" + generate_code()
    new_user = Users(api_key=hash_key(key))
    db.add(new_user)
    db.commit()
    response.set_cookie(
        "api_key", key,
        httponly=True,     
        samesite="lax",   
        secure=True,       
        max_age=60 * 60 * 24 * 365,
    )
    return {"api key": key}


def create_url(link: LinkCreate, key: Users, db: Session):
    new_url = Links(url=link.url, shortcode=generate_code(), user_id=key.id)
    db.add(new_url)
    db.commit()
    return LinkResponse.model_validate(new_url)


def retrieve_url(url: str, key: Users, db: Session):
    my_urls = db.scalars(select(Links).where(Links.user_id == key.id, Links.url==url)).first()
    if not my_urls:
        raise HTTPException(status_code=401, detail="No URL's found")
    return LinkResponse.model_validate(my_urls)


def update_url(shortcode: str, url: str, key: Users, db: Session):
    my_url = db.scalars(select(Links).where(Links.user_id == key.id, Links.shortcode==shortcode)).one_or_none()
    if not my_url:
        raise HTTPException(status_code=401, detail="No URL's found")
    my_url.url = url
    db.commit()
    return LinkResponse.model_validate(my_url)


def delete_url(shortcode: str, key: Users, db: Session):
    my_urls = db.scalars(select(Links).where(Links.user_id == key.id, Links.shortcode==shortcode)).first()
    if not my_urls:
        raise HTTPException(status_code=404, detail="URL not found")
    db.delete(my_urls)
    db.commit()
    pass


