import alphabetic_timestamp as ats

import app_core

from . import lib
from . import predefined


def mkdir(arguments):
    print("mkdir")
    ac = app_core.AppCore(predefined.app_name)

    params = lib.create.TaggedDirectoryCreatorParams()
    params.path_template = arguments.path_template
    params.tags = arguments.tags
    params.sub_directories = arguments.sub_directories
    params.timestamp_auto_tagging = not arguments.supress_timestamp_auto_tagging
    params.machine_auto_tagging = not arguments.supress_machine_auto_tagging
    params.mac_address_auto_tagging = not arguments.supress_mac_address_auto_tagging

    print("creator")
    creator = lib.create.TaggedDirectoryCreator(ac.logger())
    path = creator.create(params)
    print(path) # TODO: Consider use logger
    tags_for_print = "\n\t".join(creator.tags)
    print(f"\t{tags_for_print}") # TODO: Consider use logger

    if arguments.explorer:
        lib.open_windows_explorer(path)

    if arguments.switch_cwd:
        lib.switch_cwd(path)

    if arguments.copy_path_to_clipboard:
        lib.copy_path_to_clip_board(path)


def auto(arguments):
    auto_creator = lib.auto.AutomaticDirectoryCreator()
    path = auto_creator.create(arguments.profile, arguments.tags)
    print(path) # TODO: Consider use logger
    tags_for_print = "\n\t".join(auto_creator.creator.tags)
    print(f"\t{tags_for_print}") # TODO: Consider use logger
    if arguments.explorer:
        lib.open_windows_explorer(path)

    if arguments.switch_cwd:
        lib.switch_cwd(path)

    if arguments.copy_path_to_clipboard:
        lib.copy_path_to_clip_board(path)


def merge(arguments):
    ac = app_core.AppCore(predefined.app_name)
    logger = ac.logger()
    ac.read_cfg()
    profile_cfg = ac.cfg["merge.profiles"][arguments.profile]

    params = lib.merge.MergeParams()
    params.engine = profile_cfg["engine"]
    params.source = profile_cfg["source"]
    params.destination = profile_cfg["destination"]
    params.path_destination_template = profile_cfg["path.destination.template"]
    params.filter_rule.included = profile_cfg["tag.re.filter"]["included"]
    params.filter_rule.excluded = profile_cfg["tag.re.filter"]["excluded"]

    m = lib.merge.TaggedDirectoriesMergeMachine(logger)
    m.merge_by_params(params)


def filter(arguments):
    print("filter")


def mktag(arguments):
    print("mktag")


def time_hash(arguments):
    print(ats.base62.now())