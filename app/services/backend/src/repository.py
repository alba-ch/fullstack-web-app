import datetime

from sqlalchemy.orm import Session
import src.models as models
import src.schemas as schemas

class DatabaseError(Exception):
    pass

# ---- Team ----
def get_team(db: Session, team_id: int):
    return db.query(models.Team).filter(models.Team.id == team_id).first()

def get_team_by_name(db: Session, name: str):
    return db.query(models.Team).filter(models.Team.name == name).first()

def get_teams(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Team).offset(skip).limit(limit).all()

def create_team(db: Session, team: schemas.TeamCreate):
    db_team = models.Team(name=team.name, country=team.country, description=team.description)
    try:
        db.add(db_team)
        db.commit()
        db.refresh(db_team)
        return db_team
    except:
        db.rollback()
        raise DatabaseError("Error while creating team")

def update_team(db: Session, team : schemas.Team, new_team : schemas.TeamCreate):
    # Agafem de la base de dades l'equip que volem modificar
    #team =  db.execute(select(models.Team).where(models.Team.name == name).first())
    # Modifiquem les dades que hagin canviat
    if new_team.name:
        team.name = new_team.name
    if new_team.country:
        team.country = new_team.country
    if new_team.description:
        team.description = new_team.description
    # Actualitzem la base de dades
    try:
        db.commit()
        return team
    except:
        db.rollback()
        raise DatabaseError("Error while updating team")

def delete_team(db : Session, team: schemas.Team):
    try:
        # Esborrem l'equip
        db.delete(team)
        db.commit()
    except:
        db.rollback()
        raise DatabaseError("Error while deleting team")

# ---- Competition ----
def get_competition(db: Session, competition_id: int):
    #return db.execute(select(models.Competition).where(models.Competition.id == competition_id)).first()
     return db.query(models.Competition).filter(models.Competition.id == competition_id).first()

def get_competition_by_name(db: Session, name: str):
    #return db.execute(select(models.Competition).where(models.Competition.name == name)).first()
    return db.query(models.Competition).filter(models.Competition.name == name).first()

def get_competitions_by_team(db : Session, team : schemas.Team):
    return db.query(models.Competition).filter(team in models.Competition.teams).all()

def get_competitions(db: Session, skip: int = 0, limit: int = 100):
    #return db.execute(select(models.Competition).offset(skip).limit(limit)).all()
    return db.query(models.Competition).offset(skip).limit(limit).all()

def create_competition(db: Session, competition: schemas.CompetitionCreate):
    db_competition = models.Competition(name=competition.name, sport=competition.sport, category=competition.category)
    # Considerem que al crear una competició, no tenim cap llistat d'equips dins d'aquesta
    # Per afegir-los, ho farem en un altre métode. En aquest cas, s'actualitzarà la taula que relaciona Competitions amb Teams
    try:
        db.add(db_competition)
        db.commit()
        db.refresh(db_competition)
        return db_competition
    except:
        db.rollback()
        raise DatabaseError("Error while creating competition")
    
def delete_competitions(db : Session):
    # Esborrem totes les competicions
    try:
        db.query(models.Competition).delete()
        db.commit()
    except:
        db.rollback()
        raise DatabaseError("Error while deleting competitions")

def update_competition(db: Session, competition : schemas.Competition, new_competition : schemas.CompetitionCreate):
    # Agafem de la base de dades l'equip que volem modificar
    #team =  db.execute(select(models.Team).where(models.Team.name == name).first())
    # Modifiquem les dades que hagin canviat
    if new_competition.name:
        competition.name = new_competition.name
    if new_competition.category:
        competition.category = new_competition.category
    if new_competition.sport:
        competition.sport = new_competition.sport
    try:
        db.commit()
        return competition
    except:
        db.rollback()
        raise DatabaseError("Error while updating competition")

def delete_competition(db : Session, competition: schemas.Competition):
    # Esborrem l'equip
    try:
        db.delete(competition)
        db.commit()
    except:
        db.rollback()
        raise DatabaseError("Error while deleting competition")

def add_teams_competition(db : Session, competition : schemas.Competition, teams : list[schemas.Team]):
    try:
        competition.teams.append(teams)
        db.commit()
        return competition
    except:
        db.rollback()
        raise DatabaseError("Error while adding teams to competition")

# ---- Match ----
def get_match(db: Session, match_id: int):
    #return db.select(models.Match).where(models.Match.id == match_id).first()
    return db.query(models.Match).filter(models.Match.id == match_id).first()

# This function allows you to check if a match already exists in the DB
def get_match_by_data(db : Session, local : schemas.Team, visitor : schemas.Team, date : str):
    return db.query(models.Match).filter(models.Match.date == datetime.datetime.strptime(date, '%m/%d/%y %H:%M:%S')).filter(
        models.Match.visitor_id == visitor.id).filter(models.Match.local_id == local.id).first()

# Returns all the matches in a giving competition
def get_match_by_competition(db : Session, competition : schemas.Competition):
    return db.query(models.Match).filter(models.Match.competition_id == competition.id).all()

# Returns all the matches with a giving team
def get_match_by_team(db : Session, team : schemas.Team):
    local = db.query(models.Match).filter(models.Match.local_id == team.id).all()
    visitor = db.query(models.Match).filter(models.Match.visitor_id == team.id).all()
    return local+visitor

def get_matches(db: Session, skip: int = 0, limit: int = 100):
    #return db.select(models.Match).offset(skip).limit(limit).all()
    return db.query(models.Match).offset(skip).limit(limit).all()

