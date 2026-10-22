from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('source', default_value='udp://0.0.0.0:5000'),
        Node(
            package='rov_cameras',
            executable='cam_node',
            namespace='rov/cam_front',
            parameters=[{
                'source': LaunchConfiguration('source'),
                'frame_id': 'cam_front_optical_frame',
            }],
        ),
    ])
