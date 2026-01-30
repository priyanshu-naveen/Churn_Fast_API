# JWT Authentication

from new import app,CustomerData,PredictionResponse,predict
from fastapi.security import HTTPBearer
from fastapi import HTTPException
from jose import jwt
import uvicorn

# configuration
SECRET_KEY='Sample_key'
ALGORITHM='HS256'
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Security Scheme
security=HTTPBearer()

# User authentication models
from pydantic import BaseModel
class UserLogin(BaseModel):
    username:str
    password:str

class UserRegister(BaseModel):
    username:str
    password:str

class TokenResponse(BaseModel):
    access_token:str
    token_type:str    # Bearer Type
    expires_in:int

class AuthenticatePredictionRequest(BaseModel):
    customer:CustomerData

fake_users_db={
    "admin":{
        'username':'totla',
        'password':'totla@',
        'disabled':False
    },
    "user1":{
        'username':'user1',
        'password':'user1pass',
        'disabled':False
    }
}

from datetime import timedelta,datetime
from typing import Optional
# JWT Access Token 
def create_access_token(data:dict,expires_delta:Optional[timedelta]=None):          
    # expires_delta -> token expiring time

    # will create copy of data to avoid mutation 
    to_encode=data.copy()

    # will check expire_delta is provided otherwise meke it default expiration time 
    if expires_delta:
        expire=datetime.utcnow() + expires_delta
    # creating default expire time
    else:
        expire=datetime.utcnow() + timedelta(minutes=15)

    # Data -> add expiration time
    to_encode.update({'exp':expire})

    # encode copy data,secret key,algorithm 
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

    # return encoded token 
    return encoded_jwt

def verify_token(token:str):
    payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    username : str=payload.get('sub')
    if username is None:
        raise HTTPException(status_code=401,detail='Invalid token')
    return username

def authenticate_user(username:str,password:str):
    user=fake_users_db.get(username)
    if not user or user['password']!=password:
        return None
    return user


# Endpoint for user register
@app.post('/register',response_model=TokenResponse)
async def register_user(user:UserRegister):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400,detail='Username already exists')
    
    # Register user
    fake_users_db[user.username]={
        'username':user.username,
        'password':user.password,
        'disabled':False
    }

    access_token_expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token=create_access_token(data={'sub':user.username},expires_delta=access_token_expires)

    return {
        'access_token': access_token,
        'token_type':'Bearer',
        'expires_in':ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

# Endpoint for user login
@app.post('/login',response_model=TokenResponse)
async def login_user(user_cred:UserLogin):
    if authenticate_user(user_cred.username,user_cred.password) is None:
        raise HTTPException(status_code=401,detail='User or password not exists')

    access_token_expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token=create_access_token(data={'sub':user_cred.username},expires_delta=access_token_expires)

    return {
        'access_token': access_token,
        'token_type':'Bearer',
        'expires_in':ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
# Prediction endpoint with JWT authentication
 #1 post endpoint
@app.post('/predict/auth',response_model=PredictionResponse,dependencies=[Depends(security)]) 
# extract the authorization header,checks the format of Bearer token

 #2 response model
async def predict_auth(request:AuthenticatePredictionRequest,credentials:HTTPAuthorizationCredentials=Depends(security)):
 #3 Verify token 
    username=verify_token(credentials.credentials)

 #4 log theauthorized access
    print(f"user{username} accessed the prediction endpoint")

 #5 call the original prediction function which is in new.py file
    return predict(request.customer)   # we are extractingg the customer data from the function
