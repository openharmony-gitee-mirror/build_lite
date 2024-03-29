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

from collections import defaultdict

from hb.build.build_process import Build
from hb.set.set import set_product
from hb.common.utils import get_current_time
from hb.common.utils import OHOSException


def add_options(parser):
    parser.add_argument('component', help='name of the component', nargs='*',
                        default=None)
    parser.add_argument('-b', '--build_type', help='release or debug version',
                        nargs=1, default=['debug'])
    parser.add_argument('-c', '--compiler', help='specify compiler',
                        nargs=1, default=['clang'])
    parser.add_argument('-t', '--test', help='compile test suit', nargs='*')
    parser.add_argument('--dmverity', help='Enable dmverity',
                        action="store_true")
    parser.add_argument('--tee', help='Enable tee',
                        action="store_true")
    parser.add_argument('-p', '--product', help='build a specified product '
                        'with {product_name}@{company}, eg: camera@huawei',
                        nargs=1, default=[])
    parser.add_argument('-f', '--full',
                        help='full code compilation', action='store_true')
    parser.add_argument('-n', '--ndk', help='compile ndk',
                        action='store_true')
    parser.add_argument('-T', '--target', help='Compile single target',
                        nargs='*', default=[])
    parser.add_argument('-v', '--verbose',
                        help='show all command lines while building',
                        action='store_true')
    parser.add_argument('-shs', '--sign_haps_by_server',
                        help='sign haps by server', action='store_true')
    parser.add_argument('--patch', help='apply product patch before compiling',
                        action='store_true')
    parser.add_argument('--compact-mode',
                        help='compactiable with standard build system'
                        'set to true if we use build.sh as build entrance',
                        action='store_true', default=False)
    parser.add_argument('--gn-args', nargs=1, default='',
                        help='specifies gn build arguments, '
                             'eg: --gn-args="foo="bar" enable=true blah=7"')


def exec_command(args):
    if len(args.product):
        product, company = args.product[0].split('@')
        set_product(product_name=product, company=company)

    build = Build(args.component, args.compact_mode)
    cmd_args = defaultdict(list)

    build.register_args('ohos_build_type', args.build_type[0])
    # Get the compilation time in timestamp and human readable format
    build.register_args('ohos_build_time', get_current_time(type='timestamp'))
    build.register_args('ohos_build_datetime',
                        get_current_time(type='datetime'))

    if args.test is not None:
        build.test = args.test

    if args.dmverity:
        build.register_args('enable_ohos_security_dmverity',
                            'true',
                            quota=False)
        build.config.fs_attr.add('dmverity_enable')

    if args.tee:
        build.register_args('tee_enable', 'true', quota=False)
        build.config.fs_attr.add('tee_enable')

    if args.ndk:
        build.register_args('ohos_build_ndk', 'true', quota=False)

    if args.compact_mode is False and hasattr(args, 'target') and len(
            args.target):
        build.register_args('ohos_build_target', args.target)

    if hasattr(args, 'verbose') and args.verbose:
        cmd_args['gn'].append('-v')
        cmd_args['ninja'].append('-v')

    if hasattr(args, 'ninja'):
        return build.build(args.full, ninja=args.ninja)

    if args.sign_haps_by_server:
        build.register_args('ohos_sign_haps_by_server',
                            'true',
                            quota=False)

    if len(args.gn_args):
        for gn_arg in args.gn_args[0].split(' '):
            try:
                variable, value = gn_arg.split('=')
                build.register_args(variable, value)
            except ValueError:
                raise OHOSException(f'Invalid gn args: {gn_arg}')

    # Add build target, order is important
    if args.compact_mode:
        if hasattr(args, 'target') and len(args.target):
            cmd_args['ninja'].extend(args.target)
        else:
            cmd_args['ninja'].append('packages')

    return build.build(args.full, patch=args.patch, cmd_args=cmd_args)
