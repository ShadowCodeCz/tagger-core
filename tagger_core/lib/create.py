import json
import os
import platform
import socket
import uuid
import re
import datetime
import alphabetic_timestamp as ats
import app_core

from .. import predefined
from . import tag


class TaggedDirectoryCreatorParams:
    def __init__(self):
        self.path_template = ""
        self.tags = []
        self.sub_directories = []
        self.timestamp_auto_tagging = True
        self.machine_auto_tagging = True
        self.mac_address_auto_tagging = True
        self.only_tags_in_params = False


class SubTaggerParams:
    def __init__(self):
        self.dt = None


class MagTagger:
    def tags(self, params):
        dt = params.dt if params is not None else datetime.datetime.now()
        mag = ats.base62.from_datetime(dt, time_unit=ats.TimeUnit.seconds)
        return [f"mag@{mag}"]


class TimestampTagger:
    def tags(self, params):
        result = []
        dt = params.dt if params is not None else datetime.datetime.now()

        result.append(f"timestamp@{dt.timestamp()}")
        str_dt = dt.strftime("%Y.%m.%dT%H:%M:%S")
        str_year_month = dt.strftime("%Y.%m")
        str_month = dt.strftime("%B")
        result.append(f"datetime@{str_dt}")
        result.append(f"year.month@{str_year_month}")
        result.append(f"month@{str_month}")

        return result


class MachineTagger:
    def tags(self, params):
        result = []
        result.append(f"machine.platform.system@{self.remove_white_spaces(platform.system())}")
        result.append(f"machine.platform.release@{self.remove_white_spaces(platform.release())}")
        result.append(f"machine.platform.version@{self.remove_white_spaces(platform.version())}")
        result.append(f"machine.platform.architecture@{self.remove_white_spaces(platform.machine())}")
        result.append(f"machine.platform.processor@{self.remove_white_spaces(platform.processor())}")
        result.append(f"machine.socket.hostname@{self.remove_white_spaces(socket.gethostname())}")
        result.append(f"machine.socket.ip.address@{self.remove_white_spaces(socket.gethostbyname(socket.gethostname()))}")
        return result

    def remove_white_spaces(self, item):
        return str(item).replace(" ", "-")


class MacAddressTagger:
    def tags(self, params):
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        return [f"machine.socket.mac.address@{mac}"]


class BasicTagBuilderParams:
    def __init__(self):
        self.taggers = [
            "MagTagger",
            "TimestampTagger",
            "MachineTagger",
            "MacAddressTagger"
        ]
        self.dt = None
        self.tags = []
        self.only_tags_in_params = False


class BasicTagBuilder:
    taggers = {
        MagTagger.__name__: MagTagger(),
        TimestampTagger.__name__: TimestampTagger(),
        MachineTagger.__name__: MachineTagger(),
        MacAddressTagger.__name__: MacAddressTagger()
    }

    def build(self, params):
        tags = []

        if params.only_tags_in_params:
            return params.tags

        sub_params = SubTaggerParams()
        sub_params.dt = params.dt if params is not None else datetime.datetime.now()
        for tagger_name in params.taggers:
            tags += self.taggers[tagger_name].tags(sub_params)
        tags += params.tags

        return tags


class DirectoryCreatorParams:
    def __init__(self):
        self.path_template = None
        self.sub_directories = []
        self.tags = []
        self.dt = None


class DirectoryCreator:
    def __init__(self, logger):
        self.logger = logger
        self.path_evaluator = TaggedPathEvaluator()
        self.directory_path = ""
        self.params = None

    def create(self, params):
        # TODO: Already exists
        self.params = params
        self.evaluate_directory_path()
        self.create_directory()
        self.create_sub_directories()
        return self.directory_path

    def evaluate_directory_path(self):
        path_params = PathEvaluatorParams()
        path_params.path_template = self.params.path_template
        path_params.tags = self.params.tags
        path_params.dt = self.params.dt

        self.directory_path = self.path_evaluator.evaluate(path_params)

    def create_directory(self):
        if os.path.exists(self.directory_path):
            self.logger.warn(f"Directory path {self.directory_path} already exists")
        os.makedirs(self.directory_path, exist_ok=True)

    def create_sub_directories(self):
        for sub_directory in self.params.sub_directories:
            path = os.path.join(self.directory_path, sub_directory)
            os.makedirs(path, exist_ok=True)


