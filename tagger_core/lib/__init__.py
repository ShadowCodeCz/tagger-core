import os
import subprocess

from . import auto
from . import create
from . import merge


def copy_path_to_clip_board(path):
    cmd = f"echo '{path}' | clip"
    echo_clip = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = echo_clip.communicate()[0]


def open_windows_explorer(path):
    subprocess.Popen([f"explorer", f"{path}"])


def switch_cwd(path):
    os.chdir(path)
    subprocess.run(["cmd"])


