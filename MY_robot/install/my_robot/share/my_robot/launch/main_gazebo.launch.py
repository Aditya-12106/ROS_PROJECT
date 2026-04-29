from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():

    pkg_share = FindPackageShare('my_robot').find('my_robot')
    world_file = os.path.join(pkg_share, 'world', 'world.sdf')
    sdf_file = os.path.join(pkg_share, 'urdf', 'my_robot.sdf')

    return LaunchDescription([

        # Start Ignition Gazebo with the specified world
        ExecuteProcess(
            cmd=['ign', 'gazebo', '-r', world_file],
            output='screen'
        ),

        # Spawn robot
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
