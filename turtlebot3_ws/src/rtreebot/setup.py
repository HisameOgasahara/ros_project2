from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'rtreebot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'web'), glob('web/*')),
        (os.path.join('share', package_name, 'docs'), glob('docs/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jetson',
    maintainer_email='jetson@todo.todo',
    description='WebSocket delivery mission bridge and controller for AMR manipulation mission',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'delivery_bridge = rtreebot.delivery_bridge_node:main',
            'delivery_ctrl = rtreebot.delivery_ctrl:main',
        ],
    },
)
