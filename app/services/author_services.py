from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from app.database.connector import connect_to_db
from app.database.schemas.author import Author
from app.schemas.author import Author as pydantic_author
from app.schemas.author import AuthorUpdateCurrent

# Function to find or create an author
def find_or_create_author(author_name: str):
    engine, SessionLocal = connect_to_db()  # Assuming connect_to_db returns engine and sessionmaker
    session = SessionLocal()

    try:
        # Check if the author already exists
        author = session.query(Author).filter(Author.name == author_name).first()
        if author:
            return author.author_id, False  # Return the existing author's ID and False indicating it was not newly created

        # If the author does not exist, create a new author
        new_author = Author(name=author_name)
        session.add(new_author)
        session.commit()
        session.refresh(new_author)
        return new_author.author_id, True  # Return the new author's ID and True indicating it was newly created
    except Exception as e:
        session.rollback()
        return None, str(e)
    finally:
        session.close()

# Function to retrieve a single author by ID
def retrieve_single_author(id: int):
    engine, SessionLocal = connect_to_db()
    session = SessionLocal()

    try:
        stmt = select(Author.author_id, Author.name, Author.biography).where(Author.author_id == id)
        result = session.execute(stmt).fetchone()
        if result:
            author = {"author_id": result[0], "name": result[1], "biography": result[2]}
            return True, "Author successfully retrieved", author
        else:
            return False, "Author could not be retrieved", None
    except Exception as e:
        return False, str(e), None
    finally:
        session.close()

# Function to retrieve a list of authors with pagination
def retrieve_authors_from_db(page: int = 1, per_page: int = 10):
    engine, SessionLocal = connect_to_db()
    session = SessionLocal()

    try:
        offset = (page - 1) * per_page
        stmt = select(Author.author_id, Author.name, Author.biography).offset(offset).limit(per_page)
        results = session.execute(stmt).fetchall()
        authors = [{"author_id": result[0], "name": result[1], "biography": result[2]} for result in results]
        return True, "Authors successfully retrieved", authors
    except Exception as e:
        return False, str(e), None
    finally:
        session.close()

# Function to add a new author to the database
def add_author_to_database(author: pydantic_author):
    engine, SessionLocal = connect_to_db()
    session = SessionLocal()

    try:
        stmt_check_author_exists = select(Author.author_id).where(Author.name == author.name)
        existing_author = session.execute(stmt_check_author_exists).fetchone()

        if existing_author:
            return False, "Author already exists", existing_author[0]

        new_author = Author(name=author.name, biography=author.biography)
        session.add(new_author)
        session.commit()
        return True, "Author added successfully", new_author.author_id
    except Exception as e:
        session.rollback()
        return False, str(e), None
    finally:
        session.close()

# Function to edit an existing author's information
def edit_author_info(author_id: int, new_author: AuthorUpdateCurrent):
    engine, SessionLocal = connect_to_db()
    session = SessionLocal()

    success, message, author = retrieve_single_author(author_id)
    if not success:
        return success, message
    
    updated_author_data = {
        "name": new_author.name if new_author.name is not None else author['name'],
        "biography": new_author.biography if new_author.biography is not None else author['biography'],
    }

    stmt = (
        update(Author)
        .where(Author.author_id == author_id)
        .values(
            name=updated_author_data["name"], 
            biography=updated_author_data["biography"]
        )
        .execution_options(synchronize_session="fetch")
    )

    try:
        session.execute(stmt)
        session.commit()
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

    return True, "Author information successfully updated"

# Function to delete an author from the database
def delete_author_from_db(author_id: int):
    engine, SessionLocal = connect_to_db()
    session = SessionLocal()

    stmt = delete(Author).where(Author.author_id == author_id)

    try:
        session.execute(stmt)
        session.commit()
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

    return True, "Author information successfully deleted"
