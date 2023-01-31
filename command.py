from typing import List

from mbot.core.plugins import plugin, PluginCommandContext, PluginCommandResponse
from mbot.openapi import mbot_api
from mbot.core.params import ArgSchema, ArgType
import logging

from .Movie_Data_Capture import start

server = mbot_api
_LOGGER = logging.getLogger(__name__)


@plugin.command(name='mdcx', title='立刻刮削', desc='立刻刮削目录文件', icon='AlarmOn', run_in_background=True)
def mdcx(ctx: PluginCommandContext):
    start()
    return PluginCommandResponse(True, f'刮削成功')
