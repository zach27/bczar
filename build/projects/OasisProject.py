#!/bin/env python

################################################################################
#
# @file        OasisProject.py
#
# $Id: OasisProject.py 3705 2013-03-05 17:44:43Z dfeiock $
#
# @author      James H. Hill
#
################################################################################

from ..Project import Project
from ..scm import Git

import os
from os import path
import logging

#
# __create__
#
# Factory function for creating the project.
#
def __create__ ():
    return OasisProject ()
    
#
# @class OasisProject
#
# Implementation of the Project object for XSC.
#
class OasisProject (Project):
    #
    # Default constuctor.
    #
    def __init__ (self):
        Project.__init__ (self, 'OASIS')
        self.__location__ = 'OASIS'

    #
    # Get the project's dependencies. The return value of this
    # function is a list of 1st level project dependencies.
    #
    def get_depends (self):
        return ['Boost', 'MPC', 'XercesC', 'DOC', 'ADBC']

    #
    # Downlaod the project's source files. The download can be from an online
    # archive, or a source code repository.
    #
    def download (self, ctx):
        abspath = path.abspath (path.join (ctx.prefix, self.__location__))

        if ctx.affiliate:
            if ctx.use_https:
                url = 'https://github.iu.edu/SEDS/OASIS.git'
            else:
                url = 'git@github.iu.edu:SEDS/OASIS.git'

            Git.checkout (url, abspath)
        else:
            if not ctx.use_https:
                logging.getLogger ().warn ('Github only supports HTTPS checkouts.')

            url = 'https://github.com/SEDS/OASIS.git'
            Git.checkout (url, abspath)

    # Set environment variables
    def set_env_variables (self, prefix):
        abspath = path.abspath (path.join (prefix, self.__location__))
        os.environ['OASIS_ROOT'] = abspath

        from ..Utilities import append_libpath_variable
        from ..Utilities import append_path_variable
        
        append_path_variable (path.join (abspath, 'bin'))
        append_libpath_variable (path.join (abspath, 'lib'))

    #
    # Validate environment for the project
    #
    def validate_environment (self):
        if 'OASIS_ROOT' not in os.environ:
            logging.getLogger ().error ('OASIS_ROOT environment variable is not defined')
            return False

        return True

    #
    # Update the script with details to configure the environment and
    # support the project.
    #
    # @param[in]            script          ScriptFile object
    #
    def update_script (self, prefix, script):
        abspath = path.abspath (path.join (prefix, self.__location__))

        if path.exists (abspath):
            script_path = script.get_this_variable ()
            location = os.path.join (script_path, self.__location__)

            script.begin_section ('OASIS')
            script.write_env_variable ('OASIS_ROOT', location)
            script.append_path_variable (path.join (location, 'bin'))
            script.append_libpath_variable (path.join (location, 'lib'))

    #
    # Build the XSC project.
    #
    def build (self, ctx):
        OASIS_ROOT = os.environ['OASIS_ROOT']
        workspace = path.join (OASIS_ROOT, 'OASIS.mwc')

        # Generate the workspace
        features = 'xerces3=1,boost=1,tao=1,sqlite3=1,tests=0,performance_tests=0,build=0,examples=0,snmp=0,noinline=0'
        feature_file = path.join (OASIS_ROOT, 'default.features')

        if 'TENA_HOME' in os.environ:
            features += ',tena=1'
        else:
            features += ',tena=0'

        if 'SSL_ROOT' in os.environ:
            features += ',openssl=1'
        else:
            features += ',openssl=0'

        if ctx.versioned_namespace:
            features += ',versioned_namespace=1'

        from ..MpcWorkspace import MpcContext, MpcWorkspace
        mpc_ctx = MpcContext (workspace, ctx.build_type, ctx.config, ctx.threads, features, True)
        mwc = MpcWorkspace (mpc_ctx)

        mwc.generate_default_feature_file (feature_file)
        mwc.generate ()
        mwc.build ()

    #
    # Build the XSC project.
    #
    def clean (self, ctx):
        OASIS_ROOT = os.environ['OASIS_ROOT']
        workspace = path.join (OASIS_ROOT, 'OASIS.mwc')

        # Generate the workspace
        features = 'xerces3=1,boost=1,tao=1,sqlite3=1,tests=0,performance_tests=0,build=0,examples=0,snmp=0,noinline=0'

        if 'TENA_HOME' in os.environ:
            features += ',tena=1'
        else:
            features += ',tena=0'

        if 'SSL_ROOT' in os.environ:
            features += ',openssl=1'
        else:
            features += ',openssl=0'

        if 'PIN_ROOT' in os.environ:
            features += ',pintool=1'
        else:
            features += ',pintool=0'

        if ctx.versioned_namespace:
            features += ',versioned_namespace=1'

        from ..MpcWorkspace import MpcContext, MpcWorkspace
        mpc_ctx = MpcContext (workspace, ctx.build_type, ctx.config, ctx.threads, features, True)
        mwc = MpcWorkspace (mpc_ctx)

        mwc.clean ()

