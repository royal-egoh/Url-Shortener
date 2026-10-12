from fastapi import APIRouter, Depends, HTTPException, status, Header, Cookie, Response
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.models.short_link import *
from app.models.users import *
from sqlalchemy import select, update
from app.schemas.schemas import * 
from app.database import *
from app.services.services import *

router = APIRouter(prefix="/shorten", tags=["shorten"])

@router.get("/create-key")
def create_key_endpoint(response:Response, db: Session = Depends(get_db)):
    return create_key(response=response, db=db)

@router.post("/")
def create_url_endpoint(link: LinkCreate, key: Users = Depends(get_current_key), db: Session = Depends(get_db)):
    return create_url(link=link, key=key, db=db)

@router.get("/{shortcode}")
def retrieve_url_endpoint(shortcode:str, key: Users = Depends(get_current_key), db: Session = Depends(get_db)):
    return retrieve_url(url=shortcode, key=key, db=db)

@router.put("/{shortcode}") 
def update_url_endpoint(shortcode:str, link: LinkCreate, key: Users = Depends(get_current_key), db: Session = Depends(get_db)):
    return update_url(shortcode=shortcode, url = link.url, key=key, db=db)

@router.delete("/{shortcode}")
def delete_url_endpoint(shortcode:str, key: Users = Depends(get_current_key), db: Session = Depends(get_db)):
    return delete_url(shortcode=shortcode, db=db)

@router.get("/url/{shortcode}")
def access_url(shortcode:str, key:Users = Depends(get_current_key),db:Session = Depends(get_db)):
    my_url = db.scalars(select(Links).where(Links.user_id==key.id, shortcode==shortcode)).first()
    if my_url is None:
        raise HTTPException(status_code=404, detail="Link not found")
    db.execute(update(Links).where(Links.id == my_url.id).values(accessCount=Links.accessCount + 1))
    db.commit()
    return RedirectResponse(my_url.url)

