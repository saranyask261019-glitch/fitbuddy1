from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from .ai import generate_nutrition_tip, generate_workout, update_workout
from .database import get_db
from .models import User, WorkoutPlan
from .schemas import UserInput, FeedbackRequest

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def _page(request: Request, name: str, context: dict, status_code: int = 200):
    return templates.TemplateResponse(request=request, name=name, context=context, status_code=status_code)

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return _page(request, "index.html", {"error": None})

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout_route(
    request: Request,
    username: str = Form(...), user_id: str = Form(...), age: int = Form(...),
    weight: float = Form(...), goal: str = Form(...), intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(username=username, user_id=user_id, age=age, weight=weight, goal=goal, intensity=intensity)
    except Exception as exc:
        return _page(request, "index.html", {"error": str(exc)}, 422)
    user = db.scalar(select(User).where(User.user_id == data.user_id))
    if user is None:
        user = User(user_id=data.user_id, username=data.username, age=data.age, weight=data.weight,
                    goal=data.goal, intensity=data.intensity)
        db.add(user)
    else:
        user.username, user.age, user.weight = data.username, data.age, data.weight
        user.goal, user.intensity = data.goal, data.intensity
    try:
        plan = generate_workout(data.username, data.age, data.weight, data.goal, data.intensity)
        tip = generate_nutrition_tip(data.goal)
    except Exception:
        db.rollback()
        return _page(request, "index.html",
                     {"error": "AI service is unavailable. Check your Gemini API key and try again."}, 502)
    db.add(WorkoutPlan(user_id=data.user_id, original_plan=plan, nutrition_tip=tip))
    db.commit()
    return _page(request, "result.html", {"user": user, "workout_plan": plan, "nutrition_tip": tip,
                                          "updated": False, "feedback_message": None})

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request, user_id: str = Form(...), feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = FeedbackRequest(user_id=user_id, feedback=feedback)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    user = db.scalar(select(User).where(User.user_id == data.user_id))
    plan_record = db.scalar(select(WorkoutPlan).where(WorkoutPlan.user_id == data.user_id)
                             .order_by(WorkoutPlan.id.desc()))
    if not user or not plan_record:
        raise HTTPException(status_code=404, detail="User or workout plan not found. Generate a plan first.")
    try:
        revised = update_workout(plan_record.updated_plan or plan_record.original_plan,
                                 data.feedback, user.goal, user.intensity)
        tip = generate_nutrition_tip(user.goal)
    except Exception:
        raise HTTPException(status_code=502, detail="AI service is unavailable. Check your Gemini API key.")
    plan_record.updated_plan = revised
    plan_record.latest_feedback = data.feedback
    plan_record.nutrition_tip = tip
    db.commit()
    return _page(request, "result.html", {"user": user, "workout_plan": revised, "nutrition_tip": tip,
                                          "updated": True, "feedback_message": "Your plan has been updated."})

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.id.desc())).all()
    plans = db.scalars(select(WorkoutPlan).order_by(WorkoutPlan.id.desc())).all()
    latest_by_user = {}
    for plan in plans:
        latest_by_user.setdefault(plan.user_id, plan)
    return _page(request, "all_users.html", {"users": users, "plans_by_user": latest_by_user})

# JSON endpoints are available for API clients and can be explored at /docs.
@router.get("/api/health")
def health():
    return {"status": "ok", "service": "FitBuddy"}

@router.get("/api/users")
def api_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.id.desc())).all()
    return [{"user_id": u.user_id, "username": u.username, "age": u.age, "weight": u.weight,
             "goal": u.goal, "intensity": u.intensity} for u in users]
