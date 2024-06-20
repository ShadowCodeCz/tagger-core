import os
import app_core

from .. import predefined
from . import create


class AutomaticDirectoryCreator:
    def __init__(self):
        self.engine = None
        self.engines_classes = {
            BasicAutoCreatorEngine.engine_name: BasicAutoCreatorEngine
        }

        self.ac = app_core.AppCore(predefined.app_name)
        self.logger = self.ac.logger()
        self.ac.read_cfg()
        self.creator = None

    def create(self, profile, additional_tags):
        profile_cfg = self.ac.cfg["auto.profiles"][profile]
        engine_name = profile_cfg["engine"]
        self.engine = self.engines_classes[engine_name](profile_cfg, additional_tags)

        tagger_directory_creator_params = create.TaggedDirectoryCreatorParams()
        tagger_directory_creator_params.path_template = self.engine.build_path_template()
        tagger_directory_creator_params.tags = self.engine.build_tags()
        tagger_directory_creator_params.sub_directories = self.engine.build_sub_directories()
        tagger_directory_creator_params.timestamp_auto_tagging = self.engine.get_timestamp_auto_tagging()
        tagger_directory_creator_params.machine_auto_tagging = self.engine.get_machine_auto_tagging()
        tagger_directory_creator_params.mac_address_auto_tagging = self.engine.get_mac_address_auto_tagging()

        self.creator = creator = create.TaggedDirectoryCreator(self.logger)
        return creator.create(tagger_directory_creator_params)


class BasicAutoCreatorEngine:
    engine_name = "basic.auto.creator"

    def __init__(self, cfg, additional_tags):
        self.ac = app_core.AppCore(predefined.app_name)
        self.logger = self.ac.logger()
        self.cfg = cfg
        self.additional_tags = additional_tags

    def read_from_cfg(self, key, default):
        try:
            return self.cfg[key]
        except Exception as e:
            self.logger.warn(f"[BasicAutoCreatorEngine] For cfg key '{key}' was used default value")
            return default

    def read_boolean_from_string(self, s):
        return s.lower() in ["true", 1, "1", "yes", "t", "y"]

    def build_path_template(self):
        return self.read_from_cfg("path.template", os.path.join(self.ac.home_directory(), "tagger", "<mag>_%Y.%m.%dT%H-%M-%S"))

    def build_tags(self):
        predefined_tags = self.read_from_cfg("tags", [])
        return predefined_tags + self.additional_tags

    def build_sub_directories(self):
        return self.read_from_cfg("sub.directories", [])

    def get_timestamp_auto_tagging(self):
        s = self.read_from_cfg("timestamp.auto.tagging", "true")
        return self.read_boolean_from_string(s)

    def get_machine_auto_tagging(self):
        s = self.read_from_cfg("machine.auto.tagging", "true")
        return self.read_boolean_from_string(s)

    def get_mac_address_auto_tagging(self):
        s = self.read_from_cfg("mac.address.auto.tagging", "true")
        return self.read_boolean_from_string(s)
