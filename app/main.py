from fastapi import FastAPI, Depends
from datetime import timedelta
from . import models, schemas, auth, crud
from .database import engine, Base, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Avito shop", version="1.0.0")

@app.post("/api/auth", response_model=schemas.AuthResponse)
def auth_endpoint(auth_req: schemas.AuthRequest, db=Depends(get_db)):
    user = crud.authenticate_user(db, auth_req.username, auth_req.password)
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"token": access_token}

@app.get("/api/info", response_model=schemas.InfoResponse)
def info_endpoint(current_user=Depends(auth.get_current_user), db=Depends(get_db)):
    info = crud.get_info(db, current_user)
    return info

@app.post("/api/sendCoin")
def send_coin_endpoint(request: schemas.SendCoinRequest, current_user=Depends(auth.get_current_user), db=Depends(get_db)):
    crud.send_coins(db, current_user, request.toUser, request.amount)
    return {"message": "Coins sent successfully"}

@app.get("/api/buy/{item}", response_model=schemas.PurchaseResponse)
def buy_item_endpoint(item: str, current_user=Depends(auth.get_current_user), db=Depends(get_db)):
    result = crud.buy_item(db, current_user, item)
    return result