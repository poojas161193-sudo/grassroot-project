"""
Slide Generator
Creates professional HTML-based slide decks from course structure
Uses Reveal.js framework
"""

import json
from typing import Dict, List, Optional
from jinja2 import Template
from datetime import datetime


class SlideGenerator:
    """
    Generates professional slide decks from course structure
    """

    def __init__(self, theme: str = "light"):
        """
        Args:
            theme: "light", "dark", or "corporate"
        """
        self.theme = theme
        self.theme_colors = self._get_theme_colors(theme)

    def _get_theme_colors(self, theme: str) -> Dict:
        """Returns color scheme for the selected theme"""
        themes = {
            "light": {
                "primary": "#2c3e50",
                "secondary": "#3498db",
                "accent": "#e74c3c",
                "background": "#ffffff",
                "text": "#333333",
                "heading": "#2c3e50"
            },
            "dark": {
                "primary": "#ecf0f1",
                "secondary": "#3498db",
                "accent": "#e67e22",
                "background": "#1a1a1a",
                "text": "#ecf0f1",
                "heading": "#ffffff"
            },
            "corporate": {
                "primary": "#0066cc",
                "secondary": "#00cc66",
                "accent": "#ff9900",
                "background": "#f8f9fa",
                "text": "#333333",
                "heading": "#0066cc"
            }
        }
        return themes.get(theme, themes["light"])

    def create_slide_deck(
        self,
        course_data: Dict,
        language: str = "en"
    ) -> str:
        """
        Creates complete HTML slide deck from course structure

        Args:
            course_data: Course structure from CourseStructurer
            language: Language code

        Returns:
            Complete HTML string for slide deck
        """

        course = course_data.get("course", {})

        # Build slides
        slides_html = []

        # 1. Title slide
        slides_html.append(self._create_title_slide(course, language))

        # 2. Table of contents
        slides_html.append(self._create_toc_slide(course, language))

        # 3. Chapter slides
        for chapter in course.get("chapters", []):
            # Chapter title slide
            slides_html.append(self._create_chapter_title_slide(chapter))

            # Learning objectives slide
            slides_html.append(self._create_objectives_slide(chapter))

            # Content slides
            content_slides = self._create_content_slides(chapter)
            slides_html.extend(content_slides)

            # Chapter summary slide
            slides_html.append(self._create_chapter_summary_slide(chapter))

        # 4. Final summary slide
        slides_html.append(self._create_final_summary_slide(course, language))

        # Combine all slides
        all_slides = "\n\n".join(slides_html)

        # Wrap in Reveal.js template
        full_html = self._wrap_in_template(all_slides, course, language)

        return full_html

    def _create_title_slide(self, course: Dict, language: str) -> str:
        """Creates the title slide"""

        duration = course.get("duration", "")
        difficulty = course.get("difficulty", "intermediate")

        labels = {
            "en": {
                "duration": "Duration",
                "difficulty": "Difficulty",
                "beginner": "Beginner",
                "intermediate": "Intermediate",
                "advanced": "Advanced"
            },
            "ja": {
                "duration": "期間",
                "difficulty": "難易度",
                "beginner": "初級",
                "intermediate": "中級",
                "advanced": "上級"
            }
        }

        lang = labels.get(language, labels["en"])
        difficulty_text = lang.get(difficulty, difficulty)

        html = f"""
        <section data-transition="zoom" style="text-align: center;">
            <div style="background: linear-gradient(135deg, {self.theme_colors['primary']} 0%, {self.theme_colors['secondary']} 100%);
                        padding: 30px 40px; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        display: inline-block; max-width: 90%;">
                <h1 style="color: white; font-size: 1.8em; margin: 0; line-height: 1.3;">{course.get('title', 'Course Title')}</h1>
            </div>
            <p style="font-size: 0.95em; margin-top: 30px; line-height: 1.5; max-width: 80%; margin-left: auto; margin-right: auto;">
                {course.get('description', '')}
            </p>
            <div style="margin-top: 40px; display: inline-flex; gap: 40px; font-size: 0.85em;
                        background: rgba(0,0,0,0.03); padding: 20px 40px; border-radius: 10px;">
                <div style="text-align: center;">
                    <div style="font-size: 2em; margin-bottom: 5px;">⏱️</div>
                    <div style="color: {self.theme_colors['secondary']}; font-weight: bold;">{duration}</div>
                    <div style="font-size: 0.85em; color: #666; margin-top: 3px;">{lang['duration']}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2em; margin-bottom: 5px;">📊</div>
                    <div style="color: {self.theme_colors['secondary']}; font-weight: bold;">{difficulty_text}</div>
                    <div style="font-size: 0.85em; color: #666; margin-top: 3px;">{lang['difficulty']}</div>
                </div>
            </div>
            <p style="margin-top: 50px; font-size: 0.75em; color: #999;">
                {datetime.now().strftime("%B %Y")}
            </p>
        </section>
        """
        return html

    def _create_toc_slide(self, course: Dict, language: str) -> str:
        """Creates table of contents slide"""

        labels = {
            "en": "Table of Contents",
            "ja": "目次"
        }
        title = labels.get(language, labels["en"])

        chapters = course.get("chapters", [])
        toc_items = []

        for chapter in chapters:
            chapter_num = chapter.get("number", "")
            chapter_title = chapter.get("title", "")
            duration = chapter.get("duration", "")
            toc_items.append(
                f'<li style="margin: 20px 0; padding: 15px 20px; background: linear-gradient(to right, rgba(52, 152, 219, 0.1) 0%, transparent 100%); '
                f'border-left: 4px solid {self.theme_colors["secondary"]}; border-radius: 5px;">'
                f'<div style="display: flex; justify-content: space-between; align-items: center;">'
                f'<div><span style="color: {self.theme_colors["secondary"]}; font-weight: bold; font-size: 1.3em; margin-right: 15px;">{chapter_num}</span>'
                f'<span style="font-size: 1.05em;">{chapter_title}</span></div>'
                f'<span style="color: {self.theme_colors["secondary"]}; font-size: 0.9em; font-weight: 600;">⏱️ {duration}</span>'
                f'</div></li>'
            )

        toc_html = "\n".join(toc_items)

        html = f"""
        <section>
            <h2 style="margin-bottom: 40px;">📚 {title}</h2>
            <ul style="text-align: left; list-style: none; padding: 0;">
                {toc_html}
            </ul>
        </section>
        """
        return html

    def _create_chapter_title_slide(self, chapter: Dict) -> str:
        """Creates chapter title slide"""

        chapter_num = chapter.get("number", "")
        title = chapter.get("title", "")
        duration = chapter.get("duration", "")

        html = f"""
        <section data-transition="slide" data-background="linear-gradient(135deg, {self.theme_colors['primary']} 0%, {self.theme_colors['secondary']} 100%)"
                 data-background-transition="zoom" style="text-align: center;">
            <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); padding: 40px 50px;
                        border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); display: inline-block;">
                <div style="color: rgba(255,255,255,0.9); font-size: 1em; font-weight: 600;
                           letter-spacing: 2px; margin-bottom: 20px;">CHAPTER {chapter_num}</div>
                <h2 style="color: white; font-size: 2.2em; margin: 0; line-height: 1.3;">{title}</h2>
                <div style="margin-top: 30px; color: rgba(255,255,255,0.85); font-size: 1em;">
                    <span style="background: rgba(255,255,255,0.2); padding: 8px 20px; border-radius: 20px;">
                        ⏱️ {duration}
                    </span>
                </div>
            </div>
        </section>
        """
        return html

    def _create_objectives_slide(self, chapter: Dict) -> str:
        """Creates learning objectives slide"""

        objectives = chapter.get("learning_objectives", [])

        obj_items = []
        for i, obj in enumerate(objectives, 1):
            obj_items.append(
                f'<li style="margin: 12px 0; padding: 12px 15px; background: linear-gradient(to right, rgba(52, 152, 219, 0.08) 0%, transparent 100%); '
                f'border-left: 4px solid {self.theme_colors["accent"]}; border-radius: 5px; list-style: none; font-size: 0.9em; line-height: 1.4;">'
                f'<span style="color: {self.theme_colors["accent"]}; font-weight: bold; margin-right: 10px;">✓</span>{obj}'
                f'</li>'
            )

        obj_html = "\n".join(obj_items)

        html = f"""
        <section>
            <h3 style="margin-bottom: 20px; margin-top: 10px;">🎯 Learning Objectives</h3>
            <ul style="text-align: left; padding: 0; margin-top: 0;">
                {obj_html}
            </ul>
        </section>
        """
        return html

    def _create_content_slides(self, chapter: Dict) -> List[str]:
        """Creates content slides from chapter content"""

        slides = []
        key_points = chapter.get("key_points", [])
        content = chapter.get("content", "")

        # Split key points into slides (max 6 points per slide for better readability)
        points_per_slide = 6

        for i in range(0, len(key_points), points_per_slide):
            slide_points = key_points[i:i + points_per_slide]

            point_items = []
            icons = ["💡", "🔑", "⭐", "📌", "✨", "🎯", "🚀"]  # Variety of icons
            for idx, point in enumerate(slide_points):
                icon = icons[idx % len(icons)]
                point_items.append(
                    f'<li style="margin: 12px 0; padding: 10px 15px; font-size: 0.85em; line-height: 1.4; '
                    f'background: linear-gradient(to right, rgba(52, 152, 219, 0.06) 0%, transparent 100%); '
                    f'border-left: 3px solid {self.theme_colors["secondary"]}; border-radius: 5px; list-style: none;">'
                    f'<span style="margin-right: 10px;">{icon}</span>{point}'
                    f'</li>'
                )

            points_html = "\n".join(point_items)

            # Add slide number indicator if multiple content slides
            slide_indicator = ""
            if len(key_points) > points_per_slide:
                slide_num = (i // points_per_slide) + 1
                total_slides = (len(key_points) + points_per_slide - 1) // points_per_slide
                slide_indicator = f'<div style="position: absolute; top: 20px; right: 20px; font-size: 0.7em; ' \
                                f'color: {self.theme_colors["secondary"]}; background: rgba(52, 152, 219, 0.1); ' \
                                f'padding: 5px 15px; border-radius: 15px;">Part {slide_num} of {total_slides}</div>'

            html = f"""
            <section>
                {slide_indicator}
                <h3 style="margin-bottom: 20px; margin-top: 10px;">{chapter.get('title', '')}</h3>
                <ul style="text-align: left; padding: 0; margin-top: 0;">
                    {points_html}
                </ul>
                <aside class="notes">
                    {content[:500]}
                </aside>
            </section>
            """
            slides.append(html)

        return slides

    def _create_chapter_summary_slide(self, chapter: Dict) -> str:
        """Creates chapter summary slide"""

        key_points = chapter.get("key_points", [])[:3]  # Top 3 points

        summary_items = []
        for i, point in enumerate(key_points, 1):
            summary_items.append(
                f'<li style="margin: 20px 0; padding: 18px 22px; background: linear-gradient(135deg, rgba(231, 76, 60, 0.08) 0%, rgba(52, 152, 219, 0.08) 100%); '
                f'border-left: 4px solid {self.theme_colors["accent"]}; border-radius: 8px; list-style: none; '
                f'box-shadow: 0 2px 8px rgba(0,0,0,0.05);">'
                f'<span style="color: {self.theme_colors["accent"]}; font-weight: bold; font-size: 1.2em; margin-right: 12px;">{i}</span>{point}'
                f'</li>'
            )

        summary_html = "\n".join(summary_items)

        html = f"""
        <section data-background="{self.theme_colors['background']}">
            <h3 style="margin-bottom: 40px;">🎁 Key Takeaways: {chapter.get('title', '')}</h3>
            <ul style="text-align: left; padding: 0; font-size: 0.95em;">
                {summary_html}
            </ul>
        </section>
        """
        return html

    def _create_final_summary_slide(self, course: Dict, language: str) -> str:
        """Creates final course summary slide"""

        labels = {
            "en": {
                "title": "Course Summary",
                "outcomes": "What You've Learned",
                "next": "Next Steps",
                "thanks": "Thank You!"
            },
            "ja": {
                "title": "コースのまとめ",
                "outcomes": "学んだこと",
                "next": "次のステップ",
                "thanks": "ありがとうございました！"
            }
        }

        lang = labels.get(language, labels["en"])
        outcomes = course.get("learning_outcomes", [])

        outcome_items = []
        for i, outcome in enumerate(outcomes, 1):
            outcome_items.append(
                f'<li style="margin: 18px 0; padding: 15px 20px; '
                f'background: linear-gradient(to right, rgba(52, 152, 219, 0.08) 0%, transparent 100%); '
                f'border-left: 4px solid {self.theme_colors["secondary"]}; border-radius: 5px; list-style: none;">'
                f'<span style="color: {self.theme_colors["secondary"]}; font-weight: bold; margin-right: 10px;">✓</span>{outcome}'
                f'</li>'
            )

        outcomes_html = "\n".join(outcome_items)

        html = f"""
        <section data-transition="zoom" style="text-align: center;">
            <div style="background: linear-gradient(135deg, {self.theme_colors['primary']} 0%, {self.theme_colors['secondary']} 100%);
                        padding: 25px 40px; border-radius: 15px; box-shadow: 0 8px 30px rgba(0,0,0,0.2);
                        display: inline-block; margin-bottom: 40px;">
                <h2 style="color: white; font-size: 1.8em; margin: 0;">🎓 {lang['title']}</h2>
            </div>
            <div style="margin-top: 30px; text-align: left; max-width: 85%; margin-left: auto; margin-right: auto;">
                <h3 style="margin-bottom: 25px;">✨ {lang['outcomes']}</h3>
                <ul style="padding: 0; font-size: 0.9em;">
                    {outcomes_html}
                </ul>
            </div>
            <div style="margin-top: 60px; padding: 25px 40px; background: linear-gradient(135deg, rgba(231, 76, 60, 0.1) 0%, rgba(52, 152, 219, 0.1) 100%);
                        border-radius: 15px; display: inline-block;">
                <p style="font-size: 1.6em; margin: 0; font-weight: 600; background: linear-gradient(135deg, {self.theme_colors['primary']} 0%, {self.theme_colors['accent']} 100%);
                          -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                    {lang['thanks']}
                </p>
            </div>
        </section>
        """
        return html

    def _wrap_in_template(self, slides_html: str, course: Dict, language: str) -> str:
        """Wraps slides in complete Reveal.js HTML template"""

        template = f"""
<!DOCTYPE html>
<html lang="{language}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{course.get('title', 'Course')}</title>

    <!-- Reveal.js CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/theme/white.css" id="theme">

    <!-- Custom CSS -->
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Poppins:wght@600;700&display=swap');

        :root {{
            --primary-color: {self.theme_colors['primary']};
            --secondary-color: {self.theme_colors['secondary']};
            --accent-color: {self.theme_colors['accent']};
            --background-color: {self.theme_colors['background']};
            --text-color: {self.theme_colors['text']};
            --heading-color: {self.theme_colors['heading']};
        }}

        .reveal {{
            background-color: var(--background-color);
            color: var(--text-color);
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 28px;
        }}

        .reveal h1, .reveal h2, .reveal h3, .reveal h4 {{
            color: var(--heading-color);
            font-family: 'Poppins', 'Inter', sans-serif;
            font-weight: 700;
            text-transform: none;
            letter-spacing: -0.5px;
        }}

        .reveal h1 {{
            font-size: 2.2em;
            line-height: 1.2;
        }}

        .reveal h2 {{
            font-size: 1.8em;
            line-height: 1.3;
        }}

        .reveal h3 {{
            font-size: 1.4em;
            line-height: 1.4;
        }}

        .reveal p {{
            line-height: 1.6;
            margin: 20px 0;
        }}

        .reveal a {{
            color: var(--secondary-color);
            text-decoration: none;
            transition: all 0.3s ease;
        }}

        .reveal a:hover {{
            color: var(--accent-color);
            text-decoration: underline;
        }}

        .reveal .progress {{
            background: rgba(0,0,0,0.15);
            height: 4px;
        }}

        .reveal .progress span {{
            background: linear-gradient(90deg, var(--secondary-color) 0%, var(--accent-color) 100%);
            transition: width 0.8s ease;
        }}

        .reveal .controls {{
            color: var(--secondary-color);
            right: 20px;
            bottom: 20px;
        }}

        .reveal .controls button {{
            opacity: 0.7;
            transition: opacity 0.3s ease;
        }}

        .reveal .controls button:hover {{
            opacity: 1;
        }}

        .reveal .slide-number {{
            background-color: rgba(0, 0, 0, 0.05);
            color: var(--text-color);
            padding: 5px 12px;
            border-radius: 4px;
            font-size: 0.6em;
            font-weight: 600;
        }}

        .reveal ul {{
            line-height: 1.4;
        }}

        .reveal li {{
            margin: 8px 0;
        }}

        .reveal section {{
            text-align: left;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .reveal section[style*="text-align: center"] {{
            text-align: center !important;
        }}

        /* Animations */
        .reveal .slides section {{
            transition: all 0.5s ease;
        }}

        /* Print styles */
        @media print {{
            .reveal {{
                background-color: white;
                font-size: 12pt;
            }}
            .reveal h1, .reveal h2, .reveal h3 {{
                color: black;
            }}
            .reveal .controls, .reveal .progress, .reveal .slide-number {{
                display: none !important;
            }}
        }}

        /* Responsive adjustments */
        @media (max-width: 1920px) {{
            .reveal {{
                font-size: 26px;
            }}
        }}

        @media (max-width: 1600px) {{
            .reveal {{
                font-size: 24px;
            }}
        }}

        @media (max-width: 768px) {{
            .reveal {{
                font-size: 22px;
            }}
            .reveal h1 {{
                font-size: 1.8em;
            }}
            .reveal h2 {{
                font-size: 1.5em;
            }}
            .reveal h3 {{
                font-size: 1.2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
            {slides_html}
        </div>
    </div>

    <!-- Reveal.js JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/plugin/notes/notes.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/plugin/highlight/highlight.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/plugin/zoom/zoom.js"></script>

    <script>
        // Initialize Reveal.js
        Reveal.initialize({{
            hash: true,
            controls: true,
            progress: true,
            center: true,
            transition: 'slide',
            slideNumber: true,

            // Plugins
            plugins: [ RevealNotes, RevealHighlight, RevealZoom ]
        }});
    </script>
</body>
</html>
"""
        return template

    def apply_theme(self, theme: str):
        """Changes the theme"""
        self.theme = theme
        self.theme_colors = self._get_theme_colors(theme)

    def export_html(self, slides_html: str, output_path: str):
        """
        Exports slides to HTML file

        Args:
            slides_html: Generated HTML slides
            output_path: File path to save HTML
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(slides_html)
            print(f"Slides exported to: {output_path}")
            return True
        except Exception as e:
            print(f"Error exporting slides: {str(e)}")
            return False


# Helper function
def generate_slides(course_data: Dict, theme: str = "light", language: str = "en") -> str:
    """
    Convenience function to generate slides

    Args:
        course_data: Course structure from CourseStructurer
        theme: "light", "dark", or "corporate"
        language: Language code

    Returns:
        Complete HTML slide deck
    """
    generator = SlideGenerator(theme=theme)
    return generator.create_slide_deck(course_data, language)


if __name__ == "__main__":
    # Test with sample course data
    sample_course = {
        "course": {
            "title": "Introduction to Python Programming",
            "description": "Learn the fundamentals of Python programming from scratch",
            "duration": "3 hours",
            "difficulty": "beginner",
            "learning_outcomes": [
                "Write basic Python programs",
                "Understand variables and data types",
                "Use control flow statements"
            ],
            "chapters": [
                {
                    "number": 1,
                    "title": "Getting Started with Python",
                    "duration": "30 mins",
                    "learning_objectives": [
                        "Understand what Python is",
                        "Install Python on your system"
                    ],
                    "key_points": [
                        "Python is a high-level programming language",
                        "Python is interpreted, not compiled",
                        "Python uses indentation for code blocks"
                    ],
                    "content": "Python is one of the most popular programming languages..."
                },
                {
                    "number": 2,
                    "title": "Variables and Data Types",
                    "duration": "45 mins",
                    "learning_objectives": [
                        "Declare and use variables",
                        "Work with different data types"
                    ],
                    "key_points": [
                        "Variables store data values",
                        "Python has dynamic typing",
                        "Common types: int, float, string, bool"
                    ],
                    "content": "In Python, variables are created when you assign a value..."
                }
            ]
        }
    }

    generator = SlideGenerator(theme="light")
    html = generator.create_slide_deck(sample_course, language="en")

    # Save to file for testing
    generator.export_html(html, "test_slides.html")
    print("Test slides generated!")
