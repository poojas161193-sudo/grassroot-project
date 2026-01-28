"""
Course Structure Generator
Analyzes video transcripts or documents and generates structured course outlines
"""

from openai import OpenAI
import json
from typing import Dict, List, Optional
from decouple import config

class CourseStructurer:
    """
    Generates structured course outlines from unstructured content
    """

    def __init__(self):
        self.model = "gpt-4o"
        self.client = OpenAI(api_key=config('OPENAI_API_KEY'))

    def analyze_content(
        self,
        content: str,
        source_type: str = "transcript",
        language: str = "en",
        duration_minutes: Optional[int] = None
    ) -> Dict:
        """
        Analyzes content and generates a structured course outline

        Args:
            content: Video transcript or document text
            source_type: "transcript", "document", or "text"
            language: Language code (en, ja, etc.)
            duration_minutes: Optional duration for time estimates

        Returns:
            Dict with course structure including chapters, objectives, etc.
        """

        # Generate course outline
        outline_prompt = self._create_outline_prompt(content, language, duration_minutes)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert instructional designer who creates well-structured, engaging course outlines."
                    },
                    {
                        "role": "user",
                        "content": outline_prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            course_data = json.loads(response.choices[0].message.content)

            # Enhance with additional processing
            course_data = self._enhance_course_structure(course_data, content)

            return course_data

        except Exception as e:
            print(f"Error analyzing content: {str(e)}")
            raise

    def _create_outline_prompt(
        self,
        content: str,
        language: str,
        duration_minutes: Optional[int]
    ) -> str:
        """Creates the prompt for generating course outline"""

        duration_text = f"The original content is approximately {duration_minutes} minutes long." if duration_minutes else ""

        lang_names = {
            "en": "English",
            "ja": "Japanese"
        }
        language_name = lang_names.get(language, "English")

        prompt = f"""
Analyze the following content and create a structured course outline in {language_name}.

Content:
{content[:50000]}

{duration_text}

Create a comprehensive course outline with the following structure (respond in JSON format):

{{
  "course": {{
    "title": "An engaging, clear course title",
    "description": "2-3 sentence course description",
    "duration": "Estimated total duration (e.g., '3 hours', '2 days')",
    "difficulty": "beginner|intermediate|advanced",
    "prerequisites": ["List of prerequisites"],
    "learning_outcomes": [
      "What learners will be able to do after completing (action verbs: create, analyze, etc.)"
    ],
    "chapters": [
      {{
        "number": 1,
        "title": "Chapter title",
        "duration": "Estimated duration in minutes",
        "learning_objectives": [
          "Specific, measurable objectives using Bloom's taxonomy"
        ],
        "key_points": [
          "Detailed explanations for each main concept (2-3 sentences each, include examples and context). Provide 8-15 key points per chapter."
        ],
        "content": "Comprehensive chapter content with detailed explanations (5-8 paragraphs covering all key concepts thoroughly)",
        "activities": ["Suggested learning activities"],
        "assessment_questions": 3
      }}
    ]
  }}
}}

Guidelines:
1. Create 5-8 chapters (based on content complexity)
2. Each chapter should be 20-40 minutes of learning
3. Use clear, action-oriented language
4. Learning objectives should use Bloom's taxonomy verbs (understand, apply, analyze, etc.)
5. **IMPORTANT**: Key points should be DETAILED explanations (2-3 sentences each) with examples and context, NOT just bullet points. Provide 8-15 key points per chapter to ensure comprehensive coverage for a complete learning experience.
6. Ensure logical progression from basics to advanced concepts
7. Content should be comprehensive with detailed explanations, examples, and practical insights to create informative slides from

Respond ONLY with valid JSON matching the structure above.
"""

        return prompt

    def _enhance_course_structure(self, course_data: Dict, original_content: str) -> Dict:
        """
        Enhances the generated course structure with additional metadata
        """

        # Add metadata
        if "course" in course_data:
            course = course_data["course"]

            # Calculate total assessment questions
            total_questions = sum(
                chapter.get("assessment_questions", 0)
                for chapter in course.get("chapters", [])
            )
            course["total_assessment_questions"] = total_questions

            # Add difficulty tags to chapters
            for i, chapter in enumerate(course.get("chapters", [])):
                if i < 2:
                    chapter["difficulty_level"] = "easy"
                elif i < len(course["chapters"]) - 1:
                    chapter["difficulty_level"] = "medium"
                else:
                    chapter["difficulty_level"] = "hard"

                # Add slide count estimate (1 title + 1 objectives + content/3 + 1 summary)
                content_slides = max(2, len(chapter.get("key_points", [])))
                chapter["estimated_slides"] = 3 + content_slides

            # Calculate total slides
            course["total_slides"] = sum(
                chapter.get("estimated_slides", 5)
                for chapter in course.get("chapters", [])
            ) + 2  # +2 for title and final summary

        return course_data

    def generate_chapter_outline(self, transcript: str, num_chapters: int = 6) -> List[Dict]:
        """
        Breaks transcript into logical chapters

        Args:
            transcript: Full video transcript
            num_chapters: Desired number of chapters

        Returns:
            List of chapter dictionaries with timestamps
        """

        prompt = f"""
Analyze this transcript and divide it into {num_chapters} logical chapters.
For each chapter, identify:
1. A clear title
2. The main topic/theme
3. Approximate timestamp ranges (if timestamps are present)
4. Key concepts covered

Transcript:
{transcript[:6000]}

Return as JSON:
{{
  "chapters": [
    {{
      "number": 1,
      "title": "Chapter title",
      "theme": "Main theme",
      "start_time": "00:00",
      "end_time": "08:30",
      "concepts": ["concept1", "concept2"]
    }}
  ]
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing educational content and creating logical chapter divisions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result.get("chapters", [])

        except Exception as e:
            print(f"Error generating chapter outline: {str(e)}")
            return []

    def create_learning_objectives(self, chapter_content: str, difficulty: str = "medium") -> List[str]:
        """
        Generates learning objectives for a chapter using Bloom's taxonomy

        Args:
            chapter_content: Chapter text content
            difficulty: easy, medium, or hard

        Returns:
            List of learning objectives
        """

        bloom_verbs = {
            "easy": ["identify", "describe", "explain", "list", "recognize"],
            "medium": ["apply", "demonstrate", "implement", "solve", "use"],
            "hard": ["analyze", "evaluate", "create", "design", "critique"]
        }

        verbs = bloom_verbs.get(difficulty, bloom_verbs["medium"])

        prompt = f"""
Create 3-4 specific learning objectives for this chapter content.

Use these action verbs: {', '.join(verbs)}

Chapter content:
{chapter_content[:2000]}

Format each objective as:
"[Action verb] [specific skill/knowledge] [context/condition]"

Example: "Apply machine learning algorithms to classify text data"

Return as JSON:
{{
  "objectives": ["objective1", "objective2", "objective3"]
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an instructional designer creating measurable learning objectives."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result.get("objectives", [])

        except Exception as e:
            print(f"Error creating learning objectives: {str(e)}")
            return []

    def extract_key_points(self, content: str, max_points: int = 5) -> List[str]:
        """
        Extracts key points from content

        Args:
            content: Chapter or section content
            max_points: Maximum number of key points

        Returns:
            List of key points
        """

        prompt = f"""
Extract the {max_points} most important key points from this content.

Content:
{content[:3000]}

Each key point should be:
- One clear, concise sentence
- A standalone concept
- Important for understanding the topic

Return as JSON:
{{
  "key_points": ["point1", "point2", ...]
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying key concepts in educational content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result.get("key_points", [])

        except Exception as e:
            print(f"Error extracting key points: {str(e)}")
            return []

    def map_to_bloom_taxonomy(self, objective: str) -> str:
        """
        Maps a learning objective to Bloom's taxonomy level

        Returns: remember, understand, apply, analyze, evaluate, create
        """

        objective_lower = objective.lower()

        taxonomy_mapping = {
            "remember": ["list", "identify", "name", "recall", "recognize", "state"],
            "understand": ["explain", "describe", "summarize", "interpret", "clarify"],
            "apply": ["use", "demonstrate", "implement", "solve", "execute", "apply"],
            "analyze": ["analyze", "compare", "contrast", "examine", "differentiate"],
            "evaluate": ["evaluate", "assess", "critique", "judge", "justify"],
            "create": ["create", "design", "develop", "construct", "formulate", "generate"]
        }

        for level, verbs in taxonomy_mapping.items():
            for verb in verbs:
                if verb in objective_lower:
                    return level

        return "understand"  # Default

    def validate_course_structure(self, course_data: Dict) -> tuple[bool, List[str]]:
        """
        Validates that the course structure is complete and correct

        Returns:
            (is_valid, list_of_errors)
        """

        errors = []

        if "course" not in course_data:
            errors.append("Missing 'course' key")
            return False, errors

        course = course_data["course"]

        # Required fields
        required_fields = ["title", "description", "chapters"]
        for field in required_fields:
            if field not in course:
                errors.append(f"Missing required field: {field}")

        # Validate chapters
        if "chapters" in course:
            chapters = course["chapters"]

            if len(chapters) < 3:
                errors.append("Course must have at least 3 chapters")

            if len(chapters) > 12:
                errors.append("Course should not exceed 12 chapters")

            for i, chapter in enumerate(chapters):
                chapter_required = ["number", "title", "content", "learning_objectives"]
                for field in chapter_required:
                    if field not in chapter:
                        errors.append(f"Chapter {i+1} missing required field: {field}")

        is_valid = len(errors) == 0
        return is_valid, errors


# Helper function for easy import
def create_course_structure(content: str, source_type: str = "transcript", language: str = "en") -> Dict:
    """
    Convenience function to create course structure

    Args:
        content: Video transcript or document text
        source_type: "transcript", "document", or "text"
        language: Language code

    Returns:
        Course structure dictionary
    """
    structurer = CourseStructurer()
    return structurer.analyze_content(content, source_type, language)


if __name__ == "__main__":
    # Test with sample content
    sample_transcript = """
    Welcome to this introduction to Python programming.
    Python is a high-level, interpreted programming language known for its simplicity and readability.

    Let's start with variables. In Python, you don't need to declare variable types.
    You can simply assign a value to a variable name. For example: x = 5 or name = "John".

    Python supports various data types including integers, floats, strings, lists, and dictionaries.
    Each data type has its own properties and methods.

    Control flow is essential in programming. Python uses if-else statements and loops like for and while.
    Indentation is crucial in Python as it defines code blocks.

    Functions in Python are defined using the def keyword. They help organize code and make it reusable.
    You can pass parameters to functions and return values.

    Object-oriented programming in Python uses classes and objects. Classes are blueprints for creating objects.
    Python supports inheritance, encapsulation, and polymorphism.
    """

    structurer = CourseStructurer()
    result = structurer.analyze_content(sample_transcript, source_type="transcript", language="en")

    print("Generated Course Structure:")
    print(json.dumps(result, indent=2))
