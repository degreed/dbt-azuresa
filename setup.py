#!/usr/bin/env python
from setuptools import find_packages
from distutils.core import setup

package_name = "dbt-azuredw"
package_version = "0.0.2"
description = """The Azure Synapse Analytics data warehouse adpter plugin for dbt (data build tool)"""

setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=description,
    author="Ethan Knox | Thomas La Piana",
    author_email="thomas@degreed.com.com",
    url="",
    packages=find_packages(),
    package_data={
        "dbt": [
            "include/azuredw/dbt_project.yml",
            "include/azuredw/macros/*.sql",
            "include/azuredw/macros/materializations/**/*.sql",
        ]
    },
    install_requires=["dbt-core==0.14.0", "pyodbc==4.0.26"],
)
