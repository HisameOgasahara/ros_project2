from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='patrol_robot',
            executable='parol_robot',
            name='patrol_robot',
            output='sceen'
        )
    ])