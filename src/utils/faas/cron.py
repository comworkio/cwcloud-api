from croniter import croniter

def parse_crontab(crontab_str):
    if not croniter.is_valid(crontab_str):
        raise ValueError("Invalid crontab expression")

    parts = crontab_str.split()
    names = ['minute', 'hour', 'day', 'month', 'day_of_week']
    args = {}
    
    for i, part in enumerate(parts):
        args[names[i]] = part

    return args
