from sqlalchemy import select, update
from app.database.connector import connect_to_db
from app.database.schemas.books import Book
from app.database.schemas.user import User
from app.utils.hash import deterministic_hash
from sqlalchemy.orm import Session

def retrieve_single_user(email: str, db: Session):
    try:
        stmt = select(User.email, User.fname, User.lname, User.role).where(User.email == email)
        result = db.execute(stmt).fetchone()
        if result:
            user = {
                "email": result[0],
                "fname": result[1],
                "lname": result[2],
                "role": result[3]
            }
            return True, "User retrieved successfully", user
        else:
            return False, "User not found", None
    except Exception as e:
        return False, str(e), None


# authenticate_user
def authenticate_user(email: str, password: str, db: Session):
    try:
        stmt = select(User.hashed_pw, User.role).where(User.email == email)
        result = db.execute(stmt)
        output = result.fetchone()

        if output is None:
            return False, "User not registered", None
        else:
            if output[0] == deterministic_hash(password):
                return True, "Login successful", {"email": email, "role": output[1]}
            else:
                return False, "Wrong password", None
    except Exception as e:
        print(f"Authentication error: {e}")
        return False, str(e), None



def edit_user_info(email, user_update):
    success, message, user = retrieve_single_user(email)
    if not success:
        return success, message
    
    updated_user_data = {
        "fname": user_update.fname if user_update.fname is not None else user['fname'],
        "lname": user_update.lname if user_update.lname is not None else user['lname'],
        "password": deterministic_hash(user_update.password) if user_update.password is not None else user['password'],
        "role": user['role']
    }

    stmt = (
        update(User)
        .where(User.email == email)
        .values(
                fname=updated_user_data["fname"], 
                lname=updated_user_data["lname"], 
                hashed_pw=updated_user_data["password"], 
                role=updated_user_data["role"])
        .execution_options(synchronize_session="fetch")
    )
 
    try:
        engine, session = connect_to_db()
        with engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()
        return True, "User updated successfully"
    except Exception as e:
        print(e)
        return False, e
    finally:
        session.close()

def register_user(user_data):
    try:
        engine, SessionLocal = connect_to_db()  # Ensure you are getting a session factory
        session: Session = SessionLocal()  # Create a session instance

        select_user_email = select(User.email).where(User.email == user_data.email)
        with engine.connect() as conn:
            results = conn.execute(select_user_email)
            output = results.fetchone()
            if output is not None:
                return False, "User already registered"

        hashed_pw = deterministic_hash(user_data.password)  # Correct attribute
        new_user = User(
            email=user_data.email,
            fname=user_data.fname,
            lname=user_data.lname,
            hashed_pw=hashed_pw,
            role=user_data.role
        )
        session.add(new_user)
        session.commit()
        return True, "User registered successfully"
    except Exception as e:
        print(f"Registration error: {e}")  # Log error details
        return False, f"Registration error: {e}"
    finally:
        session.close()  # Close the session instance


def delete_user(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False, "User not found"
    
    db.delete(user)
    db.commit()
    return True, "User deleted successfully"

def retrieve_all_users(db: Session):
    users = db.query(User).all()
    return [{"email": user.email, "fname": user.fname, "lname": user.lname, "role": user.role} for user in users]