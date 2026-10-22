from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('device', default_value='/dev/video0'),
        Node(
            package='usb_cam',
            executable='usb_cam_node_exe',
            namespace='rov/cam_front',
            parameters=[{
                'video_device': LaunchConfiguration('device'),
                'image_width': 640,
                'image_height': 480,
                'framerate': 15.0,
                'pixel_format': 'mjpeg2rgb',
                'brightness': 128,
                'frame_id': 'cam_front_optical_frame',
            }],
        ),
    ])
