import logging
import os
import typing
from threading import Thread
from typing import Dict, Any, List
from importlib import import_module

import plugins.mdc_self.config as mdcConfig
from mbot.core.plugins import plugin
from mbot.core.plugins import PluginContext, PluginMeta
from mbot.common.flaskutils import api_result
from flask import Blueprint, request

########################依赖库初始化###########################
# 依赖库列表

import_list = [
    'cloudscraper',
    'pyquery',
    'Pillow',
    'PySocks',
    'zhconv',
    'langid',
    'opencv-contrib-python-headless',
    'tqdm',
    'OpenCC',
    'deepl-translate',
    'ping3',
    'cloudscraper',
    'urllib3',
    'certifi',
    'MechanicalSoup',
    'opencc-python-reimplemented',
    'face_recognition',
    'get-video-properties'
]
# 判断依赖库是否安装,未安装则安装对应依赖库
sourcestr = "https://pypi.tuna.tsinghua.edu.cn/simple/"  # 镜像源


def GetPackage(PackageName):
    comand = "pip install " + PackageName + " -i " + sourcestr
    # 正在安装
    print("------------------正在安装" + str(PackageName) + " ----------------------")
    print(comand + "\n")
    os.system(comand)


for v in import_list:
    try:
        import_module(v)
    except ImportError:
        print("Not find " + v + " now install")
        GetPackage(v)
#############################################################
from .Movie_Data_Capture import start

_LOGGER = logging.getLogger(__name__)
bp = Blueprint('plugin_mdc', __name__)
"""
把flask blueprint注册到容器
这个URL访问完整的前缀是 /api/plugins/你设置的前缀 
"""
plugin.register_blueprint('mdc', bp)

message_to_uid: typing.List[int] = []
main_mode: typing.List[int] = []
link_mode: typing.List[int] = []
source_folder: str = ''
failed_output_folder: str = ''
success_output_folder: str = ''
exclude_folders: str = ''
switch: typing.List[int] = []
proxy_type: typing.List[str] = []
proxy: str = ''


@plugin.after_setup
def after_setup(plugin_meta: PluginMeta, config: Dict[str, Any]):
    """
    插件初始化完成时调用
    """
    _LOGGER.info('mdc插件完成初始化了...')
    config_init(config)


@plugin.config_changed
def config_changed(config: Dict[str, Any]):
    """
    当用户变更插件配置后调用此函数
    """
    config_init(config)


@plugin.on_event(
    bind_event=['DownloadCompleted'], order=1)
def on_event(ctx: PluginContext, event_type: str, data: Dict):
    """
    接收下载完成的事件
    """
    _LOGGER.info(f'新的事件：{event_type} 事件数据：{data}')
    # 下载完成时存储的地址
    library_path = data['library_path']
    global source_folder
    if source_folder == library_path:
        start()


@plugin.task('art_daily_check_task', '日常艺术刮削任务', cron_expression='0 5 * * *')
def task():
    start()


def async_call(fn):
    def wrapper(*args, **kwargs):
        # 通过target关键字参数指定线程函数fun
        Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper


@async_call
def async_mdc_main():
    start()


@bp.route('/start', methods=["POST"])
def test():
    async_mdc_main()
    _LOGGER.info("已经开始异步进行刮削")
    return api_result(code=0, message='ok', data='成功')


def config_init(config: Dict[str, Any]):
    global message_to_uid
    message_to_uid = config.get('uid')
    global main_mode
    main_mode = config.get('main_mode')
    global link_mode
    link_mode = config.get('link_mode')
    global source_folder
    source_folder = config.get('source_folder')
    global failed_output_folder
    failed_output_folder = config.get('failed_output_folder')
    global success_output_folder
    success_output_folder = config.get('success_output_folder')
    global exclude_folders
    exclude_folders = config.get('exclude_folders')
    global switch
    switch = config.get('switch')
    global proxy_type
    proxy_type = config.get('proxy_type')
    global proxy
    proxy = config.get('proxy')
    # 读取配置文件的值，修改对应的配置
    option_cmd = f'common:main_mode={main_mode};link_mode={link_mode};source_folder={source_folder};' \
                 f'failed_output_folder={failed_output_folder};success_output_folder={success_output_folder};' \
                 f'escape:folders={exclude_folders};proxy:switch={switch};type={proxy_type};proxy={proxy}'
    conf = mdcConfig.Config()
    conf.set_override(option_cmd)
    with open('/data/plugins/mdc_self/config.ini', "wt", encoding='UTF-8') as code:
        conf.conf.write(code)
    code.close()
