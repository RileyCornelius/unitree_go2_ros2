from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    unitree_go2_sim = FindPackageShare("unitree_go2_sim")
    unitree_go2_description = FindPackageShare("unitree_go2_description")

    use_sim_time = LaunchConfiguration("use_sim_time")
    map_file = LaunchConfiguration("map")
    world = LaunchConfiguration("world")
    launch_rviz = LaunchConfiguration("launch_rviz")

    nav2_config = PathJoinSubstitution([unitree_go2_sim, "config", "nav", "nav2.yaml"])
    rviz_config = PathJoinSubstitution([unitree_go2_sim, "rviz", "rviz.rviz"])
    default_world = PathJoinSubstitution(
        [unitree_go2_description, "worlds", "maze_world.sdf"]
    )
    default_map = PathJoinSubstitution([unitree_go2_sim, "maps", "go2_map.yaml"])

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [unitree_go2_sim, "launch", "unitree_go2_launch.py"]
            )
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "rviz": "false",
            "world": world,
        }.items(),
    )

    nav2_nodes = [
        Node(
            package="nav2_map_server",
            executable="map_server",
            name="map_server",
            output="screen",
            parameters=[{"use_sim_time": use_sim_time}, {"yaml_filename": map_file}],
        ),
        Node(
            package="nav2_amcl",
            executable="amcl",
            name="amcl",
            output="screen",
            parameters=[nav2_config, {"use_sim_time": use_sim_time}],
        ),
        Node(
            package="nav2_controller",
            executable="controller_server",
            name="controller_server",
            output="screen",
            parameters=[nav2_config, {"use_sim_time": use_sim_time}],
            remappings=[("cmd_vel", "cmd_vel_nav")],
        ),
        Node(
            package="nav2_smoother",
            executable="smoother_server",
            name="smoother_server",
            output="screen",
            parameters=[nav2_config, {"use_sim_time": use_sim_time}],
        ),
        Node(
            package="nav2_planner",
            executable="planner_server",
            name="planner_server",
            output="screen",
            parameters=[nav2_config, {"use_sim_time": use_sim_time}],
        ),
        Node(
            package="nav2_behaviors",
            executable="behavior_server",
            name="behavior_server",
            output="screen",
            parameters=[nav2_config, {"use_sim_time": use_sim_time}],
        ),
        Node(
            package="nav2_bt_navigator",
            executable="bt_navigator",
            name="bt_navigator",
            output="screen",
            parameters=[nav2_config, {"use_sim_time": use_sim_time}],
        ),
        Node(
            package="nav2_waypoint_follower",
            executable="waypoint_follower",
            name="waypoint_follower",
            output="screen",
            parameters=[nav2_config, {"use_sim_time": use_sim_time}],
        ),
        Node(
            package="nav2_velocity_smoother",
            executable="velocity_smoother",
            name="velocity_smoother",
            output="screen",
            parameters=[nav2_config, {"use_sim_time": use_sim_time}],
            remappings=[
                ("cmd_vel", "cmd_vel_nav"),
                ("cmd_vel_smoothed", "cmd_vel"),
            ],
        ),
    ]

    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_navigation",
        output="screen",
        parameters=[
            {"use_sim_time": use_sim_time},
            {"autostart": True},
            {
                "node_names": [
                    "map_server",
                    "amcl",
                    "controller_server",
                    "smoother_server",
                    "planner_server",
                    "behavior_server",
                    "bt_navigator",
                    "waypoint_follower",
                    "velocity_smoother",
                ]
            },
        ],
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
                "map",
                default_value=default_map,
                description="Full path to map YAML file to load",
            ),
            DeclareLaunchArgument(
                "world",
                default_value=default_world,
                description="Gazebo world file path",
            ),
            DeclareLaunchArgument(
                "launch_rviz",
                default_value="true",
                description="Launch RViz for the Nav2 session",
            ),
            sim_launch,
            *nav2_nodes,
            TimerAction(period=8.0, actions=[lifecycle_manager]),
            rviz_node,
        ]
    )
