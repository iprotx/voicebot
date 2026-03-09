from backend.storage.repositories import InMemoryMessageRepository, InMemoryUserRepository

user_repo = InMemoryUserRepository()
message_repo = InMemoryMessageRepository()
