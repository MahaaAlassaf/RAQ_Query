# from fastapi import HTTPException, Header
# from typing import Annotated
# from fastapi import HTTPException, Security, Depends
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from app.services.token_services import verify_token

# security = HTTPBearer()

# def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     token = credentials.credentials
#     user = verify_token(token)
#     if not user:
#         raise HTTPException(status_code=403, detail="Invalid token")
#     return user