def create_match(db: Session, match: schemas.MatchCreate, local : schemas.Team, visitor : schemas.Team, competition : schemas.Competition):
    db_match = models.Match(date=datetime.datetime.strptime(match.date, '%m/%d/%y %H:%M:%S'), price=match.price, total_available_tickets = match.total_available_tickets, local= local, visitor = visitor, competition = competition)
    try:
        db.add(db_match)
        db.commit()
        db.refresh(db_match)
        return db_match
    except:
        db.rollback()
        raise DatabaseError("Error while creating match")

def update_match(db: Session, match : schemas.Match, new_match : schemas.MatchCreate, local : schemas.Team, visitor : schemas.Team, competition : schemas.Competition):
    # Agafem de la base de dades l'equip que volem modificar
    #team =  db.execute(select(models.Team).where(models.Team.name == name).first())
    # Modifiquem les dades que hagin canviat
    if new_match.date:
        match.date = datetime.datetime.strptime(new_match.date, '%m/%d/%y %H:%M:%S')
    if new_match.price:
        match.price = new_match.price
    if new_match.total_available_tickets:
        match.total_available_tickets = new_match.total_available_tickets
    if new_match.local:
        match.local = local
    if new_match.visitor:
        match.visitor = visitor
    if new_match.competition:
        match.competition = competition
    try:
        db.commit()
        return match
    except:
        db.rollback()
        raise DatabaseError("Error while updating match")

def delete_match(db : Session, match: schemas.Match):
    # Esborrem el partit
    try:
        db.delete(match)
        db.commit()
    except:
        db.rollback()
        raise DatabaseError("Error while deleting match")

# ---- Account ----
def create_account(db: Session, account: schemas.AccountCreate):
    db_account = models.Account(username=account.username, available_money=account.available_money, is_admin=account.is_admin)
    db_account.password = account.password
    try:
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return db_account
    except:
        db.rollback()
        raise DatabaseError("Error while creating account")

def create_account(db: Session, account: schemas.AccountCreate):
    db_account = models.Account(username=account.username)
    db_account.password = account.password
    try:
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return db_account
    except:
        db.rollback()
        raise DatabaseError("Error while creating account")

def get_account(db: Session, account_id: int):
    #return db.select(models.Account).where(models.Account.id == account_id).first()
    return db.query(models.Account).filter(models.Account.id == account_id).first()

def get_account_by_username(db: Session, username: str):
    #return db.execute(select(models.Account).where(models.Account.username == username)).first()
    return db.query(models.Account).filter(models.Account.username == username).first()

def get_accounts(db: Session, skip: int = 0, limit: int = 100):
    #return db.select(models.Account).offset(skip).limit(limit).all()
    return db.query(models.Account).offset(skip).limit(limit).all()

def update_account(db: Session, account : schemas.Account, new_account : schemas.Account):
    # Agafem de la base de dades l'equip que volem modificar
    #team =  db.execute(select(models.Team).where(models.Team.name == name).first())
    # Modifiquem les dades que hagin canviat
    if new_account.username:
        account.username = new_account.username
    # if new_account.password:
    #     account.password = new_account.password
    if new_account.available_money:
        account.available_money = new_account.available_money
    if new_account.is_admin:
        account.is_admin = new_account.is_admin
    if new_account.orders:
        account.orders = new_account.orders
    try:
        db.commit()
        return account
    except:
        db.rollback()
        raise DatabaseError("Error while updating account")

def delete_account(db : Session, account: schemas.Account):
    # Esborrem l'usuari
    try:
        db.delete(account)
        db.commit()
    except:
        db.rollback()
        raise DatabaseError("Error while deleting account")

# ---- Orders ----
def create_order(db: Session, order: schemas.OrderCreate, account : schemas.Account):
    try:
        # Iniciem la transacció
       # with db.begin():
        match = get_match(db, order.match_id)

        # Comprovem que el usuari tingui prou diners
        if account.available_money < order.tickets_bought * match.price:
            raise DatabaseError("Not enough money")
        # Comprovem que hi hagi prou entrades
        if match.total_available_tickets < order.tickets_bought:
            raise DatabaseError("Not enough tickets")
        
        # Actualitzem els diners disponibles
        account.available_money = account.available_money - order.tickets_bought * match.price
        # Actualitzem les entrades disponibles
        match.total_available_tickets = match.total_available_tickets - order.tickets_bought
        # Creem la comanda
        db_order = models.Order(match_id = match.id, tickets_bought = order.tickets_bought)
        db_order.username = account.username
        # Afegim la comanda a la relació de comandes de l'usuari
        account.orders.append(db_order)

        # Desem els canvis
        db.add(db_order)
        db.add(account)
        db.add(match)

        db.commit()
        db.refresh(db_order)
        
        return db_order
    except:
        db.rollback()
        raise DatabaseError("Error while creating order")

def get_orders_by_username(db : Session, username : str):
    return db.query(models.Order).filter(models.Order.username == username).all()

def delete_orders_by_username(db : Session, username : str):
    try:
        db.query(models.Order).filter(models.Order.username == username).delete()
        db.commit()
    except:
        db.rollback()
        raise DatabaseError("Error while deleting orders from user")

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    #return db.select(models.Order).offset(skip).limit(limit).all()
    return db.query(models.Order).offset(skip).limit(limit).all()

def delete_order(db : Session, order: schemas.Order):
    # Esborrem la comanda
    try:
        db.delete(order)
        db.commit()
    except:
        db.rollback()
        raise DatabaseError("Error while deleting order")
