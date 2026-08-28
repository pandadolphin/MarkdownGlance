from .preview.adapter.commands import *
from .preview.adapter.container import container
from .preview.adapter.events import *


def plugin_loaded():
    container.build()


def plugin_unloaded():
    container.unload()
