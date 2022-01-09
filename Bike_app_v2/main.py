import shutil
from datetime import timedelta
from typing import Optional, List

from fastapi import Depends, FastAPI, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from rest_framework.status import HTTP_200_OK
from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles

from Bike_app_v2 import crud, schemas, models
from Bike_app_v2.database import SessionLocal, engine, Base

from starlette.responses import JSONResponse
from starlette.requests import Request
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel
from typing import List
from fastapi_mail.email_utils import DefaultChecker
import uuid
import cloudinary.uploader

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

conf = ConnectionConfig(
    MAIL_USERNAME="konrad.matuszewski.98@gmail.com",
    MAIL_PASSWORD="Qaswqasw123",
    MAIL_FROM="konrad.matuszewski.98@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="Desired Name",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/photo", StaticFiles(directory="photo"), name="photo")

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
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)


@app.post("/add_user_photo/", tags=['User'])
def add_user_photo(user_id: int, db: Session = Depends(get_db), file: UploadFile = File(...)):

    exists = db.query(models.User).filter(models.User.id == user_id).first() is not None
    if not exists:
        return "Zły numer id "

    user = db.query(models.User).filter(models.User.id == user_id).first()
    # with open("photo/" + file.filename, "wb+") as img:
    #     shutil.copyfileobj(file.file, img)
    # url = str("photo/" + file.filename)

    result = cloudinary.uploader.upload(file.file)
    url = result.get("url")


    user.url = url
    db.commit()
    db.refresh(user)
    return url


