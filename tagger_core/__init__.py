import os.path

import app_core

import argparse

from . import cli
from . import predefined
from . import lib


def save_help(text):
    return text.replace("%", "%%")


def main():
    ac = app_core.AppCore(predefined.app_name)

    ac.create_empty_extended_help()
    ac.create_app_cfg_directory()

    ac.create_cfg({
        "create.path.template": "<mag>_%Y.%m.%dT%H-%M-%S",
        "create.sub.directories": [""],
        "auto.profiles": {
            "project": {
                "engine": "basic.auto.creator",
                "path.template": os.path.join(ac.home_directory(), "tagger.data", "projects/<project>/<campaign>/<id>/<id>_%Y.%m.%dT%H-%M-%S"),
                "tags": ["project@proj", "campaign@camp"],
                "sub.directories": [],
                "timestamp.auto.tagging": "True",
                "machine.auto.tagging": "True",
                "mac.address.auto.tagging": "True"
            },
            "days": {
                "engine": "basic.auto.creator",
                "path.template": os.path.join(ac.home_directory(), "tagger.data", "days/%Y.%m.%d/%Y.%m.%dT%H-%M-%S_<id>"),
                "tags": [],
                "sub.directories": [],
                "timestamp.auto.tagging": "True",
                "machine.auto.tagging": "True",
                "mac.address.auto.tagging": "True"
            },
            "notes": {
                "engine": "basic.auto.creator",
                "path.template": os.path.join(ac.home_directory(), "tagger.data", "notes/%Y.%m.%dT%H-%M-%S_<id>"),
                "tags": ["note"],
                "sub.directories": [],
                "timestamp.auto.tagging": "True",
                "machine.auto.tagging": "True",
                "mac.address.auto.tagging": "True"
            }
        },
        "merge.profiles": {
            "project": {
                "tag.re.filter": {
                    "included": [["project@", "campaign@", "id@"]],
                    "excluded": [[]],
                },
                "engine": "project.merge.engine",
                "source": "C:\\tmp-tagger\\source",
                "destination": "C:\\tmp-tagger\\destination\\",
                "path.destination.template": "<project>\\<campaign>\\<id>\\<id>_<mag>_%Y.%m.%dT%H-%M-%S",
            }
        }
    })

    ac.read_cfg()
    ac.set_standard_logger()

    predefined_tags = "\n\t\t".join(predefined.tags)
    extended_help = ac.read_extended_help()
    description = f"""
        Tagger Core\n
        \n
        Predefined tags:\n
        \t{predefined_tags}
        \n
        {extended_help}"""

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers()

    mkdir_parser = subparsers.add_parser('mkdir', aliases=["create", "c"])
    mkdir_parser.add_argument("-p", "--path-template", default=ac.cfg["create.path.template"], help=save_help(ac.cfg["create.path.template"]))
    mkdir_parser.add_argument("-t", "--tags", default=[], nargs='*')
    mkdir_parser.add_argument("--supress-timestamp-auto-tagging", action='store_true')
    mkdir_parser.add_argument("--supress-machine-auto-tagging", action='store_true')
    mkdir_parser.add_argument("--supress-mac-address-auto-tagging", action='store_true')
    mkdir_parser.add_argument("-s", "--sub-directories", default=ac.cfg["create.sub.directories"], nargs='*')
    mkdir_parser.add_argument("-e", "--explorer", action='store_true')
    mkdir_parser.add_argument("-w", "--switch-cwd", action='store_true')
    mkdir_parser.add_argument("-c", "--copy-path-to-clipboard", action='store_true')
    # create_parser.add_argument("--cmd", default=None)
    mkdir_parser.set_defaults(func=cli.mkdir)

    auto_parser = subparsers.add_parser('auto', aliases=["a"])
    auto_parser.add_argument("-p", "--profile", help="Predefined profiles: project, days and notes")
    auto_parser.add_argument("-t", "--tags", default=[], nargs='*', help="id@ tag is mandatory, because it is incorporated in path templates.")
    auto_parser.add_argument("-e", "--explorer", action='store_true')
    auto_parser.add_argument("-w", "--switch-cwd", action='store_true')
    auto_parser.add_argument("-c", "--copy-path-to-clipboard", action='store_true')
    auto_parser.set_defaults(func=cli.auto)

    # TODO: POST ACTION
    merge_parser = subparsers.add_parser('merge')
    merge_parser.add_argument("-p", "--profile", help="Predefined profiles: project")
    merge_parser.set_defaults(func=cli.merge)

    # filter_parser = subparsers.add_parser('filter')
    # filter_parser.set_defaults(func=cli.filter)

    # TODO: Central database of tagged directories
    # TODO tag

    time_hash_parser = subparsers.add_parser('hash', aliases=["time-hash", "h"])
    time_hash_parser.set_defaults(func=cli.time_hash)

    # TODO: Derivators - adding derived tags, removing tags (conditions) [plugins?]

    arguments = parser.parse_args()
    arguments.func(arguments)

