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
    lidar = LaunchConfiguration("lidar")
    world = LaunchConfiguration("world")
    launch_rviz = LaunchConfiguration("launch_rviz")

    nav2_config = PathJoinSubstitution([unitree_go2_sim, "config", "nav", "nav2.yaml"])
    slam_config = PathJoinSubstitution([unitree_go2_sim, "config", "nav", "slam.yaml"])
    rviz_config = PathJoinSubstitution([unitree_go2_sim, "rviz", "rviz.rviz"])
    default_world = PathJoinSubstitution(
        [unitree_go2_description, "worlds", "maze_world.sdf"]
    )

    # Base simulation — slam_toolbox owns map->odom so publish_map_tf is false
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

    # Convert 3D point cloud to 2D laser scan for SLAM and Nav2 costmaps
    scan_adapter = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [unitree_go2_sim, "launch", "pointcloud_to_scan_launch.py"]
            )
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "lidar": lidar,
        }.items(),
    )

    # slam_toolbox in online async mode: builds the map AND publishes map->odom TF,
    # so no map_server or amcl is needed for localization.
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

    # Nav2 nodes — map_server and amcl are omitted because slam_toolbox handles
    # both map publication (/map) and localization (map->odom transform).
    nav2_nodes = [
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
                "lidar",
                default_value="unitree_lidar",
                description="Point cloud source for /scan: unitree_lidar or velodyne_points",
            ),
            DeclareLaunchArgument(
                "world",
                default_value=default_world,
                description="Gazebo world file path",
            ),
            DeclareLaunchArgument(
                "launch_rviz",
                default_value="true",
                description="Launch RViz for the SLAM+Nav2 session",
            ),
            sim_launch,
            scan_adapter,
            slam_toolbox,
            *nav2_nodes,
            lifecycle_manager,
            rviz_node,
        ]
    )