@app.patch("/update_user/", tags=['User'])
async def update_profile(data: schemas.UserUpdate, current_user: models.User = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()

    if data.phone != 'string':
        user.phone = data.phone
    if data.email != 'string':
        user.email = data.email
    if data.address_province != 'string':
        user.address_province = data.address_province
    if data.address_city != 'string':
        user.address_city = data.address_city
    if data.address_street != 'string':
        user.address_street = data.address_street
    if data.address_number != 'string':
        user.address_number = data.address_number
    if data.firstName != 'string':
        user.firstName = data.firstName
    if data.lastName != 'string':
        user.lastName = data.lastName
    if data.description != 'string':
        user.description = data.description

    db.commit()
    return user


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
        swapObject: Optional[str] = None,
        rentalPeriod: Optional[float] = None,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    user_id = current_user.id

    if rentalPeriod == None and price == None and swapObject == None:
        return " Proszę wybrać formę transakcji"

    # with open("photo/" + file.filename, "wb+") as img:
    #     shutil.copyfileobj(file.file, img)
    # url = str("photo/" + file.filename)

    result = cloudinary.uploader.upload(file.file)
    url = result.get("url")

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

    if db.query(models.Post).filter(and_(
            models.Post.id == post_id, models.Post.owner_id != current_user.id)).first():
        return "Nie możesz dodawać zdjęć do czyjegoś posta"

    for img in files:
        result = cloudinary.uploader.upload(img.file)
        url = result.get("url")
        crud.add_new_photos(db=db, photo_url=url, comment_id=post_id)

        # with open(f'{"photo/" + img.filename}', "wb") as buffer:
        #     shutil.copyfileobj(img.file, buffer)
        #     url = str("photo/" + img.filename)
        #     crud.add_new_photos(db=db, photo_url=url, comment_id=post_id)

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


@app.patch("/post/{post_id}", tags=['Post'])
def update(post_id: int, request: schemas.PostBase, db: Session = Depends(get_db),
           current_user: models.User = Depends(get_current_user)):
    exists = db.query(models.Post).filter(models.Post.id == post_id).first() is not None

    if not exists:
        return "Zły numer id "

    if db.query(models.Post).filter(and_(
            models.Post.id == post_id, models.Post.owner_id != current_user.id)).first():
        return "Nie możesz edytować czyjegoś posta"

    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if request.title != 'string':
        post.title = request.title
    if request.description != 'string':
        post.description = request.description
    if request.tape_of_service != 'string':
        post.tape_of_service = request.tape_of_service
    if request.address_province != 'string':
        post.address_province = request.address_province
    if request.address_city != 'string':
        post.address_city = request.address_city
    if request.address_street != 'string':
        post.address_street = request.address_street
    if request.address_number != 'string':
        post.address_number = request.address_number
    if request.price != 0:
        post.price = request.price
    if request.category_of_bike != 'string':
        post.category_of_bike = request.category_of_bike
    if request.rentalPeriod != 0:
        post.rentalPeriod = request.rentalPeriod
    if request.swapObject != 'string':
        post.swapObject = request.swapObject
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


@app.get("/user_posts/", tags=['Post'])
def user_post(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user_posts = crud.get_user_post(db=db, user_id=current_user.id)
    return user_posts


@app.get("/user/{user_id}", tags=['User'])
def user_details(user_id: int, db: Session = Depends(get_db)):
    exists = db.query(models.User).filter(models.User.id == user_id).first() is not None
    if not exists:
        return "Nie istnieje użytkownik o takim id"

    user = crud.get_user_by_id(db=db, user_id=user_id)
    mark = crud.str_mark(db=db, user_id=user_id)
    return {'User info': user, 'Mark info': mark}


@app.post("/search_post/", tags=['Post'])
def post_filter(title: Optional[str] = None, tape_of_service: Optional[str] = None,
                category_of_bike: Optional[str] = None, min_price: Optional[float] = None,
                address_province: Optional[str] = None,
                swapObject: Optional[str] = None,
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

    return crud.create_comment(db=db, creator_id=current_user.id, user_id=user_id, email=current_user.email,
                               comment=comment, mark=mark)


@app.post("/user_comments/{user_id}", tags=['User'])
def comment_detail(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if user_id != Depends(get_current_user):
        user = crud.get_user_by_id(db=db, user_id=user_id)
        comment = db.query(models.Comment).filter(models.Comment.owner_id == user_id)
        active_comment = comment.filter(models.Comment.is_active == True).all()

    if user is None:
        raise HTTPException(status_code=404, detail="Nie istnieje user o takim numerze ID")
    return {"user": user, "comment": active_comment}


@app.patch("/comment_update/{comment_id}", tags=['Comment'])
def update(comment_id: int, request: schemas.CommentsUpdate, db: Session = Depends(get_db),
           current_user: models.User = Depends(get_current_user)):
    exists = db.query(models.Comment).filter(models.Comment.id == comment_id).first() is not None

    if not exists:
        return "Zły numer id "

    if db.query(models.Comment).filter(and_(
            models.Comment.id == comment_id,
            models.Comment.creator_id != current_user.id)).first():
        return "Nie możesz edytować czyjegoś komentarza"

    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()

    if request.name != 'string':
        comment.name = request.name
    if request.description != 'string':
        comment.description = request.description
    if request.mark != 0:
        if request.mark >= 0 and request.mark <= 5:
            comment.mark = request.mark
        else:
            return 'Ocena moze być z przedziału 0 do 5 '

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


@app.get("/user_comments/{user_id}", tags=['Mark'])
def get_mark(user_id: int, db: Session = Depends(get_db)):
    user = crud.str_mark(db=db, user_id=user_id)
    return user


@app.post("/photos/")
def all_photos(db: Session = Depends(get_db)):
    return db.query(models.Photo).all()


@app.post("/email/{to_mail}")
async def send_email(to_mail: str, db: Session = Depends(get_db)):
    exists = db.query(models.User).filter(models.User.email == to_mail).first() is not None

    print(str(exists))

    if exists == False:
        return "Taki email nie istnieje w naszej bazie danych "

    user_id_by_email = db.query(models.User).filter(models.User.email == to_mail).first()

    user = crud.get_user_by_id(db, user_id=user_id_by_email.id)

    reset_code = str(uuid.uuid1())

    crud.create_reset_code(db, to_mail, reset_code)

    html = f"""
    <p></p>
    <p>Przypomnienie twojego hasla</p>
    <p>Uzytkowniku {user.username}<p>
    <p> dostaliśy prośbę o resetowanie towejgo hasła do naszego portalu poniżej otrzymasz cod to restaru swojego konta</p>
    <p> Kod resetujący hasło: {reset_code} </p>

    <br>test<br>
    """

    message = MessageSchema(
        subject="Przypomninie hasla",
        recipients=[to_mail],  # List of recipients, as many as you can pass
        body=html,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    return {'Status': 'Chyba poszlo', 'Reset coede': reset_code}


@app.post("/code/")
def code(db: Session = Depends(get_db)):
    return db.query(models.Code).all()


@app.patch("/reset_password/")
async def reset(request: schemas.Reset_password, db: Session = Depends(get_db)):
    reset_token = crud.check_password(db=db, reset_password_token=request.reset_password_token)
    email_for_this_token = db.query(models.Code).filter(models.Code.reset_code == request.reset_password_token).first()
    if reset_token == None:
        return ('Error')

    if request.new_password != request.confirm_password:
        return ("Hasła są różne")

    # forgot_pass = schemas.Forgot_pass(reset_token)
    new_hash_pas = crud.get_password_hash(request.new_password)
    crud.reset_password(db=db, new_hash_pas=new_hash_pas, email=email_for_this_token.email)

    return 'Sukces'
