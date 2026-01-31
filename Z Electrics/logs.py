import os, datetime, secrets
class ZegaTelemetry:
    def __init__(self):
        self.session_id = secrets.token_hex(8)
        self.root = "logs"
        for t in ['info', 'warning', 'error']: 
            os.makedirs(os.path.join(self.root, t), exist_ok=True)
    def _get_path(self, t):
        ts = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        return os.path.join(self.root, t, f"{ts}_{self.session_id}.log")
    def log(self, t, msg):
        entry = f"[{datetime.datetime.now()}] [{t.upper()}] [ID:{self.session_id}] {msg}\n"
        with open(self._get_path(t), "a") as f: f.write(entry)
telemetry = ZegaTelemetry()