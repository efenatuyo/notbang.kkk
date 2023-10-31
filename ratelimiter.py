import time
from fastapi import Request, HTTPException
from typing import Dict

class RateLimiter:
    def __init__(self, requests_limit: int, time_window: int, auto_ban: bool = False):
        self.base_requests_limit = requests_limit
        self.requests_limit = requests_limit
        self.time_window = time_window
        self.request_counters: Dict[str, Dict[str, int]] = {}
        self.banned = []
        self.auto_ban = auto_ban
        self.key = "CdwZT9BpkXkGeoMAqIWy4raIPlj7GDnN"

    async def __call__(self, request: Request, key: str = None):
        kkk = key
        if kkk == self.key:
            self.time_window = 10

        client_ip = request.headers.get("x-forwarded-for").split(",")[-1]
      
        if "Discordbot" in request.headers.get("user-agent") and client_ip.startswith("35.") or client_ip.startswith("34."):
            return True

        
        
        if client_ip in self.banned:
            raise HTTPException(status_code=403, detail="You are banned.")

        route_path = request.url.path
        http_method = request.method
        current_time = int(time.time())
      
        if not kkk:
            key = f"{client_ip}:{http_method}:{route_path}"
        else:
            key = f"{client_ip}:{http_method}:{route_path}:{kkk}"

        if key not in self.request_counters:
            self.request_counters[key] = {"timestamp": current_time, "count": 1}
        else:
            if current_time - self.request_counters[key]["timestamp"] > self.time_window:
                self.request_counters[key]["timestamp"] = current_time
                self.request_counters[key]["count"] = 1
            else:
                if self.request_counters[key]["count"] >= self.requests_limit:
                    if self.auto_ban:
                        self.banned.append(client_ip)
                    raise HTTPException(status_code=429, detail="Rate limit exceeded.")
                else:
                    self.request_counters[key]["count"] += 1

        for k in list(self.request_counters.keys()):
            if current_time - self.request_counters[k]["timestamp"] > self.time_window:
                self.request_counters.pop(k)

        return True
