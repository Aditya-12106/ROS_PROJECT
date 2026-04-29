from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():

    pkg_share = FindPackageShare('my_robot').find('my_robot')
    sdf_file = os.path.join(pkg_share, 'urdf', 'my_robot.sdf')

    return LaunchDescription([

        ExecuteProcess(
            cmd=['ign', 'gazebo', '-r'],
            output='screen'
        ),

        Node(
            package='ros_ign_gazebo',
            executable='create',
            arguments=[
                '-name', 'my_robot',
                '-file', sdf_file,
                '-z', '0.15'
            ],
            output='screen'
        )
    ])