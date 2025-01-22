from pydantic import BaseModel, EmailStr

class CredentialCreationOptionsRequest(BaseModel):
    id: str
    email: EmailStr
    display_name: str

class RegistrationResponseJSON(BaseModel):
    id: str
    rawId: str
    response: dict
    clientExtensionResults: dict
    type: str
    email: EmailStr

class AuthenticationResponseJSON(BaseModel):
    id: str
    rawId: str
    response: dict
    clientExtensionResults: dict
    type: str