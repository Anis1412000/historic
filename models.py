from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ChatHistory(db.Model):
    __tablename__ = 'chat_history'
    id = db.Column(db.Integer, primary_key=True)
    user_prompt = db.Column(db.String(1000), nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def serialize(self):
        return {
            "id": self.id,
            "user_prompt": self.user_prompt,
            "bot_response": self.bot_response,
            "timestamp": self.timestamp.isoformat()
        }