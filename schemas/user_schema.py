from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator

class UserRegister(BaseModel):
    email: EmailStr
    name: str 
    password: str = Field(min_length = 8)
    role: str = "user"
    confirm_password: str = Field(min_length = 8)

    @field_validator("name")
    @classmethod
    def name_must_not_contain_numbers(cls, v):
        if any(char.isdigit() for char in v):
            raise ValueError("Tên không được chứa chữ số")
        return v

    @model_validator(mode="after")
    def check_password_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Password và Confirm Password không khớp")
        return self

class UserLogin(BaseModel):
    email: EmailStr
    password: str
