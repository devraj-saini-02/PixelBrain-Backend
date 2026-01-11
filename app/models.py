from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    images = relationship("Image", back_populates="owner")
    
class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    indoor = Column(Boolean, nullable=False)
    daytime = Column(String, nullable=True)
    weather = Column(String, nullable=True)
    image_url = Column(String, nullable=False)     
    public_id = Column(String, nullable=False)     
    private = Column(Boolean, nullable=False, server_default=text('true'), default=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    primary_object=Column(String,nullable=True)
    filter1=Column(String,nullable=True)
    filter2=Column(String,nullable=True)
    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    owner = relationship("User", back_populates="images")
