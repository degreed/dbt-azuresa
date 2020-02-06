#!/usr/bin/env python
from setuptools import find_packages
from distutils.core import setup

package_name = "dbt-azuredw"
package_version = "0.0.1"
description = """The azuredw adpter plugin for dbt (data build tool)"""

setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=description,
    author='Isaac Chavez | Jacob Mastel',
    author_email='ichavez@1aauto.com',
    url='',
    packages=find_packages(),
    package_data={
        'dbt': [
            'include/azuredw/dbt_project.yml',
            'include/azuredw/macros/*.sql',
            'include/azuredw/macros/materializations/**/*.sql',
        ]
    },
    install_requires=[
        'dbt-core>=0.14.0',
        'pyodbc'
    ]
)
