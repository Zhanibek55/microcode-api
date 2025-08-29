"""Database models"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.session import Base


class TaskStatus(PyEnum):
    """Task execution status"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskComplexity(PyEnum):
    """Task complexity levels"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class TaskType(PyEnum):
    """Available task types"""
    FILE_ORGANIZATION = "file_organization"
    EXCEL_PROCESSING = "excel_processing"
    EMAIL_AUTOMATION = "email_automation"
    PDF_PROCESSING = "pdf_processing"
    WEB_SCRAPING = "web_scraping"


class PaymentStatus(PyEnum):
    """Payment status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    
    # Authentication
    google_id = Column(String, unique=True, nullable=True)
    telegram_id = Column(String, unique=True, nullable=True)
    github_id = Column(String, unique=True, nullable=True)
    
    # Profile information
    preferred_language = Column(String, default="en")
    timezone = Column(String, default="UTC")
    country = Column(String, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    tasks = relationship("Task", back_populates="user")
    payments = relationship("Payment", back_populates="user")


class Task(Base):
    """Task model"""
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Task details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    task_type = Column(Enum(TaskType), nullable=False)
    complexity = Column(Enum(TaskComplexity), nullable=True)
    
    # Task execution
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    ai_analysis = Column(JSON, nullable=True)
    generated_code = Column(Text, nullable=True)
    execution_result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Pricing
    estimated_price = Column(Float, nullable=True)
    final_price = Column(Float, nullable=True)
    
    # Files
    input_files = Column(JSON, nullable=True)  # Store file metadata
    output_files = Column(JSON, nullable=True)  # Store generated files info
    
    # Timing
    estimated_duration = Column(Integer, nullable=True)  # in seconds
    actual_duration = Column(Integer, nullable=True)  # in seconds
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    payment = relationship("Payment", back_populates="task", uselist=False)


class Payment(Base):
    """Payment model"""
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    
    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Payment provider details
    provider = Column(String, nullable=False)  # stripe, yookassa
    provider_payment_id = Column(String, nullable=True)
    provider_response = Column(JSON, nullable=True)
    
    # Additional info
    payment_method = Column(String, nullable=True)
    receipt_url = Column(String, nullable=True)
    refund_reason = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    task = relationship("Task", back_populates="payment")


class SystemMetrics(Base):
    """System metrics and monitoring"""
    __tablename__ = "system_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Metrics
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String, nullable=True)
    
    # Context
    context = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class APIKey(Base):
    """API keys for external integrations"""
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Key details
    key_name = Column(String, nullable=False)
    key_hash = Column(String, nullable=False)  # Hashed version
    service = Column(String, nullable=False)  # openai, anthropic, etc.
    
    # Permissions and limits
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, nullable=True)
    daily_limit = Column(Integer, nullable=True)
    
    # Usage tracking
    total_requests = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)