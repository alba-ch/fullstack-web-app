#import Annotate as Annotate
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
import src.utils
from src.utils import verify_password, create_access_token, create_refresh_token, get_hashed_password
from src.dependencies import get_current_user

import src.repository as repository
import src.models as models
import src.schemas as schemas
from src.database import SessionLocal, engine

from typing_extensions import Annotated



models.Base.metadata.create_all(bind=engine) # Creem la base de dades amb els models que hem definit a SQLAlchemy

app = FastAPI()

# Permetre acces a solicituds de tots els orígens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Indiquem els camins a consumir
#app.mount("/static", StaticFiles(directory="./dist/static"), name="static")

# Declarem ruta per renderitzar la plantilla
templates = Jinja2Templates(directory="./dist")
@app.get("/")
async def serve_index(request: Request):
    if src.utils.is_production(): return "production"
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/userlogin")
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- TEAMS ----
@app.get("/teams/", response_model=list[schemas.Team])
def read_teams(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)): # NOT PROTECTED
    return repository.get_teams(db, skip=skip, limit=limit)

@app.post("/teams/", response_model=schemas.Team)
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    db_team = repository.get_team_by_name(db, name=team.name)
    if db_team:
        raise HTTPException(status_code=400, detail="Team already Exists, Use put for updating")
    else:
        return repository.create_team(db=db, team=team)

