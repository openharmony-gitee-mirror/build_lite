#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2020 Huawei Device Co., Ltd.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os


def get_config_path():
    search_path = os.getcwd()
    root_path = os.path.abspath(os.sep)
    while search_path != root_path:
        config_path = os.path.join(search_path, 'ohos_config.json')
        if os.path.isfile(config_path):
            return config_path
        search_path = os.path.dirname(search_path)
    return os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        'common',
                                        'config.json'))


CONFIG_JSON = get_config_path()
CONFIG_STRUCT = {
    "root_path": None,
    "board": None,
    "kernel": None,
    "product": None,
    "product_path": None,
    "device_path": None
}
VERSION = '0.3.8'
