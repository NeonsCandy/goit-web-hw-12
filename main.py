from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models, schemas, crud, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Contacts API Secure")
app.include_router(auth.router)

@app.post("/auth/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def signup(body: schemas.UserModel, db: Session = Depends(get_db)):
    exist_user = crud.get_user_by_email(db, email=body.email)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    new_user = crud.create_user(db, body)
    return new_user

@app.post("/auth/login", response_model=schemas.TokenModel)
def login(body: schemas.UserModel, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=body.email)
    if user is None or not auth.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = auth.create_access_token(data={"sub": user.email})
    refresh_token = auth.create_refresh_token(data={"sub": user.email})
    crud.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.post("/contacts/", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_contact(db=db, contact=contact, user_id=current_user.id)

@app.get("/contacts/", response_model=list[schemas.ContactResponse])
def read_contacts(name: str = Query(None), surname: str = Query(None), email: str = Query(None), skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.get_contacts(db, user_id=current_user.id, name=name, surname=surname, email=email, skip=skip, limit=limit)

@app.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def read_contact(contact_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    contact = crud.get_contact_by_id(db, contact_id=contact_id, user_id=current_user.id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def update_contact(contact_id: int, body: schemas.ContactCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    contact = crud.update_contact(db=db, contact_id=contact_id, contact=body, user_id=current_user.id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@app.delete("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def remove_contact(contact_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
 
    contact = crud.delete_contact(db=db, contact_id=contact_id, user_id=current_user.id)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
