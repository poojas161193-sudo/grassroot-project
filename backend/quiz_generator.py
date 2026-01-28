"""
Quiz Generator
Automatically generates quiz questions from course content
Supports multiple question types and difficulty levels
"""

from openai import OpenAI
import json
import random
from typing import Dict, List, Optional
from decouple import config


class QuizGenerator:
    """
    Generates quiz questions from course content
    """

    def __init__(self):
        self.model = "gpt-4o"
        self.client = OpenAI(api_key=config('OPENAI_API_KEY'))

    def generate_quiz(
        self,
        course_data: Dict,
        num_questions: int = 10,
        difficulty_mix: Optional[Dict] = None,
        question_types: Optional[List[str]] = None,
        language: str = "en"
    ) -> Dict:
        """
        Generates a complete quiz from course content

        Args:
            course_data: Course structure with chapters
            num_questions: Total number of questions to generate
            difficulty_mix: Dict like {"easy": 40, "medium": 40, "hard": 20} (percentages)
            question_types: List like ["mcq", "true_false", "fill_blank"]
            language: Language code

        Returns:
            Dict with quiz data
        """

        if difficulty_mix is None:
            difficulty_mix = {"easy": 40, "medium": 40, "hard": 20}

        if question_types is None:
            question_types = ["mcq", "true_false", "fill_blank"]

        course = course_data.get("course", {})
        chapters = course.get("chapters", [])

        # Calculate questions per difficulty
        num_easy = int(num_questions * difficulty_mix.get("easy", 40) / 100)
        num_medium = int(num_questions * difficulty_mix.get("medium", 40) / 100)
        num_hard = num_questions - num_easy - num_medium

        questions = []

        # Generate questions for each difficulty level
        for difficulty, count in [("easy", num_easy), ("medium", num_medium), ("hard", num_hard)]:
            for _ in range(count):
                # Pick a random chapter
                if not chapters:
                    continue

                chapter = random.choice(chapters)

                # Pick a random question type
                q_type = random.choice(question_types)

                # Generate question
                question = self._generate_question(
                    chapter=chapter,
                    question_type=q_type,
                    difficulty=difficulty,
                    language=language
                )

                if question:
                    question["id"] = len(questions) + 1
                    question["chapter"] = chapter.get("number", 1)
                    questions.append(question)

        # Shuffle questions
        random.shuffle(questions)

        # Re-number after shuffle
        for i, q in enumerate(questions):
            q["id"] = i + 1

        quiz_data = {
            "quiz": {
                "title": f"{course.get('title', 'Course')} - Quiz",
                "passing_score": 70,
                "time_limit": num_questions * 2,  # 2 minutes per question
                "total_questions": len(questions),
                "questions": questions
            }
        }

        return quiz_data

    def _generate_question(
        self,
        chapter: Dict,
        question_type: str,
        difficulty: str,
        language: str
    ) -> Optional[Dict]:
        """
        Generates a single question from chapter content

        Args:
            chapter: Chapter data
            question_type: "mcq", "true_false", or "fill_blank"
            difficulty: "easy", "medium", or "hard"
            language: Language code

        Returns:
            Question dict or None
        """

        content = chapter.get("content", "")
        key_points = chapter.get("key_points", [])
        title = chapter.get("title", "")

        # Combine content for context
        context = f"Chapter: {title}\n\n"
        context += f"Content: {content[:2000]}\n\n"
        context += f"Key Points: {', '.join(key_points[:3])}"

        if question_type == "mcq":
            return self._generate_mcq(context, difficulty, language)
        elif question_type == "true_false":
            return self._generate_true_false(context, difficulty, language)
        elif question_type == "fill_blank":
            return self._generate_fill_blank(context, difficulty, language)
        else:
            return self._generate_mcq(context, difficulty, language)

    def _generate_mcq(self, context: str, difficulty: str, language: str) -> Optional[Dict]:
        """Generates a Multiple Choice Question"""

        prompt = f"""
Based on this content, create ONE multiple choice question.

Content:
{context}

Difficulty: {difficulty}
- Easy: Direct recall of facts
- Medium: Understanding and application
- Hard: Analysis and evaluation

Create a question with 4 options (A, B, C, D) where:
- One option is clearly correct
- Three options are plausible but incorrect (distractors)
- Distractors should be common misconceptions or similar concepts

Return as JSON:
{{
  "question": "The question text",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": 0,
  "explanation": "Why the correct answer is correct and others are wrong",
  "difficulty": "{difficulty}",
  "points": 1
}}

Note: correct_answer is 0-indexed (0=A, 1=B, 2=C, 3=D)
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating educational quiz questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            question = json.loads(response.choices[0].message.content)
            question["type"] = "mcq"
            return question

        except Exception as e:
            print(f"Error generating MCQ: {str(e)}")
            return None

    def _generate_true_false(self, context: str, difficulty: str, language: str) -> Optional[Dict]:
        """Generates a True/False Question"""

        prompt = f"""
