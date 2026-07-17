from datetime import datetime, timedelta
from typing import List, Dict, Any

TIME_FORMAT = "%H:%M"


def _parse_time(time_str: str) -> datetime:
    """Parse a time string into a datetime object."""
    return datetime.strptime(time_str.strip(), TIME_FORMAT)


def _parse_range(range_str: str) -> tuple:
    """Parse a 'HH:MM-HH:MM' range string into (start, end) datetime tuple."""
    parts = range_str.split('-')
    return _parse_time(parts[0]), _parse_time(parts[1])


def check_overlap(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
    """Check if two time ranges overlap."""
    return max(start1, start2) < min(end1, end2)


def _preprocess_daily_constraints(daily_constraints) -> Dict[int, List[tuple]]:
    """Pre-parse daily constraints into {dancer_id: [(start, end), ...]} for faster lookups."""
    parsed: Dict[int, List[tuple]] = {}
    for dc in daily_constraints:
        try:
            start, end = _parse_range(dc.time_range)
            parsed.setdefault(dc.dancer_id, []).append((start, end))
        except Exception:
            continue
    return parsed


def calculate_full_schedule(
    sessions,
    dancers,
    daily_constraints,
    start_time_str: str = "18:00"
) -> List[Dict[str, Any]]:
    """Calculate the full schedule with conflict detection.

    Args:
        sessions: List of Session objects with sort_order, dance, duration, custom_time
        dancers: List of Dancer objects with busy_times
        daily_constraints: List of DailyConstraint objects with dancer_id, time_range
        start_time_str: Start time in HH:MM format

    Returns:
        List of schedule items with session_id, name, start, end, conflicts
    """
    schedule: List[Dict[str, Any]] = []

    # Sort by drag-and-drop order, then by id for stability
    sorted_sessions = sorted(sessions, key=lambda x: (getattr(x, 'sort_order', 0), x.id))

    current_time = _parse_time(start_time_str)
    dancer_map = {d.id: d for d in dancers}

    # Pre-process daily constraints for faster conflict checking
    dc_map = _preprocess_daily_constraints(daily_constraints)

    def get_conflicts(s_start: datetime, s_end: datetime, member_ids: List[int]) -> List[str]:
        """Check for conflicts between a session and dancer busy times/constraints."""
        conflicts: List[str] = []
        for d_id in member_ids:
            person = dancer_map.get(d_id)
            if not person:
                continue

            # Check dancer's regular busy times (from roster)
            for b_start, b_end in (person.busy_times or []):
                try:
                    if check_overlap(s_start, s_end, _parse_time(b_start), _parse_time(b_end)):
                        conflicts.append(f"{person.name} (Roster)")
                except Exception:
                    continue

            # Check today's daily constraints (pre-parsed)
            for dc_start, dc_end in dc_map.get(d_id, []):
                if check_overlap(s_start, s_end, dc_start, dc_end):
                    conflicts.append(f"{person.name} (Today)")

        return conflicts

    # Linear Flow for all sessions
    for s in sorted_sessions:
        if not s.dance:
            continue

        if s.custom_time:
            try:
                s_start, e_time = _parse_range(s.custom_time)
            except Exception:
                s_start = current_time
                e_time = current_time + timedelta(minutes=s.duration)
        else:
            s_start = current_time
            e_time = current_time + timedelta(minutes=s.duration)

        schedule.append({
            "session_id": s.id,
            "name": s.dance.name,
            "start": s_start.strftime(TIME_FORMAT),
            "end": e_time.strftime(TIME_FORMAT),
            "conflicts": get_conflicts(s_start, e_time, s.dance.member_ids)
        })

        current_time = e_time

    return schedule
