from utils.common import is_not_empty

_in_progress = "in_progress"
_states = ["complete", _in_progress, "error"]

def is_known_state (state):
    return is_not_empty(state) and any(c == "{}".format(state).lower() for c in _states)

def is_unknown_state (state):
    return not is_known_state(state)
