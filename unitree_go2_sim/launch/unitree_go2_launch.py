import os

import launch_ros
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    dynamic_base_tf = LaunchConfiguration("dynamic_base_tf")
    base_frame = "base_link"

    unitree_go2_sim = launch_ros.substitutions.FindPackageShare(
        package="unitree_go2_sim").find("unitree_go2_sim")
    unitree_go2_description = launch_ros.substitutions.FindPackageShare(
        package="unitree_go2_description").find("unitree_go2_description")

    joints_config = os.path.join(unitree_go2_sim, "config/joints/joints.yaml")
    ros_control_config = os.path.join(
        unitree_go2_sim, "config/ros_control/ros_control.yaml"
    )
    gait_config = os.path.join(unitree_go2_sim, "config/gait/gait.yaml")
    links_config = os.path.join(unitree_go2_sim, "config/links/links.yaml")
    default_model_path = os.path.join(unitree_go2_description, "urdf/unitree_go2_robot.xacro")
    default_world_path = os.path.join(unitree_go2_description, "worlds/default.sdf")
    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation (Gazebo) clock if true",
    )
    declare_rviz = DeclareLaunchArgument(
        "rviz", default_value="true", description="Launch rviz"
    )
    declare_robot_name = DeclareLaunchArgument(
        "robot_name", default_value="go2", description="Robot name"
    )
    declare_ros_control_file = DeclareLaunchArgument(
        "ros_control_file",
        default_value=ros_control_config,
        description="Ros control config path",
    )
    declare_gazebo_world = DeclareLaunchArgument(
        "world", default_value=default_world_path, description="Gazebo world file path"
    )
    declare_world_init_x = DeclareLaunchArgument("world_init_x", default_value="0.0")
    declare_world_init_y = DeclareLaunchArgument("world_init_y", default_value="0.0")
    declare_world_init_z = DeclareLaunchArgument("world_init_z", default_value="0.375")
    declare_world_init_heading = DeclareLaunchArgument(
        "world_init_heading", default_value="0.0"
    )
    declare_description_path = DeclareLaunchArgument(
        "unitree_go2_description_path",
        default_value=default_model_path,
        description="Path to the robot description xacro file",
    )

    declare_publish_map_tf = DeclareLaunchArgument(
        "publish_map_tf",
        default_value="true",
        description="Publish a static map to odom transform",
    )

    declare_publish_base_tf = DeclareLaunchArgument(
        "publish_base_tf",
        default_value="true",
        description="Publish a stable static base_footprint to base_link transform",
    )

    declare_dynamic_base_tf = DeclareLaunchArgument(
        "dynamic_base_tf",
        default_value="false",
        description="Use the CHAMP EKF for base_footprint to base_link instead of the static transform",
    )

    declare_base_link_z = DeclareLaunchArgument(
        "base_link_z",
        default_value="0.225",
        description="Static base_link height above base_footprint when publish_base_tf is true",
    )

    robot_description = {"robot_description": Command(["xacro ", LaunchConfiguration("unitree_go2_description_path"),
                                                       " robot_controllers:=", LaunchConfiguration("ros_control_file")])}

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[
            robot_description,
            {"use_sim_time": use_sim_time}
        ],
    )

    quadruped_controller_node = Node(
        package="champ_base",
        executable="quadruped_controller_node",
        output="screen",
        parameters=[
            {"use_sim_time": use_sim_time},
            {"gazebo": True},
            {"publish_joint_states": True},
            {"publish_joint_control": True},
            {"publish_foot_contacts": False},
            {"joint_controller_topic": "joint_group_effort_controller/joint_trajectory"},
            {"urdf": Command(['xacro ', LaunchConfiguration('unitree_go2_description_path')])},
            joints_config,
            links_config,
            gait_config,
            {"hardware_connected": False},
            {"publish_foot_contacts": False},
            {"close_loop_odom": True},
        ],
        remappings=[("/cmd_vel/smooth", "/cmd_vel")],
    )

    state_estimator_node = Node(
        package="champ_base",
        executable="state_estimation_node",
        output="screen",
        parameters=[
            {"use_sim_time": use_sim_time},
            {"orientation_from_imu": True},
            {"urdf": Command(['xacro ', LaunchConfiguration('unitree_go2_description_path')])},
            joints_config,
            links_config,
            gait_config,
        ],
    )

    base_to_footprint_ekf = Node(
        package="robot_localization",
        executable="ekf_node",
        name="base_to_footprint_ekf",
        output="screen",
        parameters=[
            {"base_link_frame": base_frame},
            {"use_sim_time": use_sim_time},
            os.path.join(
                get_package_share_directory("champ_base"),
                "config",
                "ekf",
                "base_to_footprint.yaml",
            ),
        ],
        remappings=[("odometry/filtered", "odom/local")],
        condition=IfCondition(dynamic_base_tf),
    )

    footprint_to_odom_ekf = Node(
        package="robot_localization",
        executable="ekf_node",
        name="footprint_to_odom_ekf",
        output="screen",
        parameters=[
            {"use_sim_time": use_sim_time},
            {"base_link_frame": "base_footprint"},
            {"odom_frame": "odom"},
            {"world_frame": "odom"},
            {"publish_tf": True},
            {"frequency": 50.0},
            {"two_d_mode": True},
            {"odom0": "odom/raw"},
            {"odom0_config": [False, False, False, False, False, False, True, True, False, False, False, True, False, False, False]},
            {"imu0": "imu/data"},
            {"imu0_config": [False, False, False, False, False, True, False, False, False, False, False, True, False, False, False]},
        ],
        remappings=[("odometry/filtered", "odom")],
    )

    map_to_odom_tf_node = Node(
        package='tf2_ros',
        name='map_to_odom_tf_node',
        executable='static_transform_publisher',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=[
            '--x', '0', '--y', '0', '--z', '0',
            '--roll', '0', '--pitch', '0', '--yaw', '0',
            '--frame-id', 'map', '--child-frame-id', 'odom'
        ],
        condition=IfCondition(LaunchConfiguration("publish_map_tf")),
    )

    base_footprint_to_base_link_tf_node = Node(
        package='tf2_ros',
        name='base_footprint_to_base_link_tf_node',
        executable='static_transform_publisher',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=[
            '--x', '0', '--y', '0', '--z', LaunchConfiguration("base_link_z"),
            '--roll', '0', '--pitch', '0', '--yaw', '0',
            '--frame-id', 'base_footprint', '--child-frame-id', 'base_link'
        ],
        condition=IfCondition(
            PythonExpression(
                [
                    "'",
                    LaunchConfiguration("publish_base_tf"),
                    "' == 'true' and '",
                    dynamic_base_tf,
                    "' != 'true'",
                ]
            )
        ),
    )

    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', os.path.join(unitree_go2_sim, "rviz/rviz.rviz")],
        parameters=[{"use_sim_time": use_sim_time}],
        condition=IfCondition(LaunchConfiguration("rviz")),
    )

    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={
            'gz_args': [LaunchConfiguration('world'), ' -r']
        }.items(),
    )

    gazebo_spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-name', LaunchConfiguration('robot_name'),
            '-topic', 'robot_description',
            '-x', LaunchConfiguration('world_init_x'),
            '-y', LaunchConfiguration('world_init_y'),
            '-z', LaunchConfiguration('world_init_z'),
            '-Y', LaunchConfiguration('world_init_heading')
        ],
    )

    gazebo_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gazebo_bridge',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=[
            # Gazebo to ROS
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/velodyne_points@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan', # /scan remapped
            '/velodyne_points/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/unitree_lidar/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/gps/fix@sensor_msgs/msg/NavSatFix[gz.msgs.NavSat',
            '/rgb_image@sensor_msgs/msg/Image[gz.msgs.Image',
            
            # D455 RGBD camera bridges
            '/d455/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/d455/depth_image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/d455/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/d455/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',

            # ROS to Gazebo
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/joint_group_effort_controller/joint_trajectory@trajectory_msgs/msg/JointTrajectory]gz.msgs.JointTrajectory',
        ],
        remappings=[
            ('/velodyne_points', '/scan'),
        ],
    )

    controller_spawner_js = TimerAction(
        period=20.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                output="screen",
                arguments=[
                    "--controller-manager-timeout", "120",
                    "joint_states_controller",
                ],
                parameters=[{"use_sim_time": use_sim_time}],
            )
        ]
    )

    controller_spawner_effort = TimerAction(
        period=30.0,
        actions=[
            Node(
                package="controller_manager",
                executable="spawner",
                output="screen",
                arguments=[
                    "--controller-manager-timeout", "120",
                    "joint_group_effort_controller",
                ],
                parameters=[{"use_sim_time": use_sim_time}],
            )
        ]
    )

    return LaunchDescription(
        [
            declare_use_sim_time,
            declare_rviz,
            declare_robot_name,
            declare_ros_control_file,
            declare_gazebo_world,
            declare_world_init_x,
            declare_world_init_y,
            declare_world_init_z,
            declare_world_init_heading,
            declare_description_path,
            declare_publish_map_tf,
            declare_publish_base_tf,
            declare_dynamic_base_tf,
            declare_base_link_z,
            gz_sim,
            robot_state_publisher_node,
            gazebo_spawn_robot,
            gazebo_bridge,
            quadruped_controller_node,
            state_estimator_node,
            base_to_footprint_ekf,
            footprint_to_odom_ekf,
            map_to_odom_tf_node,
            base_footprint_to_base_link_tf_node,
            controller_spawner_js,
            controller_spawner_effort,
            rviz2,
        ]
    )
