import os
import json
import app_core

from tagger_core import predefined


class TagDatabase:
    def __init__(self):
        self.ac = app_core.AppCore(predefined.app_name)
        self.path = os.path.join(self.ac.app_directory(), "database.json")
        self.content = []
        self.create()

    def create(self):
        if not os.path.exists(self.path):
            self.write()

    def add_directory(self, directory):
        self.read()
        self.content.append(os.path.abspath(directory))
        self.write()

    def read(self):
        with open(self.path, "r") as f:
            self.content = json.load(f)

    def write(self):
        with open(self.path, "w+") as f:
            json.dump(self.content, f)