import uuid
from openenv_core.env_server import Environment
from .models import AmbulanceAction, AmbulanceObservation, AmbulanceState, Signal

# ─────────────────────────────────────────
#  AMBULANCE ROUTE CLEARANCE ENVIRONMENT
#  Team: The Fine-Tuners
#  Real-world RL environment where AI agent
#  controls traffic signals for ambulances
# ─────────────────────────────────────────

class AmbulanceRouteEnv(Environment):

    def __init__(self):
        super().__init__()
        self._task_id = 1
        self._step_count = 0
        self._max_steps = 20
        self._ambulance_reached = False
        self._ambulance_pos = 0
        self._hospital_pos = 5
        self._signals = []
        self._blocked_roads = []
        self._time_elapsed = 0
        self._ambulances = 1
        self._episode_id = str(uuid.uuid4())

    # ─────────────────────────────────────────
    #  RESET — start fresh episode
    # ─────────────────────────────────────────
    def reset(self, task_id: int = 1) -> AmbulanceObservation:
        self._task_id = task_id
        self._step_count = 0
        self._ambulance_reached = False
        self._time_elapsed = 0
        self._episode_id = str(uuid.uuid4())

        if task_id == 1:
            # Easy: 1 signal, light traffic, short route
            self._ambulance_pos = 0
            self._hospital_pos = 5
            self._ambulances = 1
            self._blocked_roads = []
            self._signals = [
                Signal(id=1, position=2, status="red", traffic="light")
            ]

        elif task_id == 2:
            # Medium: 3 signals, moderate traffic, longer route
            self._ambulance_pos = 0
            self._hospital_pos = 10
            self._ambulances = 1
            self._blocked_roads = []
            self._signals = [
                Signal(id=1, position=3, status="red",   traffic="moderate"),
                Signal(id=2, position=6, status="red",   traffic="moderate"),
                Signal(id=3, position=9, status="green", traffic="light"),
            ]

        elif task_id == 3:
            # Hard: 2 ambulances, 4 signals, heavy traffic, blocked road
            self._ambulance_pos = [0, 2]
            self._hospital_pos = 12
            self._ambulances = 2
            self._blocked_roads = [5]
            self._signals = [
                Signal(id=1, position=3,  status="red",   traffic="heavy"),
                Signal(id=2, position=6,  status="red",   traffic="heavy"),
                Signal(id=3, position=8,  status="red",   traffic="heavy"),
                Signal(id=4, position=10, status="green", traffic="moderate"),
            ]

        return self._make_observation(reward=0.0, done=False, message="Episode started")

    # ─────────────────────────────────────────
    #  STEP — AI agent takes one action
    # ─────────────────────────────────────────
    def step(self, action: AmbulanceAction) -> AmbulanceObservation:
        self._step_count += 1
        reward = 0.0
        done = False
        message = ""

        # Find and update the signal
        for signal in self._signals:
            if signal.id == action.signal_id:
                if signal.status == "red" and action.new_status == "green":
                    signal.status = "green"

                    # Reward based on traffic — harder traffic = more reward
                    traffic_rewards = {"light": 0.3, "moderate": 0.4, "heavy": 0.5}
                    reward += traffic_rewards.get(signal.traffic, 0.3)
                    message = f"Signal {action.signal_id} cleared!"

        # Handle rerouting in task 3
        if action.reroute and self._task_id == 3:
            if 5 in self._blocked_roads:
                reward += 0.3
                message += " Rerouted around blocked road!"

        # Move ambulance forward if path is clear
        self._move_ambulance()

        # Check if ambulance reached hospital
        if self._check_reached():
            reward += 0.5
            done = True
            self._ambulance_reached = True
            message = "🚑 Ambulance reached hospital!"

        # End if max steps used up
        if self._step_count >= self._max_steps:
            done = True
            if not self._ambulance_reached:
                message = "Max steps reached — ambulance did not reach hospital"

        self._time_elapsed += 1

        return self._make_observation(reward=reward, done=done, message=message)

    # ─────────────────────────────────────────
    #  STATE — return current state
    # ─────────────────────────────────────────
    @property
    def state(self) -> AmbulanceState:
        return AmbulanceState(
            task_id=self._task_id,
            step_count=self._step_count,
            ambulance_reached=self._ambulance_reached,
            ambulance_position=self._ambulance_pos,
            hospital_position=self._hospital_pos,
            signals=self._signals,
            blocked_roads=self._blocked_roads,
            time_elapsed=self._time_elapsed
        )

    # ─────────────────────────────────────────
    #  HELPERS
    # ─────────────────────────────────────────
    def _make_observation(self, reward: float, done: bool, message: str) -> AmbulanceObservation:
        return AmbulanceObservation(
            ambulance_position=self._ambulance_pos,
            hospital_position=self._hospital_pos,
            signals=self._signals,
            blocked_roads=self._blocked_roads,
            time_elapsed=self._time_elapsed,
            ambulances=self._ambulances,
            reward=reward,
            done=done,
            message=message
        )

    def _move_ambulance(self):
        """Move ambulance forward if no red signal or block ahead"""
        if self._task_id in [1, 2]:
            next_pos = self._ambulance_pos + 1
            red_signal_ahead = any(
                s.position == next_pos and s.status == "red"
                for s in self._signals
            )
            road_blocked = next_pos in self._blocked_roads
            if not red_signal_ahead and not road_blocked:
                self._ambulance_pos = next_pos

        elif self._task_id == 3:
            for i, pos in enumerate(self._ambulance_pos):
                next_pos = pos + 1
                red_signal_ahead = any(
                    s.position == next_pos and s.status == "red"
                    for s in self._signals
                )
                road_blocked = next_pos in self._blocked_roads
                if not red_signal_ahead and not road_blocked:
                    self._ambulance_pos[i] = next_pos

    def _check_reached(self) -> bool:
        """Check if ambulance(s) reached hospital"""
        if self._task_id in [1, 2]:
            return self._ambulance_pos >= self._hospital_pos
        elif self._task_id == 3:
            return all(pos >= self._hospital_pos for pos in self._ambulance_pos)
        return False
