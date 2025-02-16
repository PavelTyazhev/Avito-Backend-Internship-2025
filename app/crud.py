from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models, auth

MERCH_ITEMS = {
    "t-shirt": 80,
    "cup": 20,
    "book": 50,
    "pen": 10,
    "powerbank": 200,
    "hoody": 300,
    "umbrella": 200,
    "socks": 10,
    "wallet": 50,
    "pink-hoody": 500
}

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, username: str, password: str):
    hashed_password = auth.get_password_hash(password)
    user = models.User(username=username, hashed_password=hashed_password, coins=1000)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        user = create_user(db, username, password)
    if not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return user

def send_coins(db: Session, from_user: models.User, to_username: str, amount: int):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    if from_user.coins < amount:
        raise HTTPException(status_code=400, detail="Insufficient coins")
    to_user = get_user_by_username(db, to_username)
    if not to_user:
        raise HTTPException(status_code=400, detail="Recipient user does not exist")
    from_user.coins -= amount
    to_user.coins += amount
    transaction = models.CoinTransaction(from_user_id=from_user.id, to_user_id=to_user.id, amount=amount)
    db.add(transaction)
    db.commit()
    return transaction

def buy_item(db: Session, user: models.User, item: str):
    if item not in MERCH_ITEMS:
        raise HTTPException(status_code=400, detail="Invalid item")
    price = MERCH_ITEMS[item]
    if user.coins < price:
        raise HTTPException(status_code=400, detail="Insufficient coins to buy this item")
    user.coins -= price
    inventory_item = db.query(models.Inventory).filter(models.Inventory.user_id == user.id, models.Inventory.item == item).first()
    if inventory_item:
        inventory_item.quantity += 1
    else:
        inventory_item = models.Inventory(user_id=user.id, item=item, quantity=1)
        db.add(inventory_item)
    db.commit()
    return {"message": f"You have purchased {item}"}

def get_info(db: Session, user: models.User):
    inventory_records = db.query(models.Inventory).filter(models.Inventory.user_id == user.id).all()
    inventory = [{"type": record.item, "quantity": record.quantity} for record in inventory_records]
    received_tx = db.query(models.CoinTransaction).filter(models.CoinTransaction.to_user_id == user.id).all()
    sent_tx = db.query(models.CoinTransaction).filter(models.CoinTransaction.from_user_id == user.id).all()
    
    received = []
    for tx in received_tx:
        sender = db.query(models.User).filter(models.User.id == tx.from_user_id).first()
        received.append({"fromUser": sender.username if sender else "Unknown", "amount": tx.amount})
    sent = []
    for tx in sent_tx:
        receiver = db.query(models.User).filter(models.User.id == tx.to_user_id).first()
        sent.append({"toUser": receiver.username if receiver else "Unknown", "amount": tx.amount})
    return {"coins": user.coins, "inventory": inventory, "coinHistory": {"received": received, "sent": sent}}