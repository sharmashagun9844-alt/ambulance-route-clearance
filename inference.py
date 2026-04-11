import sys
import os
import requests
import json

# ─────────────────────────────────────────
#  INFERENCE SCRIPT
#  Runs baseline agent on all 3 tasks
#  Judges run this to verify your environment
# ─────────────────────────────────────────

BASE_URL = os.environ.get("ENV_URL", "http://localhost:7860")

def run_task(task_id: int) -> dict:
    """Run baseline agent on a single task"""

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

    try:
        # Reset environment
        reset_resp = requests.post(
            f"{BASE_URL}/reset",
            json={"task_id": task_id},
            timeout=30
        )
        reset_resp.raise_for_status()

        total_reward = 0.0
        done = False

        # Run actions
        for action in baseline_actions[task_id]:
            if done:
                break
            step_resp = requests.post(
                f"{BASE_URL}/step",
                json=action,
                timeout=30
            )
            step_resp.raise_for_status()
            result = step_resp.json()
            total_reward += result.get("reward", 0.0)
            done = result.get("done", False)

        # Get grader score
        grader_resp = requests.get(f"{BASE_URL}/grader", timeout=30)
        grader_resp.raise_for_status()
        grader = grader_resp.json()

        score = round(min(total_reward / 1.5, 1.0), 2)

        return {
            "task_id": task_id,
            "score": score,
            "reached": grader.get("ambulance_reached", False),
            "steps": grader.get("steps_taken", 0),
            "status": "success"
        }

    except Exception as e:
        return {
            "task_id": task_id,
            "score": 0.0,
            "reached": False,
            "steps": 0,
            "status": f"error: {str(e)}"
        }


def main():
    print("=" * 50)
    print("Ambulance Route Clearance — Baseline Inference")
    print("Team: The Fine-Tuners")
    print("=" * 50)

    results = {}
    total_score = 0.0

    for task_id in [1, 2, 3]:
        print(f"\nRunning Task {task_id}...")
        result = run_task(task_id)
        results[f"task_{task_id}"] = result
        total_score += result["score"]
        print(f"  Score: {result['score']} | Reached: {result['reached']} | Steps: {result['steps']}")

    overall = round(total_score / 3, 2)
    results["overall_score"] = overall

    print(f"\n{'=' * 50}")
    print(f"Overall Score: {overall}")
    print("=" * 50)
    print(json.dumps(results, indent=2))

    return results


if __name__ == "__main__":
    main()
