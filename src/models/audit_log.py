from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    action = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Renamed Python attribute, but database column still named "metadata"
    details = Column("metadata", Text, nullable=True)

    immutable = Column(Integer, default=1, nullable=False)

    def __repr__(self):
        return (
            f"<AuditLog(id={self.id}, user_id={self.user_id}, action={self.action}, "
            f"ip_address={self.ip_address}, timestamp={self.timestamp})>"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.details,  # keep API compatibility
            "immutable": bool(self.immutable),
        }
