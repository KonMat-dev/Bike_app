from fastapi.security import OAuth2PasswordBearer

from fastapi import  HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from . import models
from . import schemas
from .models import Post

SECRET_KEY = "b8dcbc5ec17ace5a8fd3faa893e1b071b3766d8ba09e4bbf5d7e85ea68046357"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate):
    exists = db.query(models.User).filter(models.User.username == user.username).first() is not None
    if exists:
        return "Użytkownik o takim niku już istnieje "

    exists_email = db.query(models.User).filter(models.User.email == user.email).first() is not None
    if exists_email:
        return "Użytkownik o takim email już istnieje "

    db_user = models.User(username=user.username, hashed_password=get_password_hash(user.password),
                          lastName=user.lastName, firstName=user.firstName, phone=user.phone,
                          address_number=user.address_number, address_street=user.address_street,
                          address_province=user.address_province, email=user.email,
                          address_city=user.address_city
                          )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_post(db: Session, user_id: int, price: float, title: str, description: str, url: str, tape_of_service: str,
                category_of_bike: str, address_city: str, address_number: str, address_province: str,
                swapObject: str, rentalPeriod: float,
                address_street: str):
    db_post = models.Post(title=title, description=description, owner_id=user_id, url=url,
                          tape_of_service=tape_of_service, category_of_bike=category_of_bike, price=price,
                          address_street=address_street, address_city=address_city, address_number=address_number,
                          address_province=address_province, swapObject=swapObject, rentalPeriod=rentalPeriod)

    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def add_photos(db: Session, post_id: str, picture: str):  # TODO sprawdz cz to poprawnie jest
    return models.Photo(post_id=post_id, picture=picture)


def get_post(db, id: int):
    return db.query(models.Post).filter(models.Post.id == id).first()


def get_user_post(db, user_id: int):
    return db.query(models.Post).filter(models.Post.owner_id == user_id).all()


def post_list(db):
    return db.query(models.Post).all()


def posts_photo(db, post_id: int):
    return db.query(models.Photo).filter(models.Photo.comment_id == post_id).all()


def search_post(db, title: Optional[str] = None, tape_of_service: Optional[str] = None,
                category_of_bike: Optional[str] = None, min_price: Optional[float] = None,
                max_price: Optional[float] = None,
                address_province: Optional[float] = None,
                swapObject: Optional[str] = None,
                rentalPeriod: Optional[float] = None,
                ):
    search = db.query(models.Post).distinct(Post.id)

    if title is not None:
        search = search.filter(models.Post.title.ilike(f'%{title}%'))

    if tape_of_service is not None:
        search = search.filter(models.Post.tape_of_service == tape_of_service)
    if category_of_bike is not None:
        search = search.filter(models.Post.category_of_bike.ilike(f'%{category_of_bike}%'))
    if address_province is not None:
        search = search.filter(models.Post.address_province == address_province)
    if min_price is not None:
        search = search.filter(models.Post.price >= min_price)
    if max_price is not None:
        search = search.filter(Post.price <= max_price)
    if swapObject is not None:
        search = search.filter(models.Post.swapObject == swapObject)
    if rentalPeriod is not None:
        search = search.filter(models.Post.rentalPeriod == rentalPeriod)

    return search.all()


def create_comment(db: Session, creator_id: int, email: str, user_id: int, mark: int, comment: schemas.Comments):
    if mark >= 6 or mark < 0:
        return " Ocena może być wprowadzona z zakresu o 0 do 5"
    db_comment = models.Comment(creator_id=creator_id, owner_id=user_id, mark=mark, email=email, **comment.dict())
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_user_posts(db, user_id: int):
    return db.query(models.Post).filter(models.Comment.owner_id == user_id).all()


def get_user_comment(db, user_id: int):
    return db.query(models.Comment).filter(models.Comment.owner_id == user_id).all()


def str_mark(db, user_id: int):
    average_mark = 0
    row_number = 0

    comments = db.query(models.Comment).filter(models.Comment.owner_id == user_id).all()

    for row in comments:
        average_mark = average_mark + row.mark
        row_number = row_number + 1

    if row_number <= 0:
        return 'Brak opini o użytkowniku'

    value = average_mark / row_number

    if value < 1:
        return {'int_mark': value, 'str_mark': 'Większości negatywne'}
    if value < 2:
        return {'int_mark': value, 'str_mark': 'negatywne'}
    if value < 3:
        return {'int_mark': value, 'str_mark': 'Umiarkowane'}
    if value < 4:
        return {'int_mark': value, 'str_mark': 'Pozytywne'}
    if value < 5:
        return {'int_mark': value, 'str_mark': 'Godny polecenia'}

    return 'test'


def add_new_photos(db: Session, comment_id: int, photo_url: str):
    db_photos = models.Photo(comment_id=comment_id, photo_url=photo_url)
    db.add(db_photos)
    db.commit()
    db.refresh(db_photos)
    return db_photos


def create_reset_code(db: Session, email: str, reset_code: str):
    code = models.Code(email=email, reset_code=reset_code, status=1, expired_in=datetime.now())
    db.add(code)
    db.commit()
    db.refresh(code)
    return code


def check_password(db: Session, reset_password_token: str):
    sql_query = db.query(models.Code).\
        filter(models.Code.reset_code == reset_password_token). \
        filter(models.Code.status == "1") \
        .first()

    sql_query is not None
    if not sql_query:
        raise HTTPException(status_code=404, detail="Token niepoprawny lub wygasł")

    return sql_query



def reset_password(db: Session, new_hash_pas: str, email: str):
    user = db.query(models.User).filter(models.User.email == email).first()

    user.hashed_password = new_hash_pas

    db.commit()
    db.refresh(user)
    return user


def make_code_revised(db: Session, reset_password_token: str, email: str):
    make_pass = db.query(models.Code).filter(models.Code.reset_code == reset_password_token).first()
    make_pass.status = 0

    db.commit()
    db.refresh(make_pass)

    return make_pass