from sqlalchemy import DateTime, UUID, String
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import ARRAY

from datetime import datetime
from typing import List

class Base(DeclarativeBase):
    pass


class AccessToken(Base):
    __tablename__ = "access_token"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(String(), index=True)
    token: Mapped[str] = mapped_column(String(), index=True)
    email: Mapped[str] = mapped_column(String(), index=True)
    expires: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    last_used: Mapped[datetime] = mapped_column(DateTime(), nullable=True)
    scopes: Mapped[List[str]] = mapped_column(ARRAY(String), index=True)

    def __repr__(self) -> str:
        return f"AccessToken(token={self.token!r}, email={self.email!r}, expires={self.expires!r}, scopes={self.scopes!r})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "token": self.token,
            "email": self.email,
            "expires": self.expires,
            "created": self.created,
            "last_used": self.last_used,
            "scopes": self.scopes
        }