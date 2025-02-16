import pytest
from app import crud, models, auth
from app.database import Base, engine, SessionLocal

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_create_and_authenticate_user(db):
    username = "testuser"
    password = "testpassword"
    user = crud.create_user(db, username, password)
    assert user.username == username
    authenticated_user = crud.authenticate_user(db, username, password)
    assert authenticated_user.id == user.id

def test_send_coins_insufficient_balance(db):
    user1 = crud.create_user(db, "user1", "password")
    user2 = crud.create_user(db, "user2", "password")
    user1.coins = 50
    db.commit()
    with pytest.raises(Exception):
        crud.send_coins(db, user1, "user2", 100)