import json
import os
from datetime import datetime
from ai_helper import ask_ai

# Initialize session data file
SESSION_FILE = "sessions.json"

def load_sessions():
    """Load all sessions from JSON file"""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as f:
            return json.load(f)
    return {}

def save_sessions(sessions):
    """Save sessions to JSON file"""
    with open(SESSION_FILE, "w") as f:
        json.dump(sessions, f, indent=2)

# Stage 1: Writing Analysis
def analyze_writing(spanish_text: str) -> str:
    """AI Call 1: Analyze user's Spanish writing"""
    prompt = f"""Analyze the following Spanish text for grammar, vocabulary, and style.
Provide constructive feedback in Spanish.

Spanish text:
{spanish_text}

Please provide:
1. Grammar corrections
2. Vocabulary suggestions
3. Writing improvements"""

    return ask_ai(prompt)

# Stage 2: Reading Exercise Creation
def create_reading_exercise(spanish_text: str, analysis: str) -> dict:
    """AI Call 2: Create interactive reading exercise with word metadata"""
    prompt = f"""Based on this Spanish text and analysis, create an interactive reading exercise.

Original text:
{spanish_text}

Analysis:
{analysis}

For the reading exercise, provide:
1. A refined version of the text
2. A JSON with word metadata containing: word, definition (English), tense/grammar form, unconjugated form

Format your response as JSON with keys: "text" and "words"
Words should be an array of objects with keys: word, definition, tense, unconjugated"""

    response = ask_ai(prompt)
    try:
        # Extract JSON from response
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            return json.loads(response[json_start:json_end])
    except json.JSONDecodeError:
        pass

    return {"text": spanish_text, "words": []}

# Stage 3: Exercise Generation
def generate_exercises(text: str, word_data: dict) -> str:
    """AI Call 3: Generate exercises based on reading"""
    prompt = f"""Create Spanish learning exercises based on this reading:

Text:
{text}

Word metadata:
{json.dumps(word_data, ensure_ascii=False)}

Generate 5 different types of exercises:
1. Comprehension questions (in Spanish)
2. Fill-in-the-blank sentences
3. Vocabulary matching
4. Grammar practice
5. Translation exercises

Format each clearly with exercise type and instructions."""

    return ask_ai(prompt)

# Stage 4: Exercise Checking
def check_exercises(exercises_text: str, user_answers: str) -> str:
    """AI Call 4: Check user's exercise responses and provide feedback"""
    prompt = f"""Check these Spanish exercise responses and provide detailed feedback.

Exercises:
{exercises_text}

User's answers:
{user_answers}

For each answer, provide:
1. Correctness (✓ or ✗)
2. Explanation in Spanish
3. Grammar notes if applicable
4. Overall score and recommendations"""

    return ask_ai(prompt)

# Main pipeline
def run_spanish_learning_pipeline(spanish_input: str, user_answers: str = None) -> dict:
    """Run the complete 4-stage pipeline"""

    # Create session ID
    session_id = datetime.now().isoformat()
    sessions = load_sessions()

    session = {
        "id": session_id,
        "timestamp": session_id,
        "input": spanish_input,
        "stages": {}
    }

    print("🔄 Stage 1: Analyzing your Spanish writing...")
    analysis = analyze_writing(spanish_input)
    session["stages"]["analysis"] = analysis

    print("🔄 Stage 2: Creating reading exercise...")
    reading_exercise = create_reading_exercise(spanish_input, analysis)
    session["stages"]["reading_exercise"] = reading_exercise

    print("🔄 Stage 3: Generating exercises...")
    exercises = generate_exercises(reading_exercise.get("text", spanish_input), reading_exercise.get("words", []))
    session["stages"]["exercises"] = exercises

    if user_answers:
        print("🔄 Stage 4: Checking your exercises...")
        feedback = check_exercises(exercises, user_answers)
        session["stages"]["feedback"] = feedback

    # Save session
    sessions[session_id] = session
    save_sessions(sessions)

    return session

if __name__ == "__main__":
    # Example usage
    sample_text = "Yo como una manzana en el parque cada día. El parque es muy bonito y hay muchos árboles."

    print("Starting Spanish Learning Pipeline...\n")
    result = run_spanish_learning_pipeline(sample_text)

    print("\n✅ Pipeline Complete!")
    print(f"Session ID: {result['id']}")
