from pydantic import BaseModel, EmailStr, model_validator

class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def check_password_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Password và Confirm Password không khớp")
        return self
