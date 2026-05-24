# Unitree Go2 ROS2

<p align="center">
  <img src="https://oss-global-cdn.unitree.com/static/c487f93e06954100a44fac4442b94d94_288x238.png" alt="Unitree Go2" />
</p>

## Overview

This package provides a complete ROS 2 Jazzy integration for the Unitree Go2 quadrupedal robot using the CHAMP controller framework. It includes custom configuration packages and robot description models specifically adapted for ROS 2, enabling simulation, control, and autonomous operation capabilities.

## About Unitree Go2

The Go2 is a quadrupedal robot manufactured by Unitree Robotics, designed for both research and commercial applications. It features powerful actuators, advanced sensor integration, and a robust mechanical design capable of navigating various terrains.

## About CHAMP Controller

CHAMP is an open-source development framework designed for quadrupedal robots. It provides a hierarchical control system that combines pattern modulation and impedance control techniques for efficient locomotion.

![CHAMP Controller](https://raw.githubusercontent.com/chvmp/champ/master/docs/images/robots.gif)

## Features

- ✅ Complete ROS 2 Jazzy integration
- ✅ URDF model adapted to ROS 2 control framework
- ✅ Gazebo Harmonic simulation support
- ✅ Teleoperation using keyboard
- ✅ RViz visualization
- ✅ Integrated gait control and configuration
- ✅ Simulated sensors:
  - ✅ IMU
  - ✅ 3D LiDAR (Velodyne VLP16)
  - ✅ 3D LiDAR (Unitree 4D L1)
  - ✅ Mono camera
  - ✅ Depth camera (RealSense D455 RGBD)
  - ✅ GPS (NavSat — simulates standard u-blox, ~0.5 m horizontal accuracy)
- ✅ Point cloud visualization in RViz
- ✅ Multiple sensor configurations available
- ✅ SLAM mapping with `slam_toolbox`
- ✅ Nav2 autonomous navigation with selectable LiDAR source

## System Requirements

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Sim Harmonic

## Installation

### 1. Create workspace and clone

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/RileyCornelius/unitree_go2_ros2
```

### 2. Install dependencies

```bash
cd ~/ros2_ws
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

### 3. Build

```bash
colcon build --symlink-install
source install/setup.bash
```

## Usage

### Gazebo Simulation

Launch the Gazebo simulation with RViz:

```bash
ros2 launch unitree_go2_sim unitree_go2_launch.py
```

RViz launches by default. To disable it:

```bash
ros2 launch unitree_go2_sim unitree_go2_launch.py rviz:=false
```

![Unitree Go2 Simulation](docs/unitree_go2_sim.png)

[Watch Demo on YouTube](https://youtu.be/NUu7TaZhaQM)


**Velodyne Lidar and 4D Lidar L1**

![Velodyne Lidar and 4D Lidar L1](docs/1.png)

**Velodyne Lidar Beams**

![Velodyne Lidar Beams](docs/2.png)

**4D Lidar L1 Beams**

![4D Lidar L1 Beams](docs/3.png)

**Mono Camera**

![Mono Camera](docs/camera.png)

### Teleoperation

With the simulation running, control the robot using keyboard:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### SLAM Mapping

Launch Gazebo, RViz, the point-cloud-to-laserscan adapter, and `slam_toolbox`. Use this when you want to build and save a map for later use with Nav2.

```bash
ros2 launch unitree_go2_sim go2_slam_launch.py
```

The SLAM launch defaults to the Unitree L1 LiDAR. To map with the Velodyne instead:

```bash
ros2 launch unitree_go2_sim go2_slam_launch.py lidar:=velodyne_points
```

Drive the robot around while SLAM is running:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Save the map once it looks complete in RViz:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/maps/go2_map
```

Run this from the `unitree_go2_sim` package directory. This creates `go2_map.yaml` and `go2_map.pgm` in the `maps/` folder.

### Navigation — SLAM + Nav2 (no pre-built map required)

The easiest way to navigate: one launch command starts SLAM, Nav2, and RViz together. `slam_toolbox` builds the map in real time and provides localization, so no pre-built map or AMCL is needed.

```bash
ros2 launch unitree_go2_sim go2_slam_nav_launch.py
```

**Sending a navigation goal:**

1. Wait for Gazebo and RViz to open and the map (grey area) to appear around the robot.
2. In the RViz toolbar, click **2D Goal Pose** (or press `G`).
3. Click a point on the map and drag to set the desired heading — an arrow will appear.
4. Release — Nav2 will plan a path (green line in RViz) and the robot will walk to the goal.

The map grows as the robot explores. Drive with teleop first to reveal areas before setting goals in unexplored space.

With Velodyne instead of Unitree L1:

```bash
ros2 launch unitree_go2_sim go2_slam_nav_launch.py lidar:=velodyne_points
```

### Navigation — Nav2 with a pre-built map (AMCL localization)

For known environments, load a saved map and use AMCL for localization:

```bash
ros2 launch unitree_go2_sim go2_nav_launch.py map:=maps/go2_map.yaml
```

**First run:** set the robot's initial pose with **2D Pose Estimate** in RViz (click the robot's location on the map and drag to match its heading). Once the AMCL particle cloud collapses, use **2D Goal Pose** to navigate.

With Velodyne:

```bash
ros2 launch unitree_go2_sim go2_nav_launch.py map:=maps/go2_map.yaml lidar:=velodyne_points
```

Without RViz:

```bash
ros2 launch unitree_go2_sim go2_nav_launch.py map:=maps/go2_map.yaml launch_rviz:=false
```

### Navigation Worlds

The base simulation launch defaults to `default.sdf`. The SLAM and Nav2 launches default to `maze_world.sdf`. To switch worlds, pass the full path to the `.sdf` file (found in `unitree_go2_description/worlds/`):

```bash
ros2 launch unitree_go2_sim unitree_go2_launch.py world:=src/unitree_go2_ros2/unitree_go2_description/worlds/walled_world.sdf
```

```bash
ros2 launch unitree_go2_sim go2_slam_launch.py world:=src/unitree_go2_ros2/unitree_go2_description/worlds/default.sdf
```

Available worlds:

| World | Description |
|-------|-------------|
| `default.sdf` | Open world with scattered obstacles and GPS origin metadata |
| `walled_world.sdf` | Small enclosed world with walls |
| `maze_world.sdf` | Narrow-corridor navigation test world (default for SLAM/Nav2) |

### LiDAR Selection for SLAM and Nav2

Both SLAM and Nav2 consume `/scan`. The launch files create `/scan` from one of the simulated point clouds:

| Launch value | Input point cloud | Output |
|--------------|-------------------|--------|
| `lidar:=unitree_lidar` | `/unitree_lidar/points` | `/scan` |
| `lidar:=velodyne_points` | `/velodyne_points/points` | `/scan` |

`unitree_lidar` is the default.

The scan adapter filters by height in `base_footprint` frame so floor returns are not projected into `/scan`. The Unitree L1 uses `0.12–0.55 m`; the Velodyne uses `0.25–0.70 m`. To tune these values, edit the constants in `unitree_go2_sim/launch/pointcloud_to_scan_launch.py`.

### GPS Simulation

The robot includes a simulated GPS (NavSat) sensor mounted on top of the trunk, publishing at 10 Hz on `/gps/fix` as `sensor_msgs/msg/NavSatFix`.

The sensor models standard u-blox-level accuracy:

| Axis | Noise (std dev) | Equivalent variance |
|------|----------------|---------------------|
| Horizontal (lat/lon) | 0.5 m | 0.25 m² |
| Vertical (altitude) | 0.8 m | 0.64 m² |

**Verify it is working:**

```bash
ros2 topic echo /gps/fix
```

**Setting the geographic origin:**

The world's GPS origin is defined in `unitree_go2_description/worlds/default.sdf` under `<spherical_coordinates>`. Edit `latitude_deg`, `longitude_deg`, and `elevation` to match your actual test site:

```xml
<spherical_coordinates>
  <surface_model>EARTH_WGS84</surface_model>
  <world_frame_orientation>ENU</world_frame_orientation>
  <latitude_deg>YOUR_LAT</latitude_deg>
  <longitude_deg>YOUR_LON</longitude_deg>
  <elevation>YOUR_ALT_METERS</elevation>
  <heading_deg>0</heading_deg>
</spherical_coordinates>
```

> **Note:** The `position_covariance` field in the bridged message will be all-zeros (`COVARIANCE_TYPE_UNKNOWN`) because the Gazebo→ROS bridge does not carry covariance. When integrating with `robot_localization`, set the covariance override in your EKF config or add a relay node that stamps diagonal covariance values matching the noise above.

## Tuning Gait Parameters

The gait configuration is in `unitree_go2_sim/config/gait/gait.yaml`:

> **Nav2 and SLAM configuration** is in `unitree_go2_sim/config/nav/nav2.yaml` and `unitree_go2_sim/config/nav/slam.yaml` respectively.

| Parameter | Value | Description |
|-----------|-------|-------------|
| `knee_orientation` | `>>` | How the knees bend (>> >< << <>) |
| `max_linear_velocity_x` | 0.3 m/s | Maximum forward/reverse speed |
| `max_linear_velocity_y` | 0.25 m/s | Maximum sideways speed |
| `max_angular_velocity_z` | 0.5 rad/s | Maximum rotational speed |
| `stance_duration` | 0.25 s | Time each leg spends on the ground per step |
| `swing_height` | 0.04 m | Foot trajectory height during swing phase |
| `stance_depth` | 0.01 m | Foot trajectory depth during stance phase |
| `nominal_height` | 0.225 m | Distance from hip to ground while walking |
| `com_x_translation` | 0.0 m | CoM offset to compensate for weight distribution |
| `odom_scaler` | 0.9 | Multiplier applied to calculated velocities for dead reckoning |

## Project Structure

```
unitree_go2_ros2/
├── champ/                    # CHAMP core quadruped controller (header-only library)
├── champ_base/               # ROS 2 interface nodes for CHAMP (controller, state estimation, EKF)
├── champ_msgs/               # Custom ROS 2 message types (contacts, joints, velocities)
├── unitree_go2_description/  # URDF, meshes, and Gazebo world files
│   ├── urdf/                 # Xacro robot description files
│   ├── meshes/               # Visual mesh files (.dae)
│   └── worlds/               # Gazebo SDF world files
└── unitree_go2_sim/          # Simulation launch files and configuration
    ├── launch/               # All launch files
    ├── config/
    │   ├── gait/             # Gait tuning parameters
    │   ├── joints/           # Joint name mapping
    │   ├── links/            # Link name mapping
    │   ├── nav/              # Nav2 (nav2.yaml) and SLAM (slam.yaml) parameters
    │   └── ros_control/      # ros2_control hardware interface config
    └── rviz/                 # RViz configuration
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository at [github.com/RileyCornelius/unitree_go2_ros2](https://github.com/RileyCornelius/unitree_go2_ros2)
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Acknowledgements

This project builds upon and incorporates work from the following projects:

* [Unitree Robotics](https://github.com/unitreerobotics/unitree_ros) — Go2 robot description (URDF model)
* [CHAMP](https://github.com/chvmp/champ) — Quadruped controller framework
* [CHAMP Robots](https://github.com/chvmp/robots) — Robot configurations and setup examples
* [unitree-go2-ros2](https://github.com/anujjain-dev/unitree-go2-ros2) — Original ROS 2 package with Gazebo Classic
* [khaledgabr77/unitree_go2_ros2](https://github.com/khaledgabr77/unitree_go2_ros2) — ROS 2 Jazzy + Gazebo Harmonic port this fork is based on

## License
