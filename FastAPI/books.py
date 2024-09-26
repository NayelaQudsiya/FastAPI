from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from uuid import UUID
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()


class Book(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=101)

@app.get("/")
def read_api(db: Session = Depends(get_db)):
    print("GET request received")
    return db.query(models.Books).all()


@app.post("/")
def create_book(book: Book, db: Session = Depends(get_db)):
    try:
        book_model = models.Books(
            title=book.title,
            author=book.author,
            description=book.description,
            rating=book.rating
        )
        db.add(book_model)
        db.commit()
        return book
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

@app.put("/{book_id}")
def update_book(book_id: UUID, book: Book, db: Session = Depends(get_db)):
    book_model = db.query(models.Books).filter(models.Books.id == str(book_id)).first()
    if book_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {book_id} does not exist"
        )

    book_model.title = book.title
    book_model.author = book.author
    book_model.description = book.description
    book_model.rating = book.rating

    db.commit()
    return book_model

@app.delete("/{book_id}")
def delete_book(book_id: UUID, db: Session = Depends(get_db)):
    book_model = db.query(models.Books).filter(models.Books.id == str(book_id)).first()
    if book_model is None:
       raise HTTPException(
           status_code=404,
           detail=f"ID {book_id} does not exist"
       )

    db.delete(book_model)
    db.commit()
    return {"message": f"ID: {book_id} deleted"}