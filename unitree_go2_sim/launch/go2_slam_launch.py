from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    unitree_go2_sim = FindPackageShare("unitree_go2_sim")
    unitree_go2_description = FindPackageShare("unitree_go2_description")

    use_sim_time = LaunchConfiguration("use_sim_time")
    world = LaunchConfiguration("world")
    launch_rviz = LaunchConfiguration("launch_rviz")

    slam_config = PathJoinSubstitution([unitree_go2_sim, "config", "nav", "slam.yaml"])
    rviz_config = PathJoinSubstitution([unitree_go2_sim, "rviz", "rviz.rviz"])
    default_world = PathJoinSubstitution(
        [unitree_go2_description, "worlds", "maze_world.sdf"]
    )

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [unitree_go2_sim, "launch", "unitree_go2_launch.py"]
            )
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "rviz": "false",
            "publish_map_tf": "false",
            "publish_base_tf": "true",
            "dynamic_base_tf": "false",
            "world": world,
        }.items(),
    )

    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("slam_toolbox"), "launch", "online_async_launch.py"]
            )
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "slam_params_file": slam_config,
        }.items(),
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config],
        parameters=[{"use_sim_time": use_sim_time}],
        condition=IfCondition(launch_rviz),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use simulation (Gazebo) clock if true",
            ),
            DeclareLaunchArgument(
                "world",
                default_value=default_world,
                description="Gazebo world file path",
            ),
            DeclareLaunchArgument(
                "launch_rviz",
                default_value="true",
                description="Launch RViz for the SLAM session",
            ),
            sim_launch,
            slam_toolbox,
            rviz_node,
        ]
    )
