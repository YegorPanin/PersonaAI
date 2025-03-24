from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Bot, Story

engine = create_engine(f"sqlite:///{config.DB_PATH}/bots.db")
Session = sessionmaker(bind=engine)

def get_bot_description(bot_id: int) -> str:
    with Session() as session:
        bot = session.query(Bot).filter(Bot.id == bot_id).first()
        return bot.description if bot else ""

def save_story(user_id: int, bot_id: int, message: str, response: str):
    with Session() as session:
        story = Story(
            user_id=user_id,
            bot_id=bot_id,
            user_message=message,
            bot_response=response,
            timestamp=datetime.now()
        )
        session.add(story)
        session.commit()