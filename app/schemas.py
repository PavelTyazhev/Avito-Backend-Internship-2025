from pydantic import BaseModel
from typing import List

class AuthRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    token: str

class SendCoinRequest(BaseModel):
    toUser: str
    amount: int

class InventoryItem(BaseModel):
    type: str
    quantity: int

class ReceivedTransaction(BaseModel):
    fromUser: str
    amount: int

class SentTransaction(BaseModel):
    toUser: str
    amount: int

class CoinHistory(BaseModel):
    received: List[ReceivedTransaction]
    sent: List[SentTransaction]

class InfoResponse(BaseModel):
    coins: int
    inventory: List[InventoryItem]
    coinHistory: CoinHistory

class PurchaseResponse(BaseModel):
    message: str