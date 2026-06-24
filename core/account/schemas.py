from pydantic import BaseModel, Field, model_validator


class RegiterationSchema(BaseModel):
    username: str = Field(..., max_length=250)
    password: str = Field(...)
    confirm_password: str = Field(...)

    @model_validator(mode="after")
    def check_passwords_match(self) -> "RegiterationSchema":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class RefreshAccessTokenSchema(BaseModel):
    refresh_token: str = Field(...)


class AccessTokenVerifySchema(BaseModel):
    access_roken: str = Field(...)


class LoginSchema(BaseModel):
    username: str = Field(...)
    password: str = Field(...)
