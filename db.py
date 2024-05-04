import logging

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from config import settings

Base = declarative_base()

# Create an engine at the module level
engine = create_engine(settings.database_url, echo=False)


def get_session():
    # Create a thread-safe session factory
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)

    bookmarks = relationship("Bookmark", back_populates="user")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True)
    url = Column(String(255), nullable=False)
    title = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="bookmarks")
    tags = relationship("Tag", secondary="bookmark_tags", back_populates="bookmarks")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    bookmarks = relationship(
        "Bookmark", secondary="bookmark_tags", back_populates="tags"
    )


class BookmarkTag(Base):
    __tablename__ = "bookmark_tags"

    bookmark_id = Column(Integer, ForeignKey("bookmarks.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)


if __name__ == "__main__":
    from datetime import datetime
    from sqlalchemy import create_engine

    engine = create_engine(settings.database_url, echo=True)
    Base.metadata.create_all(engine)
    
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=engine)
    session = Session()

    default_user = User(username='mvv', email='michael@mvanveen.net', password='securepassword', created_at=datetime.now())
    session.add(default_user)
    session.commit()