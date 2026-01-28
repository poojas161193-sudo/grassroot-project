"""
Course Database Models
Separate models for Q2 Course Generation feature
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from models import Base, engine


class Course(Base):
    """
    Model for storing generated courses
    """
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey('videos.id'), index=True)
    course_id = Column(String, unique=True, index=True)  # Unique course identifier (e.g., course_1_20250128_103045)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)

    # File paths
    course_dir = Column(String)  # Directory containing all course files
    slides_path = Column(String, nullable=True)
    quiz_path = Column(String, nullable=True)
    viewer_path = Column(String, nullable=True)
    zip_path = Column(String, nullable=True)

    # Course metadata
    language = Column(String(10), default='en')  # Course language (en, ja, etc.)
    theme = Column(String(20), default='light')  # Slide theme: light, dark, corporate
    total_slides = Column(Integer, nullable=True)
    total_questions = Column(Integer, nullable=True)

    # Structure data (stored as JSON string)
    course_structure = Column(Text, nullable=True)  # JSON string of full course structure

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Course(id={self.id}, title='{self.title}', course_id='{self.course_id}')>"


def create_course_tables():
    """
    Create course-related tables
    """
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    # Test table creation
    create_course_tables()
    print("Course tables created successfully!")
