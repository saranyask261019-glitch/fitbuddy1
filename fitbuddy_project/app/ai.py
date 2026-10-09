"""Gemini integration with a deterministic demo fallback when no API key is configured."""
import os
from google import genai
from google.genai import types

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
WORKOUT_MODEL = os.getenv("GEMINI_WORKOUT_MODEL", "gemini-2.5-flash")
TIP_MODEL = os.getenv("GEMINI_TIP_MODEL", "gemini-2.5-flash")
_client = genai.Client(api_key=API_KEY) if API_KEY else None

def _generate(prompt: str, model: str) -> str:
    if _client is None:
        raise RuntimeError("Gemini API key is not configured.")
    response = _client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.5),
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("The AI provider returned an empty response.")
    return text

def demo_workout(username: str, goal: str, intensity: str) -> str:
    effort = {"low": "2 sets of 8–10 comfortable repetitions",
              "medium": "3 sets of 8–12 controlled repetitions",
              "high": "3 sets of 10–12 controlled repetitions; stop before form breaks"}[intensity]
    days = [
        ("Day 1 — Full body", "Chair squats, wall push-ups, glute bridges, bird-dogs"),
        ("Day 2 — Cardio", "Brisk walking or easy cycling"),
        ("Day 3 — Mobility", "Gentle hip, shoulder, and ankle mobility; easy stretching"),
        ("Day 4 — Strength", "Supported lunges, rows with a light bag, calf raises, dead bugs"),
        ("Day 5 — Cardio and core", "Comfortable walking intervals, bird-dogs, standing marches"),
        ("Day 6 — Flexibility", "Gentle full-body mobility and relaxed stretching"),
        ("Day 7 — Recovery", "Rest, or an easy walk if it feels comfortable"),
    ]
    lines = [f"Personalized starter plan for {username}", f"Goal: {goal} | Intensity: {intensity}",
             "", "Begin each active session with 5–10 minutes of gentle warm-up. Keep movements pain-free."]
    for day, exercises in days:
        lines.extend(["", day, f"Warm-up: easy marching and joint circles for 5–10 minutes.",
                      f"Main session: {exercises}. For strength moves, start with {effort}.",
                      "Cool-down: slow breathing and gentle stretching for 3–5 minutes."])
    lines.extend(["", "Safety: this is general wellness information, not medical advice. Adjust to your ability,",
                  "take rest when needed, and consult a qualified professional if you have health concerns."])
    return "\n".join(lines)

def generate_workout(username: str, age: int, weight: float, goal: str, intensity: str) -> str:
    prompt = f"""Create a safe, practical 7-day beginner-friendly fitness plan.
Name: {username}; age: {age}; weight kg: {weight}; goal: {goal}; preferred intensity: {intensity}.
For each day include focus, warm-up, exercises with sets/reps or duration, and cool-down/recovery.
Include rest or active recovery. Scale intensity appropriately; avoid extreme dieting or unsafe claims.
Do not diagnose, promise weight loss, or prescribe treatment. State that exercises should be pain-free.
Use clear plain text headings for Day 1 through Day 7."""
    try:
        return _generate(prompt, WORKOUT_MODEL)
    except (RuntimeError, Exception):
        if not API_KEY:
            return demo_workout(username, goal, intensity)
        raise

def generate_nutrition_tip(goal: str) -> str:
    prompt = f"""Give one concise, safe nutrition or recovery tip for the fitness goal: {goal}.
Use general balanced-eating and hydration guidance. Avoid calorie prescriptions, supplements, and medical claims.
Keep it to 2–4 sentences and note that individual needs vary."""
    try:
        return _generate(prompt, TIP_MODEL)
    except Exception:
        if not API_KEY:
            tips = {
                "muscle gain": "Include a source of protein such as beans, lentils, eggs, dairy, tofu, fish, or chicken in balanced meals. Eat enough overall and allow recovery time.",
                "cardio fitness": "Drink water regularly and include balanced meals with carbohydrates, protein, fruits, and vegetables to support activity and recovery.",
                "flexibility": "Stay hydrated and eat a varied, balanced diet. Gentle movement, sufficient sleep, and rest support recovery.",
                "strength": "Include protein-rich foods and a variety of whole foods in regular meals. Give trained muscles time to recover.",
                "general wellness": "Aim for regular balanced meals, a variety of fruits and vegetables, and water throughout the day. Your needs may vary with activity and health."
            }
            return tips.get(goal, tips["general wellness"])
        raise

def update_workout(original_plan: str, feedback: str, goal: str, intensity: str) -> str:
    prompt = f"""Revise this 7-day workout plan using the user's feedback.
Goal: {goal}; preferred intensity: {intensity}.
Feedback: {feedback}
Original plan:
{original_plan}
Keep it practical and safe, include rest/recovery, and do not recommend exercising through pain.
Return the complete revised 7-day plan in plain text."""
    try:
        return _generate(prompt, WORKOUT_MODEL)
    except Exception:
        if not API_KEY:
            return original_plan + "\n\nDEMO UPDATE NOTE\nRequested feedback: " + feedback + (
                "\nThis demo environment preserves the original plan. Configure GEMINI_API_KEY to receive an AI-revised plan.")
        raise
