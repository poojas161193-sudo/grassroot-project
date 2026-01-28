"""
Course Assembler
Combines course structure, slides, and quiz into a complete course package
"""

import os
import json
import zipfile
from typing import Dict, Optional
from datetime import datetime


class CourseAssembler:
    """
    Assembles complete course from individual components
    """

    def __init__(self):
        self.output_dir = "generated_courses"
        os.makedirs(self.output_dir, exist_ok=True)

    def assemble_course(
        self,
        course_structure: Dict,
        slides_html: str,
        quiz_data: Dict,
        course_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Assembles complete course package

        Args:
            course_structure: Course outline from CourseStructurer
            slides_html: Generated slides HTML from SlideGenerator
            quiz_data: Quiz from QuizGenerator
            course_id: Unique course identifier
            metadata: Additional metadata (video_id, language, etc.)

        Returns:
            Dict with course package info and file paths
        """

        course = course_structure.get("course", {})
        course_title = course.get("title", "Course")

        # Create course directory
        course_dir = os.path.join(self.output_dir, course_id)
        os.makedirs(course_dir, exist_ok=True)

        # Save course structure as JSON
        structure_path = os.path.join(course_dir, "course_structure.json")
        with open(structure_path, 'w', encoding='utf-8') as f:
            json.dump(course_structure, f, indent=2, ensure_ascii=False)

        # Save slides HTML
        slides_path = os.path.join(course_dir, "slides.html")
        with open(slides_path, 'w', encoding='utf-8') as f:
            f.write(slides_html)

        # Save quiz data as JSON
        quiz_path = os.path.join(course_dir, "quiz_data.json")
        with open(quiz_path, 'w', encoding='utf-8') as f:
            json.dump(quiz_data, f, indent=2, ensure_ascii=False)

        # Generate quiz HTML
        quiz_html = self._generate_quiz_html(quiz_data, course_title)
        quiz_html_path = os.path.join(course_dir, "quiz.html")
        with open(quiz_html_path, 'w', encoding='utf-8') as f:
            f.write(quiz_html)

        # Generate course viewer (combines slides + quiz)
        viewer_html = self._generate_course_viewer(
            course_title=course_title,
            slides_file="slides.html",
            quiz_file="quiz.html",
            course_structure=course_structure,
            quiz_data=quiz_data
        )
        viewer_path = os.path.join(course_dir, "index.html")
        with open(viewer_path, 'w', encoding='utf-8') as f:
            f.write(viewer_html)

        # Save metadata
        full_metadata = {
            "course_id": course_id,
            "title": course_title,
            "created_at": datetime.now().isoformat(),
            "structure_file": "course_structure.json",
            "slides_file": "slides.html",
            "quiz_file": "quiz.html",
            "viewer_file": "index.html"
        }
        if metadata:
            full_metadata.update(metadata)

        metadata_path = os.path.join(course_dir, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(full_metadata, f, indent=2)

        return {
            "course_id": course_id,
            "course_dir": course_dir,
            "files": {
                "structure": structure_path,
                "slides": slides_path,
                "quiz_data": quiz_path,
                "quiz_html": quiz_html_path,
                "viewer": viewer_path,
                "metadata": metadata_path
            },
            "metadata": full_metadata
        }

    def _generate_quiz_html(self, quiz_data: Dict, course_title: str) -> str:
        """Generates standalone quiz HTML"""

        quiz = quiz_data.get("quiz", {})
        questions = quiz.get("questions", [])

        # Generate questions HTML
        questions_html = []
        for q in questions:
            q_html = self._generate_question_html(q)
            questions_html.append(q_html)

        questions_content = "\n".join(questions_html)

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{quiz.get('title', 'Quiz')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .quiz-container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}

        .quiz-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .quiz-header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}

        .quiz-info {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
            font-size: 0.9em;
        }}

        .quiz-content {{
            padding: 30px;
        }}

        .question {{
            margin-bottom: 40px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}

        .question-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}

        .question-number {{
            font-weight: bold;
            color: #667eea;
            font-size: 0.9em;
        }}

        .question-difficulty {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            text-transform: uppercase;
        }}

        .difficulty-easy {{
            background: #d4edda;
            color: #155724;
        }}

        .difficulty-medium {{
            background: #fff3cd;
            color: #856404;
        }}

        .difficulty-hard {{
            background: #f8d7da;
            color: #721c24;
        }}

        .question-text {{
            font-size: 1.1em;
            margin-bottom: 20px;
            color: #333;
            line-height: 1.6;
        }}

        .options {{
            list-style: none;
        }}

        .option {{
            margin: 10px 0;
        }}

        .option label {{
            display: block;
            padding: 15px 20px;
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .option label:hover {{
            border-color: #667eea;
            background: #f0f4ff;
        }}

        .option input[type="radio"] {{
            margin-right: 10px;
        }}

        .fill-blank-input {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }}

        .fill-blank-input:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .quiz-actions {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 30px;
            padding: 30px;
            background: #f8f9fa;
        }}

        .btn {{
            padding: 15px 40px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}

        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }}

        .btn-secondary {{
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }}

        .btn-secondary:hover {{
            background: #667eea;
            color: white;
        }}

        .results {{
            display: none;
            padding: 30px;
        }}

        .results.show {{
            display: block;
        }}

        .score-display {{
            text-align: center;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 30px;
        }}

        .score-display h2 {{
            font-size: 3em;
            margin-bottom: 10px;
        }}

        .passed {{
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        }}

        .failed {{
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        }}

        .result-item {{
            margin: 20px 0;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid;
        }}

        .result-correct {{
            background: #d4edda;
            border-color: #28a745;
        }}

        .result-incorrect {{
            background: #f8d7da;
            border-color: #dc3545;
        }}

        .explanation {{
            margin-top: 10px;
            padding: 15px;
            background: rgba(255,255,255,0.5);
            border-radius: 5px;
            font-size: 0.9em;
        }}

        @media (max-width: 768px) {{
            .quiz-container {{
                margin: 10px;
            }}

            .quiz-header h1 {{
                font-size: 1.5em;
            }}

            .quiz-info {{
                flex-direction: column;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="quiz-container">
        <div class="quiz-header">
            <h1>{quiz.get('title', 'Quiz')}</h1>
            <div class="quiz-info">
                <div>📝 {len(questions)} Questions</div>
                <div>⏱️ {quiz.get('time_limit', 20)} Minutes</div>
                <div>✅ Passing Score: {quiz.get('passing_score', 70)}%</div>
            </div>
        </div>

        <div class="quiz-content" id="quizContent">
            <form id="quizForm">
                {questions_content}
            </form>
        </div>

        <div class="quiz-actions">
            <button type="button" class="btn btn-secondary" onclick="resetQuiz()">Reset</button>
            <button type="button" class="btn btn-primary" onclick="submitQuiz()">Submit Quiz</button>
        </div>

        <div class="results" id="results">
            <!-- Results will be inserted here -->
        </div>
    </div>

    <script>
        const quizData = {json.dumps(quiz_data)};

        function submitQuiz() {{
            const form = document.getElementById('quizForm');
            const formData = new FormData(form);
            const userAnswers = {{}};

            // Collect answers
            quizData.quiz.questions.forEach(q => {{
                const qId = q.id;

                if (q.type === 'fill_blank') {{
                    userAnswers[qId] = formData.get(`q${{qId}}`);
                }} else {{
                    const selectedOption = formData.get(`q${{qId}}`);
                    userAnswers[qId] = selectedOption ? parseInt(selectedOption) : null;
                }}
            }});

            // Calculate score
            const result = calculateScore(userAnswers);
            displayResults(result);
        }}

        function calculateScore(userAnswers) {{
            const questions = quizData.quiz.questions;
            let totalPoints = 0;
            let earnedPoints = 0;
            const results = [];

            questions.forEach(q => {{
                const points = q.points || 1;
                totalPoints += points;

                const userAnswer = userAnswers[q.id];
                let isCorrect = false;

                if (q.type === 'fill_blank') {{
                    const acceptable = q.acceptable_answers || [q.correct_answer];
                    if (userAnswer) {{
                        isCorrect = acceptable.some(ans =>
                            ans.toLowerCase().trim() === userAnswer.toLowerCase().trim()
                        );
                    }}
                }} else {{
                    isCorrect = userAnswer === q.correct_answer;
                }}

                if (isCorrect) {{
                    earnedPoints += points;
                }}

                results.push({{
                    questionId: q.id,
                    question: q.question,
                    correct: isCorrect,
                    userAnswer: userAnswer,
                    correctAnswer: q.correct_answer,
                    explanation: q.explanation || '',
                    options: q.options || []
                }});
            }});

            const percentage = (earnedPoints / totalPoints * 100).toFixed(2);
            const passed = percentage >= quizData.quiz.passing_score;

            return {{
                totalQuestions: questions.length,
                totalPoints,
                earnedPoints,
                percentage,
                passed,
                results
            }};
        }}

        function displayResults(result) {{
            const resultsDiv = document.getElementById('results');
            const quizContent = document.getElementById('quizContent');

            quizContent.style.display = 'none';
            document.querySelector('.quiz-actions').style.display = 'none';

            const statusClass = result.passed ? 'passed' : 'failed';
            const statusIcon = result.passed ? '🎉' : '😔';
            const statusText = result.passed ? 'Passed!' : 'Not Passed';

            let resultsHTML = `
                <div class="score-display ${{statusClass}}">
                    <div style="font-size: 4em; margin-bottom: 10px;">${{statusIcon}}</div>
                    <h2>${{result.percentage}}%</h2>
                    <p style="font-size: 1.2em;">${{statusText}}</p>
                    <p style="margin-top: 15px; opacity: 0.9;">
                        ${{result.earnedPoints}} / ${{result.totalPoints}} points
                    </p>
                </div>

                <h3 style="margin-bottom: 20px;">Detailed Results</h3>
            `;

            result.results.forEach((r, index) => {{
                const resultClass = r.correct ? 'result-correct' : 'result-incorrect';
                const resultIcon = r.correct ? '✅' : '❌';

                let answerDisplay = '';
                if (r.options && r.options.length > 0) {{
                    answerDisplay = `
                        <p><strong>Your answer:</strong> ${{r.options[r.userAnswer] || 'Not answered'}}</p>
                        <p><strong>Correct answer:</strong> ${{r.options[r.correctAnswer]}}</p>
                    `;
                }} else {{
                    answerDisplay = `
                        <p><strong>Your answer:</strong> ${{r.userAnswer || 'Not answered'}}</p>
                        <p><strong>Correct answer:</strong> ${{r.correctAnswer}}</p>
                    `;
                }}

                resultsHTML += `
                    <div class="result-item ${{resultClass}}">
                        <div style="display: flex; align-items: start; gap: 10px;">
                            <span style="font-size: 1.5em;">${{resultIcon}}</span>
                            <div style="flex: 1;">
                                <p style="font-weight: bold; margin-bottom: 10px;">
                                    Question ${{index + 1}}: ${{r.question}}
                                </p>
                                ${{answerDisplay}}
                                ${{r.explanation ? `
                                    <div class="explanation">
                                        <strong>💡 Explanation:</strong> ${{r.explanation}}
                                    </div>
                                ` : ''}}
                            </div>
                        </div>
                    </div>
                `;
            }});

            resultsHTML += `
                <div style="text-align: center; margin-top: 30px;">
                    <button class="btn btn-primary" onclick="location.reload()">Take Quiz Again</button>
                    <button class="btn btn-secondary" onclick="window.close()">Close</button>
                </div>
            `;

            resultsDiv.innerHTML = resultsHTML;
            resultsDiv.classList.add('show');
        }}

        function resetQuiz() {{
            if (confirm('Are you sure you want to reset the quiz?')) {{
                document.getElementById('quizForm').reset();
            }}
        }}
    </script>
</body>
</html>
"""
        return html

    def _generate_question_html(self, question: Dict) -> str:
        """Generates HTML for a single question"""

        q_id = question.get("id", 1)
        q_type = question.get("type", "mcq")
        q_text = question.get("question", "")
        difficulty = question.get("difficulty", "medium")

        difficulty_class = f"difficulty-{difficulty}"

        html = f"""
        <div class="question">
            <div class="question-header">
                <span class="question-number">Question {q_id}</span>
                <span class="question-difficulty {difficulty_class}">{difficulty}</span>
            </div>
            <div class="question-text">{q_text}</div>
        """

        if q_type in ["mcq", "true_false"]:
            options = question.get("options", [])
            html += '<ul class="options">'
            for i, option in enumerate(options):
                html += f"""
                <li class="option">
                    <label>
                        <input type="radio" name="q{q_id}" value="{i}">
                        {option}
                    </label>
                </li>
                """
            html += '</ul>'

        elif q_type == "fill_blank":
            html += f'<input type="text" name="q{q_id}" class="fill-blank-input" placeholder="Type your answer here...">'

        html += '</div>'
        return html

    def _generate_course_viewer(
        self,
        course_title: str,
        slides_file: str,
        quiz_file: str,
        course_structure: Dict,
        quiz_data: Dict
    ) -> str:
        """Generates course viewer that combines slides and quiz"""

        course = course_structure.get("course", {})
        chapters = course.get("chapters", [])

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{course_title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 2em;
            margin-bottom: 5px;
        }}

        .header p {{
            opacity: 0.9;
        }}

        .container {{
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 20px;
        }}

        .course-info {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .course-info h2 {{
            color: #667eea;
            margin-bottom: 15px;
        }}

        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .info-item {{
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            text-align: center;
        }}

        .info-item strong {{
            display: block;
            color: #667eea;
            margin-bottom: 5px;
        }}

        .chapters-list {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .chapters-list h2 {{
            color: #667eea;
            margin-bottom: 20px;
        }}

        .chapter-item {{
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 5px;
        }}

        .chapter-item strong {{
            color: #333;
        }}

        .actions {{
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
        }}

        .btn {{
            padding: 15px 40px;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s;
        }}

        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}

        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }}

        .btn-secondary {{
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }}

        .btn-secondary:hover {{
            background: #667eea;
            color: white;
        }}

        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.5em;
            }}

            .info-grid {{
                grid-template-columns: 1fr;
            }}

            .actions {{
                flex-direction: column;
            }}

            .btn {{
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{course_title}</h1>
        <p>{course.get('description', '')}</p>
    </div>

    <div class="container">
        <div class="course-info">
            <h2>📚 Course Overview</h2>
            <div class="info-grid">
                <div class="info-item">
                    <strong>Duration</strong>
                    {course.get('duration', 'N/A')}
                </div>
                <div class="info-item">
                    <strong>Difficulty</strong>
                    {course.get('difficulty', 'N/A').capitalize()}
                </div>
                <div class="info-item">
                    <strong>Chapters</strong>
                    {len(chapters)}
                </div>
                <div class="info-item">
                    <strong>Quiz Questions</strong>
                    {len(quiz_data.get('quiz', {}).get('questions', []))}
                </div>
            </div>
        </div>

        <div class="chapters-list">
            <h2>📖 Course Content</h2>
            {"".join([f'<div class="chapter-item"><strong>Chapter {ch.get("number")}:</strong> {ch.get("title")} <span style="color: #667eea;">({ch.get("duration", "N/A")})</span></div>' for ch in chapters])}
        </div>

        <div class="actions">
            <a href="{slides_file}" class="btn btn-primary" target="_blank">
                📊 Start Course (View Slides)
            </a>
            <a href="{quiz_file}" class="btn btn-secondary" target="_blank">
                ✏️ Take Quiz
            </a>
        </div>

        <div class="footer">
            <p>🤖 Generated with AI Course Creation Platform</p>
            <p>Created: {datetime.now().strftime("%B %d, %Y")}</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def export_to_zip(self, course_id: str) -> Optional[str]:
        """
        Exports course to ZIP file

        Args:
            course_id: Course identifier

        Returns:
            Path to ZIP file or None
        """

        course_dir = os.path.join(self.output_dir, course_id)

        if not os.path.exists(course_dir):
            print(f"Course directory not found: {course_dir}")
            return None

        zip_path = f"{course_dir}.zip"

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(course_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.output_dir)
                        zipf.write(file_path, arcname)

            print(f"Course exported to: {zip_path}")
            return zip_path

        except Exception as e:
            print(f"Error creating ZIP: {str(e)}")
            return None


# Helper function
def create_course_package(
    course_structure: Dict,
    slides_html: str,
    quiz_data: Dict,
    course_id: str,
    metadata: Optional[Dict] = None
) -> Dict:
    """
    Convenience function to create course package

    Args:
        course_structure: From CourseStructurer
        slides_html: From SlideGenerator
        quiz_data: From QuizGenerator
        course_id: Unique identifier
        metadata: Optional metadata

    Returns:
        Package info dict
    """
    assembler = CourseAssembler()
    return assembler.assemble_course(
        course_structure,
        slides_html,
        quiz_data,
        course_id,
        metadata
    )


if __name__ == "__main__":
    print("Course Assembler module loaded successfully!")
    print("Use create_course_package() to assemble a complete course.")
