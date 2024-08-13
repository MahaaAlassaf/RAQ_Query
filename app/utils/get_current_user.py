# # app/api/get_current_user.py
# from fastapi import HTTPException, Security
# from fastapi.security import OAuth2PasswordBearer
# from app.services.token_services import TokenService

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# class BaseAPIHandler:
#     @staticmethod
#     def get_current_user(token: str = Security(oauth2_scheme), required_role: str = None):
#         payload = TokenService.verify_token(token)
#         if required_role and payload.get("role") != required_role:
#             raise HTTPException(status_code=403, detail="Insufficient privileges")
#         return payload
