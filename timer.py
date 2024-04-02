import time


class Timer:
    def __init__(self):
        self.started_at = 0
        self.counting = 0
        self.running = False

    def start(self):
        self.started_at = 0
        self.counting = 0
        if not self.running:
            self.started_at = time.time()
            self.running = not self.running

    def end(self):
        if self.running:
            self.running = not self.running

    def reset(self):
        self.counting = 0

    def update(self):
        if self.running:
            self.counting = round(time.time() - self.started_at)
