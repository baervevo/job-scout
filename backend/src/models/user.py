from typing import Optional, List

from pydantic import BaseModel


class User(BaseModel):
    id: int
    login: str
    password: str

    def validate_password(self, password: str) -> bool:
        return self.password == password
