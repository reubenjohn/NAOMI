from contextlib import contextmanager
from dataclasses import asdict
import json
import os
from typing import Any
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DB_PATH = os.environ.get("DB_PATH", "sqlite:///db.sqlite")

Base: Any = declarative_base()
engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)

Message = dict[str, str]

DEFAULT_CONVERSATION_ID = 0


def dataclass_to_json(dataclass_instance):
    return json.dumps(asdict(dataclass_instance))


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class Conversation(Base):
    __tablename__ = "storylines"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)


class MessageModel(Base):
    __tablename__ = "messages"
    conversation_id = Column(Integer, primary_key=True, nullable=False)
    id = Column(Integer, primary_key=True, nullable=False)
    content = Column(Text, nullable=False)

    @property
    def content_dumps(self) -> str:
        return str(self.content)

    @property
    def content_dict(self) -> Message:
        return json.loads(self.content)  # type: ignore

    @property
    def content_val(self) -> str:
        return self.content_dict["content"]


class SummaryModel(Base):
    __tablename__ = "summaries"
    conversation_id = Column(Integer, primary_key=True, nullable=False)
    summary_until_id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)


class AgentGoalModel(Base):
    __tablename__ = "agent_goals"
    name = Column(String, primary_key=True, nullable=False)
    description = Column(Text, nullable=False)
    completed = Column(Boolean, nullable=False)
    persistence = Column(Text, nullable=False)


class PropertyModel(Base):
    __tablename__ = "properties"
    key = Column(String, primary_key=True, nullable=False)
    value = Column(Text, nullable=False)


# Database setup
def initialize_db():
    Base.metadata.create_all(engine)


# Save message to database
def add_message_to_db(message: Message, session, conversation_id: int):
    max_id = (
        session.query(func.max(MessageModel.id))
        .where(MessageModel.conversation_id == conversation_id)
        .scalar()
    )
    if max_id is None:
        max_id = 0
    message_model = MessageModel(
        conversation_id=conversation_id,
        id=max_id + 1,
        content=json.dumps(message),
    )
    session.add(message_model)
    return message_model


def save_agent_goal(goal: AgentGoalModel):
    with session_scope() as session:
        session.add(goal)


def load_goals_from_db() -> list[AgentGoalModel]:
    with session_scope() as session:
        return session.query(AgentGoalModel).order_by(AgentGoalModel.name).all()


def get_all_tables():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT name, sql FROM sqlite_master WHERE type='table';"))
        return [(name, sql) for name, sql in result]
