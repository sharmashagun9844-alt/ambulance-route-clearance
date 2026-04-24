import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .environment import AmbulanceRouteEnv
from .models import AmbulanceAction, AmbulanceObservation
app = FastAPI(
    title="Ambulance Route Clearance Environment",
    description="AI agent controls traffic signals to clear ambulance routes",
    version="1.0.0"
)
env = AmbulanceRouteEnv()
@app.post("/reset")
def reset(task_id: int = 1):
    obs = env.reset(task_id=task_id)
    return obs.model_dump()
@app.post("/step")
def step(action: AmbulanceAction):
    obs = env.step(action)
    return obs.model_dump()
@app.get("/state")
def state():
    return env.state.model_dump()
@app.get("/")
def root():
    return {
        "name": "Ambulance Route Clearance Environment",
        "team": "The Fine-Tuners",
        "version": "1.0.0",
        "status": "ok",
        "description": "AI agent controls traffic signals to clear ambulance routes"
    }
@app.get("/tasks")
def tasks():
    """Returns all tasks and action schema for judges"""
    return {
        "tasks": [
            {
                "id": 1,
                "name": "Single Signal Clear",
                "difficulty": "easy",
                "description": "Clear 1 red signal with light traffic",
                "max_steps": 20
            },
            {
                "id": 2,
                "name": "Full Route Optimization",
                "difficulty": "medium",
                "description": "Clear 3 signals across full route with moderate traffic",
                "max_steps": 20
            },
            {
                "id": 3,
                "name": "Multi-Ambulance Emergency",
                "difficulty": "hard",
                "description": "2 ambulances, heavy traffic, 1 road blocked",
                "max_steps": 20
            }
        ],
        "action_schema": {
            "signal_id": "int — ID of signal to control",
            "new_status": "str — 'green' to clear, 'red' to block",
            "reroute": "bool — True to reroute ambulance around blocked road"
        }
    }
@app.get("/grader")
def grader():
    """Returns score after episode completes"""
    reached = env._ambulance_reached
    steps = env._step_count

    if reached and steps <= 5:
        score = 1.0
    elif reached and steps <= 10:
        score = 0.8
    elif reached:
        score = 0.6
    else:
        score = 0.2

    return {
        "task_id": env._task_id,
        "score": score,
        "ambulance_reached": reached,
        "steps_taken": steps,
        "feedback": _get_feedback(score, reached)
    }
@app.get("/baseline")
def baseline():
    """Runs baseline rule-based agent on all 3 tasks"""
    results = {}
    total = 0.0

    baseline_actions = {
        1: [{"signal_id": 1, "new_status": "green", "reroute": False}],
        2: [
            {"signal_id": 1, "new_status": "green", "reroute": False},
            {"signal_id": 2, "new_status": "green", "reroute": False},
            {"signal_id": 3, "new_status": "green", "reroute": False},
        ],
        3: [
            {"signal_id": 1, "new_status": "green", "reroute": False},
            {"signal_id": 2, "new_status": "green", "reroute": True},
            {"signal_id": 3, "new_status": "green", "reroute": False},
            {"signal_id": 4, "new_status": "green", "reroute": False},
        ]
    }
    for task_id in [1, 2, 3]:
        test_env = AmbulanceRouteEnv()
        test_env.reset(task_id=task_id)
        total_reward = 0.0

        for action_data in baseline_actions[task_id]:
            from .models import AmbulanceAction
            action = AmbulanceAction(**action_data)
            obs = test_env.step(action)
            total_reward += obs.reward
            if obs.done:
                break
        score = round(min(total_reward / 1.5, 1.0), 2)
        results[f"task_{task_id}"] = {
            "score": score,
            "reached": test_env._ambulance_reached,
            "steps": test_env._step_count
        }
        total += score
    results["overall_score"] = round(total / 3, 2)
    return results

def _get_feedback(score: float, reached: bool) -> str:
    if score >= 0.9:
        return "Excellent! Optimal route cleared."
    elif score >= 0.7:
        return "Good. Ambulance reached but could be faster."
    elif score >= 0.5:
        return "Partial. Some signals cleared correctly."
    elif reached:
        return "Ambulance reached but too many steps used."
    else:
        return "Ambulance did not reach hospital."
def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)
if __name__ == "__main__":
    main()
