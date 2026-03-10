from datetime import datetime, timedelta

def check_overlap(start1, end1, start2, end2):
    return max(start1, start2) < min(end1, end2)

def calculate_full_schedule(sessions, dancers, daily_constraints, start_time_str="18:00"):
    fmt = "%H:%M"
    schedule = []
    
    # Sort purely by drag-and-drop order
    sorted_sessions = sorted(sessions, key=lambda x: (getattr(x, 'sort_order', 0), x.id))
    
    current_time = datetime.strptime(start_time_str, fmt)
    dancer_map = {d.id: d for d in dancers}

    def get_conflicts(s_start, s_end, members):
        conflicts = []
        for d_id in members:
            person = dancer_map.get(d_id)
            if not person: continue
            
            for b_start, b_end in (person.busy_times or []):
                try:
                    if check_overlap(s_start, s_end, datetime.strptime(b_start, fmt), datetime.strptime(b_end, fmt)):
                        conflicts.append(f"{person.name} (Roster)")
                except Exception: continue

            for dc in daily_constraints:
                if dc.dancer_id == d_id:
                    try:
                        t_parts = dc.time_range.split('-')
                        if check_overlap(s_start, s_end, datetime.strptime(t_parts[0].strip(), fmt), datetime.strptime(t_parts[1].strip(), fmt)):
                            conflicts.append(f"{person.name} (Today)")
                    except Exception: continue 
        return conflicts

    # Linear Flow for all sessions
    for s in sorted_sessions:
        if not s.dance:
            continue

        if getattr(s, 'custom_time', None):
            try:
                t_parts = s.custom_time.split('-')
                s_start = datetime.strptime(t_parts[0].strip(), fmt)
                e_time = datetime.strptime(t_parts[1].strip(), fmt)
            except Exception:
                s_start = current_time
                e_time = current_time + timedelta(minutes=s.duration)
        else:
            s_start = current_time
            e_time = current_time + timedelta(minutes=s.duration)
        
        schedule.append({
            "session_id": s.id,
            "name": s.dance.name,
            "start": s_start.strftime(fmt),
            "end": e_time.strftime(fmt),
            "conflicts": get_conflicts(s_start, e_time, s.dance.member_ids)
        })
        
        current_time = e_time
            
    return schedule