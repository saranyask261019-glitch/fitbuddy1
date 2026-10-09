from typing import Literal
from pydantic import BaseModel, Field, field_validator

Goal = Literal["general wellness", "strength", "muscle gain", "cardio fitness", "flexibility"]
Intensity = Literal["low", "medium", "high"]

class UserInput(BaseModel):
    username: str = Field(min_length=1, max_length=120)
    user_id: str = Field(min_length=2, max_length=80)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=0, le=500)
    goal: Goal
    intensity: Intensity

    @field_validator("username", "user_id")
    @classmethod
    def trim_strings(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value

class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=80)
    feedback: str = Field(min_length=3, max_length=1000)

    @field_validator("feedback")
    @classmethod
    def trim_feedback(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Please enter at least 3 characters.")
        return value
