from pydantic_settings import BaseSettings

PINBOARD_API_URL = "https://api.pinboard.in/v1/posts/all"


class Settings(BaseSettings):
    database_url: str = "sqlite:///bookmarks.db"
    pinboard_api_token: str

    @property
    def pinboard_api_url(self) -> str:
        return f"{PINBOARD_API_URL}?auth_token={self.pinboard_api_token}&format=json"

    class Config:
        env_file = "local.env"


settings = Settings()
