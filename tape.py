import requests
import os
import re
import time
import subprocess
import signal
import traceback

class DuctTape:
    def __init__(self):
        self.url = os.environ['DUCTTAPE_URL']
        self.cmd = os.environ['DUCTTAPE_RESTART_CMD']

        self.interval = int(os.getenv('DUCTTAPE_INTERVAL', '3'))
        self.max_attempts = int(os.getenv('DUCTTAPE_ATTEMPTS', '6'))
        self.restart_interval = int(os.getenv('DUCTTAPE_RESTART_INTERVAL', '2'))
        self.requests_timeout = int(os.getenv('DUCTTAPE_REQUESTS_TIMEOUT', '5'))

        self.slack_webhook = os.getenv('DUCTTAPE_SLACK_WEBHOOK')
        self.slack_channel = os.getenv('DUCTTAPE_SLACK_CHANNEL')

        self.match = os.getenv('DUCTTAPE_MATCH')
        if self.match:
            self.regex = re.compile(self.match, re.IGNORECASE|re.DOTALL)

        self.last_restarted = 0
        self.attempts = 0
        self.running = True
        signal.signal(signal.SIGINT, self.__exit__)
    
    def __exit__(self, type, value):
        print('Exiting...')
        self.running = False

    def _loop(self):
        try:
            r = requests.get(self.url, timeout=self.requests_timeout)
        except requests.exceptions.Timeout as e:
            return False, f'Requests timeout: {e}'
        except Exception as e:
            return True, f'Unhandled requests exception: {e}'

        if r.status_code >= 400:
            return False, f'Status code is {r.status_code}'
        
        if self.match:
            has_title = self.regex.search(r.text)
            if not has_title:
                return False, f'Regex not matched: "{self.match}"'

        return True, None

    def _restart(self, msg):
        print(f'Restarting... {msg}')
        self._slack(msg)
        subprocess.Popen(self.cmd, shell=True)
        print('Restarted.')

    def _slack(self, msg):
        if not self.slack_webhook:
            print('No webhook set, not notifying on Slack.')
            return

        print('Notifying on Slack.')
        post_data = {'text': f':ducttape: Restarting {self.url} due to `{msg}`'}
        if self.slack_channel:
            post_data['channel'] = self.slack_channel

        response = requests.post(
            self.slack_webhook, json=post_data,
            headers={'Content-Type': 'application/json'},
        )


    def run(self):
        while self.running:

            # sleep x seconds if it was restarted recently
            if (self.last_restarted + self.restart_interval) > time.time():
                time.sleep(1)
                print('Sleeping until next loop...')
                continue

            # check if alive
            alive, msg = self._loop()
            if alive:
                self.attempts = 0
                print('Target is alive' if not msg else f'Warning: {msg}')
            else:
                self.attempts += 1
                print(f'Target is dead. {msg}')

            # restart if over threshold 
            if self.attempts > self.max_attempts:
                self._restart(msg)
                self.last_restarted = time.time()
                self.attempts = 0

            # sleep until next loop
            time.sleep(self.interval)
    
Tape = DuctTape()
Tape.run()