@app.get("/team/{team_name}", response_model=schemas.Team)
def read_team(team_name: str,db: Session = Depends(get_db)): # NOT PROTECTED
    team = repository.get_team_by_name(db, name=team_name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@app.put("/team/{team_name}", response_model=schemas.Team)
def update_team(team_name: str, team_new_data: schemas.TeamCreate, db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    # Check if the team is already in the DB
    db_team = repository.get_team_by_name(db, name=team_name)
    # If the team doesn't exit, create a new one
    if not db_team:
        return repository.create_team(db, team=team_new_data)
    # Else we update the data
    else:
        # Update values from the new data that are not None.
        return repository.update_team(db, team=db_team, new_team=team_new_data)

@app.delete("/team/{team_name}", )
def delete_team(team_name : str, db :Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    # Check if team is already in the DB
    db_team = repository.get_team_by_name(db, name=team_name)
    # If team is not in the DB, we send back an error message
    if not db_team:
        raise HTTPException(status_code=404, detail="Team doesn't exist")
    # Else remove it
    # Remove all the matches where that team plays
    for match in repository.get_match_by_team(db, team=db_team):
        repository.delete_match(db, match=match)
    repository.delete_team(db, team=db_team)
    raise HTTPException(status_code=200, detail="Team deleted properly")

# Retorna tots els partits d'un equip, donat el seu nom.
@app.get("/teams/{team_name}/matches", response_model=list[schemas.Match])
def read_matches_by_team(team_name: str,db: Session = Depends(get_db)): # NOT PROTECTED
    # Check if team is already in the DB
    db_team = repository.get_team_by_name(db, name=team_name)
    # If team is not in the DB, we send back an error message
    if not db_team:
        raise HTTPException(status_code=404, detail="Team doesn't exist")
    return repository.get_match_by_team(db, team=db_team)

# Retorna totes les competicions d'un equip, donat el seu nom.
@app.get("/teams/{team_name}/competitions", response_model=list[schemas.Competition])
def read_matches_by_team(team_name: str,db: Session = Depends(get_db)) : # NOT PROTECTED
    # Check if team is already in the DB
    db_team = repository.get_team_by_name(db, name=team_name)
    # If team is not in the DB, we send back an error message
    if not db_team:
        raise HTTPException(status_code=404, detail="Team doesn't exist")
    return repository.get_competitions_by_team(db, team=db_team)

# ---- COMPETITIONS ----
@app.get("/competitions/", response_model=list[schemas.Competition])
def read_competitions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)): # NOT PROTECTED
    return repository.get_competitions(db, skip=skip, limit=limit)

@app.post("/competitions/", response_model=schemas.Competition)
def create_competition(competition: schemas.CompetitionCreate, db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    db_competition = repository.get_competition_by_name(db, name=competition.name)
    if db_competition:
        raise HTTPException(status_code=400, detail="Competition already Exists, Use put for updating")
    else:
        return repository.create_competition(db=db, competition=competition)

@app.get("/competition/{competition_name}", response_model=schemas.Competition)
def read_competition(competition_name: str,db: Session = Depends(get_db)): # NOT PROTECTED
    competition = repository.get_competition_by_name(db, name=competition_name)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    return competition

@app.put("/competition/{competition_name}", response_model=schemas.Competition)
def update_competition(competition_name: str, competition_new_data: schemas.CompetitionCreate, db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    # Check if the competition is already in the DB
    db_competition = repository.get_competition_by_name(db, name=competition_name)
    # If the competition doesn't exit, create a new one
    if not db_competition:
        return repository.create_competition(db, competition=competition_new_data)
    # Else we update the data
    else:
        # Update values from the new data that are not None.
        return repository.update_competition(db, competition=db_competition, new_competition=competition_new_data)

@app.delete("/competition/{competition_name}", )
def delete_competition(competition_name : str, db :Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    # Check if competition is already in the DB
    db_competition = repository.get_competition_by_name(db, name=competition_name)
    # If competition is not in the DB, we send back an error message
    if not db_competition:
        raise HTTPException(status_code=404, detail="Competition doesn't exist")
    # Else remove it
    # Remove all matches in that competition
    for match in repository.get_match_by_competition(db, competition=db_competition):
        repository.delete_match(db, match=match)
    repository.delete_competition(db, competition=db_competition)
    raise HTTPException(status_code=200, detail="Competition deleted properly")

@app.delete("/competitions/", )
def delete_competitions(db :Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    # Remove all competitions from the DB
    return repository.delete_competitions(db)


# Retorna tots els partits d'una competició, donada el seu nom.
@app.get("/competitions/{competition_name}/matches", response_model=list[schemas.Match])
def read_matches_by_competition(competition_name: str,db: Session = Depends(get_db)) : # NOT PROTECTED
    # Check if team is already in the DB
    db_competition = repository.get_competition_by_name(db, name=competition_name)
    # If team is not in the DB, we send back an error message
    if not db_competition:
        raise HTTPException(status_code=404, detail="Competition doesn't exist")
    return repository.get_match_by_competition(db, competition=db_competition)

# Retorna tots els equips d'una competició, donada el seu nom.
@app.get("/competitions/{competition_name}/teams", response_model=list[schemas.Team])
def read_teams_by_competition(competition_name: str,db: Session = Depends(get_db)) : # NOT PROTECTED
    # Check if team is already in the DB
    db_competition = repository.get_competition_by_name(db, name=competition_name)
    # If team is not in the DB, we send back an error message
    if not db_competition:
        raise HTTPException(status_code=404, detail="Competition doesn't exist")
    return db_competition.teams

# Afegir equips a una competicio donada
@app.put("/competitions/{competition_name}/teams", response_model=schemas.Competition)
def add_teams_by_competition(competition_name: str, teams : list[schemas.Team], db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    # Check if team is already in the DB
    db_competition = repository.get_competition_by_name(db, name=competition_name)
    # If team is not in the DB, we send back an error message
    if not db_competition:
        raise HTTPException(status_code=404, detail="Competition doesn't exist")
    return repository.add_teams_competition(db, competition=db_competition, teams=teams)

# ---- MATCHES ----
@app.get("/matches/", response_model=list[schemas.Match])
def read_matches(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)): # NOT PROTECTED
    return repository.get_matches(db, skip=skip, limit=limit)

@app.post("/matches/", response_model=schemas.Match)
def create_match(match: schemas.MatchCreate, db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    # First we check if this match already exists
    db_match = repository.get_match_by_data(db, local=match.local, visitor=match.visitor, date=match.date)
    # Is so, we send an error message
    if db_match:
        raise HTTPException(status_code=400, detail="This Match already Exists, Use put for updating")
    # Otherwise we add the new match to the DB
    else:
        # Check if  local, visitor and competition exist, if not, we add them to the DB
        local = repository.get_team_by_name(db, name = match.local.name)
        if not local:
            repository.create_team(db, team = match.local)
        visitor = repository.get_team_by_name(db, name = match.visitor.name)
        if not visitor:
            repository.create_team(db, team = match.visitor)
        competition = repository.get_competition_by_name(db, name = match.competition.name)
        if not competition:
            repository.create_competition(db, competition = match.competition)
        return repository.create_match(db=db, match=match, local=local, visitor = visitor, competition = competition)

@app.get("/match/{match_id}", response_model=schemas.Match)
def read_match(match_id: str,db: Session = Depends(get_db)): # NOT PROTECTED
    match = repository.get_match(db, match_id=match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@app.put("/match/{match_id}", response_model=schemas.Match)
def update_match(match_id: int, match_new_data: schemas.MatchCreate, db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    # Check if the match is already in the DB
    db_match = repository.get_match(db, match_id=match_id)
    # Check if  local, visitor and competition exist, if not, we add them to the DB
    local = repository.get_team_by_name(db, name=match_new_data.local.name)
    if not local:
        repository.create_team(db, team=match_new_data.local)
    visitor = repository.get_team_by_name(db, name=match_new_data.visitor.name)
    if not visitor:
        repository.create_team(db, team=match_new_data.visitor)
    competition = repository.get_competition_by_name(db, name=match_new_data.competition.name)
    if not competition:
        repository.create_competition(db, competition=match_new_data.competition)
    # If the match doesn't exit, create a new one
    if not db_match:
        return repository.create_match(db=db, match=match_new_data, local=local, visitor = visitor, competition = competition)
    # Else we update the data
    else:
        # Update values from the new data that are not None.
        return repository.update_match(db, match=db_match, new_match=match_new_data, local=local, visitor = visitor, competition = competition)

@app.delete("/match/{match_id}", )
def delete_match(match_id: int, db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    # Check if match is already in the DB
    db_match = repository.get_match(db, match_id=match_id)
    # If match is not in the DB, we send back an error message
    if not db_match:
        raise HTTPException(status_code=404, detail="Match doesn't exist")
    # Else we remove it
    repository.delete_match(db, match=db_match)
    raise HTTPException(status_code=200, detail="Match deleted properly")

@app.get("/matches/{match_id}/teams", response_model=list[schemas.Team])
def read_teams_by_match(match_id: int,db: Session = Depends(get_db)) : # NOT PROTECTED
    # Check if team is already in the DB
    db_match = repository.get_match(db, match_id=match_id)
    # If team is not in the DB, we send back an error message
    if not db_match:
        raise HTTPException(status_code=404, detail="Competition doesn't exist")
    return [db_match.local,db_match.visitor]

@app.get("/matches/{match_id}/teams", response_model=schemas.Competition)
def read_competition_by_match(match_id: int,db: Session = Depends(get_db)) : # NOT PROTECTED
    # Check if team is already in the DB
    db_match = repository.get_match(db, match_id=match_id)
    # If team is not in the DB, we send back an error message
    if not db_match:
        raise HTTPException(status_code=404, detail="Competition doesn't exist")
    return db_match.competition

# ---- ACCOUNT ----
#creeu un compte nou passant `username` i `password' Utilitzeu `hash_ password` quan creeu un compte (primer heu de crear un usuari nou i després afegir una contrasenya hash mitjançant el mètode `.hash_ password (password)`).
@app.post('/account', summary="Create new user", response_model=schemas.Account)
def create_user(data: schemas.AccountCreate, db: Session = Depends(get_db)):
    # querying database to check if username already exist
    db_account = repository.get_account_by_username(db, username=data.username)
    # if user exist, raise an exception
    if db_account:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Encriptem la contrasenya
    data.password = get_hashed_password(data.password)

    user = repository.create_account(db=db, account=data)
    return user

@app.get('/account', summary='Get details of currently logged in user', response_model=schemas.Account)
async def get_me(user: schemas.Account = Depends(get_current_user)):
    return user

# TODO: Preguntar si debemos cambiar los endpoints a async
@app.get('/accounts') #obtenir informació sobre tots els comptes
def read_accounts(user: schemas.Account = Depends(get_current_user), skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if not user.is_admin:
        raise HTTPException(status_code=400, detail="Unauthorized user")
    accounts = repository.get_accounts(db, skip=skip, limit=limit)
    return accounts

@app.get('/account/{username}', response_model=schemas.Account) #obtenir informació del compte amb un nom d'usuari
def read_account(username: str, db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin and user.username != username:
        raise HTTPException(status_code=400, detail="Unauthorized user")
    account = repository.get_account_by_username(db, username=username)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@app.delete('/account/{username}') #suprimiu un compte relacionat amb un nom d'usuari (recordeu també suprimir totes les comandes relacionades).
def delete_account(username: str, db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin and user.username != username:
        raise HTTPException(status_code=400, detail="Unauthorized user")
    # Check if account is already in the DB
    db_account = repository.get_account_by_username(db, username=username)
    # If account is not in the DB, we send back an error message
    if not db_account:
        raise HTTPException(status_code=404, detail="Account doesn't exist")
    # Check if there are orders
    if db_account.orders:
        # If there are orders, we delete them
        for order in db_account.orders:
            repository.delete_order(db, order=order)
    # Finally we delete the account
    repository.delete_account(db, account=db_account)
    raise HTTPException(status_code=200, detail="Account deleted ")

@app.put('/account/{username}') #actualitzeu la informació del compte amb un nom d'usuari
def update_account(username: str, new_data: schemas.Account, db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin and user.username != username:
        raise HTTPException(status_code=400, detail="Unauthorized user")
    # Check if account is already in the DB
    db_account = repository.get_account_by_username(db, username=username)
    # If account is not in the DB, we send back an error message
    if not db_account:
        raise HTTPException(status_code=404, detail="Account doesn't exist")
    
    # If there are orders, we delete them
    if db_account.orders:
        repository.delete_orders_by_username(db, username=username)

    # Check if there are new orders
    if new_data.orders:
        # If there are new orders, we add them
        for order in new_data.orders:
            repository.create_order(db=db, order=order)

    # Finally we update the account
    return repository.update_account(db, account=db_account, new_account=new_data)

# ---- ORDERS ----
@app.get('/orders', response_model=list[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=400, detail="Unauthorized user")
    orders = repository.get_orders(db, skip=skip, limit=limit)
    return orders

@app.get('/orders/{username}', response_model=list[schemas.Order])
def read_orders(username: str, db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin and user.username != username:
        raise HTTPException(status_code=400, detail="Unauthorized user")
    # Check if order is already in the DB
    db_order = repository.get_orders_by_username(db, username=username)
    # If the user doesn't have any order, we return an empty list
    if not db_order:
        return []
    return db_order

@app.post('/order/{username}', response_model=schemas.Order)
async def create_order(order: schemas.OrderCreate, username: str, db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin and user.username != username:
        raise HTTPException(status_code=400, detail="Unauthorized user")
    # First we check if user exists
    db_user = repository.get_account_by_username(db, username=username)
    # Is so, we send an error message
    if not db_user:
        raise HTTPException(status_code=400, detail="User doesn't exist")
    # Otherwise we add the new order to the DB
    order = repository.create_order(db=db, order=order, account=db_user)
    if order == -1:
        raise HTTPException(status_code=400, detail="Not enough money")
    elif order == -2:
        raise HTTPException(status_code=400, detail="Not enough tickets available")
    return order


@app.get('/orders', response_model=list[schemas.Order])
def read_all_orders(db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=400, detail="Unauthorized user")
    # Check if there are orders in the DB
    db_order = repository.get_all_orders(db)
    # If order is not in the DB, we send back an error message
    if not db_order:
        raise HTTPException(status_code=404, detail="Order doesn't exist")
    return db_order

# ---- Token ----
@app.post('/login', summary="Create access and refresh tokens for user", response_model=schemas.TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm=Depends(), db: Session = Depends(get_db)): 
    username = form_data.username
    password = form_data.password
    # get user from database
    user = repository.get_account_by_username(db, username=username)
    # if user does not exist, raise an exception
    if not user:
        raise HTTPException(status_code=404, detail="User doesnt exist")
    # if user exist, verify password using verify_password function
    elif not verify_password(password, user.password):
        print(password)
        print(not verify_password(password, user.password))
        # if password is not correct, raise an exception
        raise HTTPException(status_code=400, detail="Incorrect password")
    # if password is correct, create access and refresh tokens and return them
    else:
        access = create_access_token(username)
        refresh = create_refresh_token(username)
        print(access)
        print("....")
        print(refresh)
        return {
            "access_token": access,
            "refresh_token": refresh
        }




# NEW: El mateix pero en comptes de nom, per id
# @app.get("/competition/{competition_id}", response_model=schemas.Competition)
# def read_competition(competition_id: int,db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
#     competition = repository.get_competition(db, id=competition_id)
#     if not competition:
#         raise HTTPException(status_code=404, detail="Competition not found")
#     return competition

# @app.put("/competition/{competition_id}", response_model=schemas.Competition)
# def update_competition(competition_id: int, competition_new_data: schemas.CompetitionCreate, db: Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
#     # Check if the competition is already in the DB
#     db_competition =repository.get_competition(db,id=competition_id)
#     # If the competition doesn't exit, create a new one
#     if not db_competition:
#         return repository.create_competition(db, competition=competition_new_data)
#     # Else we update the data
#     else:
#         # Update values from the new data that are not None.
#         return repository.update_competition(db , competition=db_competition, new_competition=competition_new_data)

# @app.delete("/competition/{competition_id}", )
# def delete_competition(competition_id : int, db :Session = Depends(get_db), user: schemas.Account = Depends(get_current_user)):
#     # Check if competition is already in the DB
#     db_competition =repository.get_competition(db,id=competition_id)
#     # If competition is not in the DB, we send back an error message
#     if not db_competition:
#         raise HTTPException(status_code=404, detail="Competition doesn't exist")
#     # Else remove it
#     # Remove all matches in that competition
#     for match in repository.get_match_by_competition(db, competition=db_competition):
#         repository.delete_match(db,match=match)
#     repository.delete_competition(db, competition=db_competition)
#     raise HTTPException(status_code=200, detail="Competition deleted properly")
