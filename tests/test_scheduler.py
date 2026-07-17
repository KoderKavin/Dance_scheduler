from datetime import datetime
from app.engine import check_overlap, calculate_full_schedule

# Mock objects
class MockDance:
    def __init__(self, name, member_ids):
        self.name = name
        self.member_ids = member_ids

class MockSession:
    def __init__(self, id, duration, dance, sort_order=0, custom_time=None):
        self.id = id
        self.duration = duration
        self.dance = dance
        self.sort_order = sort_order
        self.custom_time = custom_time

class MockDancer:
    def __init__(self, id, name, busy_times=None):
        self.id = id
        self.name = name
        self.busy_times = busy_times or []

class MockDailyConstraint:
    def __init__(self, dancer_id, time_range):
        self.dancer_id = dancer_id
        self.time_range = time_range

# Test check_overlap
def test_check_overlap():
    fmt = "%H:%M"
    # Overlap
    assert check_overlap(datetime.strptime("10:00", fmt), datetime.strptime("11:00", fmt),
                         datetime.strptime("10:30", fmt), datetime.strptime("11:30", fmt)) == True
    # No overlap
    assert check_overlap(datetime.strptime("10:00", fmt), datetime.strptime("11:00", fmt),
                         datetime.strptime("11:00", fmt), datetime.strptime("12:00", fmt)) == False
    print("test_check_overlap passed")

# Test calculate_full_schedule
def test_calculate_full_schedule():
    dancers = [MockDancer(1, "Alice", [("19:00", "19:30")])]
    dance1 = MockDance("Dance1", [1])
    sessions = [MockSession(1, 30, dance1)]
    daily_constraints = [MockDailyConstraint(1, "20:00-20:30")]
    
    schedule = calculate_full_schedule(sessions, dancers, daily_constraints, "18:00")
    
    assert len(schedule) == 1
    assert schedule[0]["start"] == "18:00"
    assert schedule[0]["end"] == "18:30"
    assert len(schedule[0]["conflicts"]) == 0
    
    # Test conflict
    sessions2 = [MockSession(1, 60, dance1)] # 18:00 - 19:00
    schedule2 = calculate_full_schedule(sessions2, dancers, daily_constraints, "18:30")
    # Starts at 18:30, ends at 19:30. Alice is busy 19:00-19:30.
    assert len(schedule2[0]["conflicts"]) == 1
    assert "Alice (Roster)" in schedule2[0]["conflicts"]
    
    print("test_calculate_full_schedule passed")

if __name__ == "__main__":
    test_check_overlap()
    test_calculate_full_schedule()
