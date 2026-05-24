from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import EqualsSubstitution, LaunchConfiguration
from launch_ros.actions import Node

UNITREE_RANGE_MIN = 0.8
UNITREE_MIN_HEIGHT = 0.12
UNITREE_MAX_HEIGHT = 0.55

VELODYNE_RANGE_MIN = 0.5
VELODYNE_MIN_HEIGHT = 0.25
VELODYNE_MAX_HEIGHT = 0.70


def pointcloud_to_laserscan_node(lidar_name, cloud_topic, range_min, min_height, max_height):
    return Node(
        package="pointcloud_to_laserscan",
        executable="pointcloud_to_laserscan_node",
        name="pointcloud_to_laserscan",
        output="screen",
        condition=IfCondition(
            EqualsSubstitution(LaunchConfiguration("lidar"), lidar_name)
        ),
        remappings=[
            ("cloud_in", cloud_topic),
            ("scan", "/scan"),
        ],
        parameters=[
            {
                "use_sim_time": LaunchConfiguration("use_sim_time"),
                "target_frame": "base_footprint",
                "transform_tolerance": 0.05,
                "min_height": min_height,
                "max_height": max_height,
                "angle_min": -3.14159,
                "angle_max": 3.14159,
                "angle_increment": 0.0087,
                "scan_time": 0.1,
                "range_min": range_min,
                "range_max": 30.0,
                "use_inf": True,
                "inf_epsilon": 1.0,
                "qos_overrides": {
                    "/scan": {
                        "publisher": {
                            "reliability": "reliable",
                            "history": "keep_last",
                            "depth": 10,
                            "durability": "volatile",
                        }
                    }
                },
            }
        ],
    )


def generate_launch_description():
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
            pointcloud_to_laserscan_node(
                "unitree_lidar",
                "/unitree_lidar/points",
                UNITREE_RANGE_MIN,
                UNITREE_MIN_HEIGHT,
                UNITREE_MAX_HEIGHT,
            ),
            pointcloud_to_laserscan_node(
                "velodyne_points",
                "/velodyne_points/points",
                VELODYNE_RANGE_MIN,
                VELODYNE_MIN_HEIGHT,
                VELODYNE_MAX_HEIGHT,
            ),
        ]
    )
