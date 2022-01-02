import shutil
from datetime import timedelta
from typing import Optional, List

from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import and_
from sqlalchemy.orm import Session

from Bike_app_v2 import crud, schemas, models
from Bike_app_v2.database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, crud.SECRET_KEY, algorithms=[crud.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = username
    except JWTError:
        raise credentials_exception
    user = crud.get_user(db, username=token_data)
    if user is None:
        raise credentials_exception
    return user


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", tags=['User'])
async def read_users_me(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.User.id, models.User.username, models.User.description, models.User.email,
                    models.User.url, models.User.address_city, models.User.address_province,
                    models.User.address_street, models.User.address_number, models.User.created_date, models.User.phone,
                    models.User.firstName, models.User.lastName
                    ).filter(
        models.User.id == current_user.id).first()


@app.post("/users/", tags=['User'])
def create_user(
        user: schemas.UserCreate, db: Session = Depends(get_db)
):

    return crud.create_user(db=db, user=user)


@app.put("/user_update/", tags=['User'])
def update(request: schemas.UserUpdate, db: Session = Depends(get_db),
           current_user: models.User = Depends(get_current_user)):
    db.query(models.User).filter(models.User.id == current_user.id).update(request.dict())
    db.commit()
    return "User updated "


@app.post("/posts/", tags=['Post'])
def create_post(
        tape_of_service: str,
        address_street: str,
        title: str,
        description: str,
        category_of_bike: str,
        address_city: str,
        address_province: str,
        address_number: str,
        price: Optional[float] = None,
        swapObject: Optional[bool] = None,
        rentalPeriod: Optional[float] = None,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    user_id = current_user.id

    if rentalPeriod == None and price == None and swapObject == None:
        return " Proszę wybrać formę transakcji"

    with open("photo/" + file.filename, "wb+")as img:
        shutil.copyfileobj(file.file, img)
    url = str("photo/" + file.filename)

    return crud.create_post(db=db, user_id=user_id, title=title, description=description, url=url,
                            tape_of_service=tape_of_service, category_of_bike=category_of_bike, price=price,
                            address_street=address_street, address_city=address_city, address_number=address_number,
                            swapObject=swapObject, rentalPeriod=rentalPeriod,
                            address_province=address_province)


@app.post("/post/{post_id}/add_photos", tags=['Post'])
def add_photos(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user),
               files: List[UploadFile] = File(...)):
    exists = db.query(models.Post).filter(models.Post.id == post_id).first() is not None

    if not exists:
        return "Zły numer id "

    if db.query(models.Comment).filter(and_(
            models.Post.id == post_id, models.Post.owner_id != current_user.id)).first():
        return "Nie możesz dodawać zdjęć do czyjegoś posta"

    for img in files:
        with open(f'{"photo/" + img.filename}', "wb") as buffer:
            shutil.copyfileobj(img.file, buffer)
            url = str("photo/" + img.filename)
            crud.add_new_photos(db=db, photo_url=url, comment_id=post_id)

    return {"file_name": "Good"}


@app.get("/post_list/", tags=['Post'])
def post_list(db: Session = Depends(get_db)):
    return crud.post_list(db=db)


@app.get("/post/{post_id}", tags=['Post'])
def post_detail(post_id: int, db: Session = Depends(get_db)):
    exists = db.query(models.Post).filter(models.Post.id == post_id).first() is not None

    if not exists:
        return "Zły numer id "

    post = crud.get_post(db=db, id=post_id)
    post_photo = crud.posts_photo(db=db, post_id=post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="Nie istnieje post o takim numerze ID")
    return {"Post Details": post, "Post Photo": post_photo}


@app.put("/post/{post_id}", tags=['Post'])
def update(post_id: int, request: schemas.PostBase, db: Session = Depends(get_db),
           current_user: models.User = Depends(get_current_user)):
    exists = db.query(models.Post).filter(models.Post.id == post_id).first() is not None

    if not exists:
        return "Zły numer id "

    if db.query(models.Post).filter(and_(
            models.Post.id == post_id, models.Post.owner_id != current_user.id)).first():
        return "Nie możesz edytować czyjegoś posta"

    db.query(models.Post).filter(models.Post.id == post_id).update(request.dict())
    db.commit()
    return "Post updated "


@app.delete("/post/{post_id}", tags=['Post'])
def destroy(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    exists = db.query(models.Post).filter(models.Post.id == post_id).first() is not None
    print(str(exists))

    if not exists:
        return "Zły numer id "

    if db.query(models.Comment).filter(and_(
            models.Post.id == post_id, models.Post.owner_id != current_user.id)).first():
        return "Nie możesz usuwać czyjegoś posta"

    post = db.query(models.Post).filter(models.Post.id == post_id).delete(synchronize_session=False)
    db.commit()
    return "Post ha been deleated "


@app.post("/user_posts/", tags=['Post'])
def user_post(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user_posts = crud.get_user_post(db=db, user_id=current_user.id)
    return user_posts


@app.get("/user/{user_id}", tags=['User'])
def user_post(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db=db, user_id=user_id)
    return user


@app.post("/search_post/", tags=['Post'])
def post_filter(title: Optional[str] = None, tape_of_service: Optional[str] = None,
                category_of_bike: Optional[str] = None, min_price: Optional[float] = None,
                address_province: Optional[str] = None,
                swapObject: Optional[bool] = None,
                rentalPeriod: Optional[float] = None,
                max_price: Optional[float] = None, db: Session = Depends(get_db)):
    posts = crud.search_post(db=db, title=title, tape_of_service=tape_of_service, category_of_bike=category_of_bike,
                             min_price=min_price, max_price=max_price, address_province=address_province,
                             swapObject=swapObject, rentalPeriod=rentalPeriod
                             )

    if posts is None:
        raise HTTPException(status_code=404, detail="Nie istnieje post o takim numerze ID")
    return posts


@app.post("/user/{user_id}/comment/", tags=['Comment'])
def create_comment(user_id: int, mark: int, comment: schemas.Comments,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)
                   ):
    if user_id == current_user.id:
        return "Nie możesz oceniać własnego profilu"

    return crud.create_comment(db=db, creator_id=current_user.id, user_id=user_id, comment=comment, mark=mark)


@app.post("/user_comments/{user_id}", tags=['User'])
def comment_detail(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if user_id != Depends(get_current_user):
        user = crud.get_user_by_id(db=db, user_id=user_id)
        comment = db.query(models.Comment).filter(models.Comment.owner_id == user_id)
        active_comment = comment.filter(models.Comment.is_active == True).all()

    if user is None:
        raise HTTPException(status_code=404, detail="Nie istnieje user o takim numerze ID")
    return {"user": user, "comment": active_comment}


@app.put("/comment_update/{comment_id}", tags=['Comment'])
def update(comment_id: int, request: schemas.CommentsUpdate, db: Session = Depends(get_db),
           current_user: models.User = Depends(get_current_user)):
    exists = db.query(models.Comment).filter(models.Comment.id == comment_id).first() is not None
    print(str(exists))

    if not exists:
        return "Zły numer id "

    if db.query(models.Comment).filter(and_(
            models.Comment.id == comment_id,
            models.Comment.creator_id != current_user.id)).first():
        return "Nie możesz edytować czyjegoś komentarza"

    db.query(models.Comment).filter(models.Comment.id == comment_id).update(request.dict())
    db.commit()
    return "Comment updated "


@app.delete("/comment/{comment_id}", tags=['Comment'])
def destroy(comment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    exists = db.query(models.Comment).filter(models.Comment.id == comment_id).first() is not None
    print(str(exists))

    if not exists:
        return "Zły numer id "

    if db.query(models.Comment).filter(and_(
            models.Comment.id == comment_id,
            models.Comment.creator_id != current_user.id)).first():
        return "Nie możesz usuwać czyjegoś komentarza"

    if db.query(models.Comment).filter(models.Comment.id == comment_id).filter(
            models.Comment.owner_id == current_user.id).first():
        return "Nie możesz usuwać czyjegoś komentarza"

    post = db.query(models.Comment).filter(models.Comment.id == comment_id).delete(synchronize_session=False)
    db.commit()
    return "Comment has been deleated "


@app.get("/user_comments/{user_id}", tags=['Comment'])
def user_comments(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_posts(db=db, user_id=user_id)
    return user


@app.post("/photos/")
def all_photos(db: Session = Depends(get_db)):
    return db.query(models.Photo).all()
