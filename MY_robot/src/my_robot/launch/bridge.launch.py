from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable, TimerAction
from launch_ros.actions import Node
import os


def generate_launch_description():

    # 🔥 Set resource path (your export command)
    set_env = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '') +
              ':/home/sidharth/MY_robot/install/my_robot/share'
    )

    # 🔥 Spawn robot (your ign service command)
    spawn_robot = TimerAction(
        period=2.0,
        actions=[
            ExecuteProcess(
                cmd=[
                    'ign', 'service',
                    '-s', '/world/earthquake_disaster/create',
                    '--reqtype', 'ignition.msgs.EntityFactory',
                    '--reptype', 'ignition.msgs.Boolean',
                    '--timeout', '5000',
                    '--req',
                    'sdf_filename: "/home/sidharth/MY_robot/install/my_robot/share/my_robot/urdf/my_robot.sdf", '
                    'name: "my_robot", pose: {position: {x: 0, y: 0, z: 0.5}}'
                ],
                output='screen'
            )
        ]
    )

    # 🔥 Bridge (your ros2 run command)
    bridge = Node(
        package='ros_ign_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist'
        ],
        output='screen'
    )

    return LaunchDescription([
        set_env,
        spawn_robot,
        bridge
    ])