from sqlalchemy.orm import Session
import models, schemas, auth
from datetime import date

# --- КОРИСТУВАЧІ ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserModel):
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_token(user: models.User, token: str | None, db: Session):
    user.refresh_token = token
    db.commit()

# --- КОНТАКТИ ---
def create_contact(db: Session, contact: schemas.ContactCreate, user_id: int):
    db_contact = models.Contact(**contact.model_dump(), user_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts(db: Session, user_id: int, name: str = None, surname: str = None, email: str = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Contact).filter(models.Contact.user_id == user_id)
    if name: query = query.filter(models.Contact.first_name.ilike(f"%{name}%"))
    if surname: query = query.filter(models.Contact.last_name.ilike(f"%{surname}%"))
    if email: query = query.filter(models.Contact.email.ilike(f"%{email}%"))
    return query.offset(skip).limit(limit).all()

def get_contact_by_id(db: Session, contact_id: int, user_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id, models.Contact.user_id == user_id).first()

def update_contact(db: Session, contact_id: int, contact: schemas.ContactCreate, user_id: int):
    db_contact = get_contact_by_id(db, contact_id, user_id)
    if db_contact:
        for key, value in contact.model_dump().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int, user_id: int):
    db_contact = get_contact_by_id(db, contact_id, user_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact

def get_upcoming_birthdays(db: Session, user_id: int):
    contacts = db.query(models.Contact).filter(models.Contact.user_id == user_id).all()

def get_upcoming_birthdays(db: Session):
    contacts = db.query(models.Contact).all()
    today = date.today()
    upcoming = []
    
    for contact in contacts:
        if contact.birthday:
            try:
                bday_this_year = contact.birthday.replace(year=today.year)
            except ValueError:
                bday_this_year = contact.birthday.replace(year=today.year, month=3, day=1)
            
            if bday_this_year < today:
                try:
                    bday_this_year = contact.birthday.replace(year=today.year + 1)
                except ValueError:
                    bday_this_year = contact.birthday.replace(year=today.year + 1, month=3, day=1)

            days_until_birthday = (bday_this_year - today).days
            if 0 <= days_until_birthday <= 30:
                upcoming.append(contact)
    
    return upcoming