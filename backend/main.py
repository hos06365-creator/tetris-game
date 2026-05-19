from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from . import models, schemas
from .auth import create_access_token, get_current_user, hash_password, verify_password
from .database import Base, engine, get_db

BASE_DIR = Path(__file__).resolve().parent.parent

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini Tetris API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def auth_response(user: models.User) -> schemas.AuthResponse:
    return schemas.AuthResponse(
        access_token=create_access_token(str(user.id)),
        user=user,
    )


def get_global_high_score(db: Session) -> schemas.GlobalHighScore:
    row = (
        db.query(models.User.email, models.User.high_score)
        .filter(models.User.high_score > 0)
        .order_by(desc(models.User.high_score), models.User.created_at.asc())
        .first()
    )
    if row is None:
        return schemas.GlobalHighScore(score=0, email=None)
    return schemas.GlobalHighScore(score=row.high_score, email=row.email)


@app.post("/api/auth/register", response_model=schemas.AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    email = normalize_email(payload.email)
    existing_user = db.query(models.User).filter(func.lower(models.User.email) == email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = models.User(email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return auth_response(user)


@app.post("/api/auth/login", response_model=schemas.AuthResponse)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    email = normalize_email(payload.email)
    user = db.query(models.User).filter(func.lower(models.User.email) == email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return auth_response(user)


@app.get("/api/users/me", response_model=schemas.UserRead)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.get("/api/scores/high-score", response_model=schemas.GlobalHighScore)
def read_global_high_score(db: Session = Depends(get_db)):
    return get_global_high_score(db)


@app.get("/api/scores/me", response_model=list[schemas.ScoreRead])
def read_my_scores(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Score)
        .filter(models.Score.user_id == current_user.id)
        .order_by(models.Score.created_at.desc())
        .limit(20)
        .all()
    )


@app.post("/api/scores", response_model=schemas.ScoreSaveResponse, status_code=status.HTTP_201_CREATED)
def save_score(
    payload: schemas.ScoreCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    score = models.Score(user_id=current_user.id, score=payload.score, lines=payload.lines)
    db.add(score)
    if payload.score > current_user.high_score:
        current_user.high_score = payload.score
    db.commit()
    db.refresh(score)
    db.refresh(current_user)
    return schemas.ScoreSaveResponse(
        score=score,
        user_high_score=current_user.high_score,
        global_high_score=get_global_high_score(db),
    )


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/static/styles.css", include_in_schema=False)
def styles():
    return FileResponse(BASE_DIR / "styles.css", media_type="text/css")


@app.get("/static/script.js", include_in_schema=False)
def script():
    return FileResponse(BASE_DIR / "script.js", media_type="application/javascript")
