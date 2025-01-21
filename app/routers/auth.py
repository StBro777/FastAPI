import select
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def authenticate_user(email: str, password: str, db: AsyncSession):
    """Аутентифицирует пользователя."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user or not verify_password(password, user.password):
        return None
    return user

@router.post("/auth/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Маршрут для входа и получения JWT-токена."""
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Маршрут для регистрации нового пользователя.
    """
    # Проверяем, существует ли пользователь с таким email
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Хешируем пароль и создаем нового пользователя
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, password=hashed_password)

    # Сохраняем пользователя в базе данных
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Возвращаем данные пользователя (без пароля)
    return db_user