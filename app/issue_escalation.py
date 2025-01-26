def issue_escalation(text):
    imp = ['Urgent','Disruption','Outage','Crash','Critical','Breach','Virus','Incident','Failure','immediate','crucial','exchange']
    for element in imp:
        if element.lower() in text.lower():
            return 'high'
    return 'low'

def required_issue_escalation(text):
    if text=="high":
        return True
    else:
        return False