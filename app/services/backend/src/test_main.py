import json
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from main import app, get_db
import repository, models, schemas, main

client = TestClient(app)

# ---- Database tests using get_db ----

# Creates
def test_create_team_db():
    db = next(get_db())
    teamTest = schemas.TeamCreate(name = "Test_T", country = "Spain")
    repository.create_team(db, teamTest)
    response = client.get("/team/Test_T")
    assert response.status_code == 200
    assert response.json().get("name") == "Test_T"
    assert response.json().get("country") == "Spain"

def test_create_competition_db():
    db = next(get_db())
    competitionTest = schemas.CompetitionCreate(name = "Test_C", category = "Senior", sport = "Volleyball")
    repository.create_competition(db, competitionTest)
    response = client.get("/competition/Test_C")
    assert response.status_code == 200
    assert response.json().get("name") == "Test_C"
    assert response.json().get("category") == "Senior"
    assert response.json().get("sport") == "Volleyball"

def test_create_match_db():
    db = next(get_db())
    local = repository.get_team_by_name(db, "Test_T")
    visitor = repository.get_team_by_name(db, "Barça")
    competition = repository.get_competition_by_name(db, "Test_C")
    matchTest = schemas.MatchCreate(date = "05/09/23 15:45:00", local = local, visitor = visitor, competition = competition, price = 60.0)
    repository.create_match(db, matchTest, local=local, visitor = visitor, competition = competition)
    response = client.get("/match/1")
    assert response.status_code == 200
    assert response.json().get("date") == "2023-05-09T15:45:00"

# Reads
def test_read_teams_db():
    db = next(get_db())
    response = client.get("/teams/")
    assert response.status_code == 200
    assert response.json()[0].get("name") == "Barça"
    assert response.json()[0].get("country") == "Spain"
    assert response.json()[1].get("name") == "Test_T"
    assert response.json()[1].get("country") == "Spain"

def test_read_competitions_db():
    db = next(get_db())
    response = client.get("/competitions/")
    assert response.status_code == 200
    assert response.json()[0].get("name") == "Test_C"
    assert response.json()[0].get("category") == "Senior"
    assert response.json()[0].get("sport") == "Volleyball"

def test_read_matches_db():
    db = next(get_db())
    response = client.get("/matches/")
    assert len(response.json()) == 1
    assert response.status_code == 200
    assert response.json()[0].get("price") == 60.0

# Deletes
def test_delete_match_db():
    db = next(get_db())
    repository.delete_match(db, repository.get_match_by_data(db, local=repository.get_team_by_name(db, "Test_T"), visitor=repository.get_team_by_name(db, "Barça"), date="05/09/23 15:45:00"))
    response = client.get("/match/1")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Match not found'}

def test_delete_competition_db():
    db = next(get_db())
    repository.delete_competition(db, repository.get_competition_by_name(db, "Test_C"))
    response = client.get("/competition/Test_C")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Competition not found'}

def test_delete_team_db():
    db = next(get_db())
    repository.delete_team(db, repository.get_team_by_name(db, "Test_T"))
    response = client.get("/team/Test_T")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Team not found'}