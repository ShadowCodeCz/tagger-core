import datetime
import glob
import json
import os.path
import shutil

import app_core
import alphabetic_timestamp as ats


from .. import predefined
from . import filter
from . import create
from . import tag


class MergeParams:
    def __init__(self):
        self.engine = ""
        self.filter_rule = filter.ReFilterRule()
        self.source = ""
        self.destination = ""
        self.path_destination_template = ""


class TaggedDirectoriesMergeMachine:
    def __init__(self, logger):
        self.logger = logger
        self.locator = RecursiveTaggedDirectoriesLocator()
        self.source_index_builder = TaggedDirectoriesIndexBuilder(filter.NoFilter())
        self.destination_index_builder = TaggedDirectoriesIndexBuilder(filter.NoFilter())
        self.engines = {
            BasicMergeEngine.__name__: BasicMergeEngine(self.logger)
        }
        self.params = None

    def merge_by_params(self, params):
        self.params = params
        source_directories = self.locator.locate(params.source)
        destination_directories = self.locator.locate(params.destination)

        # print(source_directories)
        # print("-")
        # print(destination_directories)
        # print("--")

        self.source_index_builder.filter = filter.ReFilter(params.filter_rule)
        source_index = self.source_index_builder.build(source_directories)
        destination_index = self.destination_index_builder.build(destination_directories)

        # print(source_index)
        # print("*")
        # print(destination_index)
        # print("**")

        for source_mag in source_index:
            if not source_mag in destination_index:
                # print(f"mag for merge {source_mag}")
                self.merge_single_directory(source_index[source_mag], self.params.engine)

    def merge_single_directory(self, source_item, engine_name):
        engine = self.engines[engine_name]
        engine_params = MergeEngineParams()
        engine_params.source_item = source_item
        engine_params.destination_directory = self.params.destination
        engine_params.path_destination_template = self.params.path_destination_template
        engine.merge(engine_params)


class MergeEngineParams:
    def __init__(self):
        self.source_item = None
        self.destination_directory = None
        self.path_destination_template = None


class BasicMergeEngine:
    def __init__(self, logger):
        self.logger = logger
        self.params = None
        self.tag_parser = tag.TagsParser()

    def merge(self, params):
        self.params = params

        directory_creator_params = create.DirectoryCreatorParams()
        directory_creator_params.path_template = os.path.join(self.params.destination_directory, self.params.path_destination_template)
        directory_creator_params.tags = self.params.source_item.tags
        directory_creator_params.tags.append(f"merged@{datetime.datetime.now()}")
        directory_creator_params.dt = self.dt()

        directory_creator = create.DirectoryCreator(self.logger)
        destination_directory = directory_creator.create(directory_creator_params)

        print(f"{self.params.source_item.path} ---> {destination_directory}")
        # os.makedirs(destination_directory, exist_ok=True)
        if not os.path.exists(self.params.source_item.path):
            print(f"!!! Source path {self.params.source_item.path} does not exists !!!")
        shutil.copytree(self.ensure_trailing_slash(self.params.source_item.path), self.ensure_trailing_slash(destination_directory), dirs_exist_ok=True)

    def dt(self):
        parsed_tags = self.tag_parser.parse(self.params.source_item.tags)
        reader = tag.TagsReader(parsed_tags)
        mag_value = reader.read_tag_value("mag")
        return ats.base62.to_datetime(mag_value)

    def ensure_trailing_slash(self, path):
        normalized_path = os.path.normpath(path)
        if not normalized_path.endswith(os.sep):
            return normalized_path + os.sep
        else:
            return normalized_path


class RecursiveTaggedDirectoriesLocator:
    def locate(self, root_directory):
        template = os.path.join(root_directory, "**", ".tagger.json")
        return [os.path.abspath(os.path.dirname(t)) for t in glob.glob(template, recursive=True)]


class TaggedItem:
    def __init__(self, path, tags):
        self.path = path
        self.tags = tags

    @property
    def mag(self):
        for t in self.tags:
            if "mag@" in t:
                return t


class TaggedDirectoriesIndexBuilder:
    def __init__(self, filter):
        self.filter = filter

    def build(self, directories):
        index = {}
        items = self.tagged_items(directories)
        for item in self.filter.filter(items):
            index[item.mag] = item
        return index

    def tagged_items(self, directories):
        result = []
        for directory in directories:
            item = TaggedItem(directory, [])
            self.load_tags(item)
            result.append(item)
        return result

    def load_tags(self, item):
        tagger_file = os.path.join(item.path, ".tagger.json")
        with open(tagger_file, "r") as f:
            item.tags = json.load(f)

