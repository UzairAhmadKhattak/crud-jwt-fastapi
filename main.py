
from fastapi import FastAPI,Depends
from database import Base,engine,SessionLocal
from sqlalchemy.orm import Session,joinedload
from fastapi import status
from auth import router,get_current_user
from fastapi.exceptions import HTTPException
from schemas import ItemSchema,ItemUpdateSchema,ItemInsertSchema
from models import Item,User
from typing import List

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/",tags=["Home"])
def home(user:dict = Depends(get_current_user),status_code = status.HTTP_200_OK):
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail="couldnt validate user.")
    return user

@app.get("/get_items",response_model=List[ItemSchema],tags=["Items"])
def get_items(db:Session=Depends(get_db)):
    return db.query(Item).options(joinedload(Item.owner)).all()

@app.post("/insert_item",tags=["Items"])
def create_item(item:ItemInsertSchema,db:Session=Depends(get_db)):
    item = Item(**item.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"msg":f"item:{item.title} created"}

@app.get("/item/{pk}",tags=["Items"],response_model=ItemSchema)
def get_item(pk:int,db:Session=Depends(get_db)):
    item = db.query(Item).filter(Item.id == pk).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.delete("/item/{pk}", tags=["Items"])
def delete_item(pk: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == pk).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"msg": f"Item with id {pk} has been deleted"}


@app.put("/item/{pk}", tags=["Items"])
def update_item(pk: int, item_update: ItemUpdateSchema, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == pk).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update the item fields
    if item_update.title is not None:
        item.title = item_update.title
    if item_update.description is not None:
        item.description = item_update.description
    if item_update.owner_id is not None:
        item.owner_id = item_update.owner_id

    db.commit()
    db.refresh(item)
    return item