Based on this content, create ONE true/false question.

Content:
{context}

Difficulty: {difficulty}

Create a statement that is either true or false.
For medium/hard difficulty, make the statement subtle or require careful thinking.

Return as JSON:
{{
  "question": "The statement to evaluate",
  "correct_answer": true,
  "explanation": "Why this statement is true/false",
  "difficulty": "{difficulty}",
  "points": 1
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating educational quiz questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            question = json.loads(response.choices[0].message.content)
            question["type"] = "true_false"
            question["options"] = ["True", "False"]
            # Convert boolean to index (True=0, False=1)
            question["correct_answer"] = 0 if question["correct_answer"] else 1

            return question

        except Exception as e:
            print(f"Error generating True/False: {str(e)}")
            return None

    def _generate_fill_blank(self, context: str, difficulty: str, language: str) -> Optional[Dict]:
        """Generates a Fill-in-the-Blank Question"""

        prompt = f"""
Based on this content, create ONE fill-in-the-blank question.

Content:
{context}

Difficulty: {difficulty}

Create a sentence with ONE blank (use _____) where a key term or concept should go.
The blank should test important knowledge.

Return as JSON:
{{
  "question": "A sentence with _____ for the blank",
  "correct_answer": "the word/phrase that fills the blank",
  "acceptable_answers": ["correct answer", "acceptable alternative", "another variant"],
  "explanation": "Why this answer is correct",
  "difficulty": "{difficulty}",
  "points": 1
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating educational quiz questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            question = json.loads(response.choices[0].message.content)
            question["type"] = "fill_blank"
            return question

        except Exception as e:
            print(f"Error generating Fill-in-Blank: {str(e)}")
            return None

    def generate_distractors(self, correct_answer: str, context: str, num_distractors: int = 3) -> List[str]:
        """
        Generates plausible wrong answers (distractors) for MCQ

        Args:
            correct_answer: The correct answer
            context: Content context
            num_distractors: Number of distractors to generate

        Returns:
            List of distractor strings
        """

        prompt = f"""
Generate {num_distractors} plausible but incorrect answers (distractors) for this question.

Correct Answer: {correct_answer}
Context: {context[:1000]}

Distractors should be:
1. Plausible (sound like they could be correct)
2. Related to the topic
3. Based on common misconceptions
4. Similar in length and format to the correct answer

Return as JSON:
{{
  "distractors": ["distractor1", "distractor2", "distractor3"]
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating educational quiz questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result.get("distractors", [])

        except Exception as e:
            print(f"Error generating distractors: {str(e)}")
            return []

    def validate_quiz(self, quiz_data: Dict) -> tuple[bool, List[str]]:
        """
        Validates quiz data structure and quality

        Returns:
            (is_valid, list_of_errors)
        """

        errors = []

        if "quiz" not in quiz_data:
            errors.append("Missing 'quiz' key")
            return False, errors

        quiz = quiz_data["quiz"]

        # Check required fields
        required_fields = ["title", "questions"]
        for field in required_fields:
            if field not in quiz:
                errors.append(f"Missing required field: {field}")

        # Validate questions
        questions = quiz.get("questions", [])

        if len(questions) < 5:
            errors.append("Quiz should have at least 5 questions")

        for i, q in enumerate(questions):
            q_num = i + 1

            # Check required question fields
            if "question" not in q:
                errors.append(f"Question {q_num}: Missing question text")

            if "type" not in q:
                errors.append(f"Question {q_num}: Missing type")

            if "correct_answer" not in q:
                errors.append(f"Question {q_num}: Missing correct_answer")

            # Type-specific validation
            q_type = q.get("type", "")

            if q_type == "mcq":
                if "options" not in q or len(q.get("options", [])) != 4:
                    errors.append(f"Question {q_num}: MCQ must have exactly 4 options")

                correct_idx = q.get("correct_answer")
                if not isinstance(correct_idx, int) or correct_idx < 0 or correct_idx > 3:
                    errors.append(f"Question {q_num}: Invalid correct_answer index")

            elif q_type == "true_false":
                correct_ans = q.get("correct_answer")
                if correct_ans not in [0, 1]:
                    errors.append(f"Question {q_num}: True/False answer must be 0 or 1")

        is_valid = len(errors) == 0
        return is_valid, errors

    def calculate_score(self, quiz_data: Dict, user_answers: Dict) -> Dict:
        """
        Calculates quiz score based on user answers

        Args:
            quiz_data: Quiz with correct answers
            user_answers: Dict mapping question_id to user's answer

        Returns:
            Dict with score, percentage, passed, feedback
        """

        questions = quiz_data.get("quiz", {}).get("questions", [])
        passing_score = quiz_data.get("quiz", {}).get("passing_score", 70)

        total_points = 0
        earned_points = 0
        results = []

        for question in questions:
            q_id = question.get("id")
            points = question.get("points", 1)
            total_points += points

            user_answer = user_answers.get(str(q_id))
            correct_answer = question.get("correct_answer")

            # Check if answer is correct
            is_correct = False

            if question.get("type") == "fill_blank":
                # For fill-in-blank, check acceptable answers
                acceptable = question.get("acceptable_answers", [])
                if user_answer:
                    user_answer_lower = str(user_answer).lower().strip()
                    is_correct = any(
                        user_answer_lower == acc.lower().strip()
                        for acc in acceptable
                    )
            else:
                # For MCQ and True/False
                is_correct = user_answer == correct_answer

            if is_correct:
                earned_points += points

            results.append({
                "question_id": q_id,
                "correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "explanation": question.get("explanation", "")
            })

        percentage = (earned_points / total_points * 100) if total_points > 0 else 0
        passed = percentage >= passing_score

        return {
            "total_questions": len(questions),
            "total_points": total_points,
            "earned_points": earned_points,
            "percentage": round(percentage, 2),
            "passed": passed,
            "passing_score": passing_score,
            "results": results
        }


# Helper function
def generate_quiz_from_course(
    course_data: Dict,
    num_questions: int = 10,
    language: str = "en"
) -> Dict:
    """
    Convenience function to generate quiz

    Args:
        course_data: Course structure
        num_questions: Number of questions
        language: Language code

    Returns:
        Quiz data
    """
    generator = QuizGenerator()
    return generator.generate_quiz(course_data, num_questions=num_questions, language=language)


if __name__ == "__main__":
    # Test with sample course data
    sample_course = {
        "course": {
            "title": "Python Fundamentals",
            "chapters": [
                {
                    "number": 1,
                    "title": "Variables and Data Types",
                    "content": "In Python, variables are used to store data. Python has several data types including integers, floats, strings, and booleans. Variables are dynamically typed, meaning you don't need to declare their type.",
                    "key_points": [
                        "Variables store data values",
                        "Python uses dynamic typing",
                        "Common types: int, float, str, bool"
                    ]
                },
                {
                    "number": 2,
                    "title": "Control Flow",
                    "content": "Control flow statements allow you to control the execution of your code. Python uses if-elif-else for conditional execution and for and while loops for repetition.",
                    "key_points": [
                        "if-elif-else for conditions",
                        "for loops iterate over sequences",
                        "while loops run until condition is false"
                    ]
                }
            ]
        }
    }

    generator = QuizGenerator()
    quiz = generator.generate_quiz(sample_course, num_questions=5, language="en")

    print("Generated Quiz:")
    print(json.dumps(quiz, indent=2))

    # Validate
    is_valid, errors = generator.validate_quiz(quiz)
    print(f"\nQuiz Valid: {is_valid}")
    if errors:
        print("Errors:", errors)