class TaggerFileCreatorParams:
    def __init__(self):
        self.directory_path = None
        self.tags = None


class TaggerFileCreator:
    def __init__(self, logger):
        self.logger = logger
        self.params = None

    def create(self, params):
        self.params = params
        path = self.tagger_file_path()

        if os.path.exists(path):
            self.logger.warn(f"Tagger file already exists '{path}'. Writing to the file was stopped.")
            return

        with open(path, "w+") as f:
            json.dump(self.params.tags, f, indent=4)

    def tagger_file_path(self):
        return os.path.join(self.params.directory_path, ".tagger.json")


class TaggedDirectoryCreator:

    def __init__(self, logger):
        self.logger = logger
        self.params = DirectoryCreatorParams()
        self.dt = datetime.datetime.now()
        self.tag_builder = BasicTagBuilder()
        self.directory_creator = DirectoryCreator(logger)
        self.tagger_file_creator = TaggerFileCreator(logger)
        self.tags = []
        self.directory_path = ""

    def create(self, params):
        print("TaggedDirectoryCreator.create")
        # TODO: Add to database
        self.params = params
        self.restore()

        self.build_tags()
        self.create_directory()
        self.create_tagger_file()

        return self.directory_path

    def restore(self):
        self.tags = []
        self.dt = datetime.datetime.now()
        self.directory_path = ""

    def build_tags(self):
        self.tags = []
        build_params = BasicTagBuilderParams()
        build_params.taggers = [
            MagTagger.__name__
        ]

        if self.params.timestamp_auto_tagging:
            build_params.taggers.append(TimestampTagger.__name__)

        if self.params.machine_auto_tagging:
            build_params.taggers.append(MachineTagger.__name__)

        if self.params.mac_address_auto_tagging:
            build_params.taggers.append(MacAddressTagger.__name__)

        build_params.dt = self.dt
        build_params.tags = self.params.tags
        build_params.only_tags_in_params = self.params.only_tags_in_params
        self.tags = self.tag_builder.build(build_params)

    def create_directory(self):
        params = DirectoryCreatorParams()
        params.path_template = self.params.path_template
        params.sub_directories = self.params.sub_directories
        params.tags = self.tags
        params.dt = self.dt

        self.directory_path = self.directory_creator.create(params)

    def create_tagger_file(self):
        params = TaggerFileCreatorParams()
        params.directory_path = self.directory_path
        params.tags = self.tags

        self.tagger_file_creator.create(params)


class PathEvaluatorParams:
    def __init__(self):
        self.path_template = ""
        self.tags = []
        self.dt = None


class TaggedPathEvaluator:
    def __init__(self):
        self.params = None

    def evaluate(self, params):
        self.params = params
        return self.tags_evaluation(self.time_evaluation())

    def time_evaluation(self):
        return self.params.dt.strftime(self.params.path_template)

    def tags_evaluation(self, path):
        # print(f"TaggedPathEvaluator: path {path}")
        tags_parser = tag.TagsParser()
        tags_index = tags_parser.parse(self.params.tags)
        # print(f"TaggedPathEvaluator: tags {self.params.tags}")

        for tag_name in tags_index:
            tag_value = tags_index[tag_name].value
            path = path.replace(f"<{tag_name}>", f"{tag_value}")
        # print(f"TaggedPathEvaluator: path(final) {path}")
        print(f"TaggedPathEvaluator: path(final) {path}")
        return path
