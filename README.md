# Unitree Go2 ROS2

<p align="center">
  <img src="https://oss-global-cdn.unitree.com/static/c487f93e06954100a44fac4442b94d94_288x238.png" alt="Unitree Go2" />
</p>

## Overview

This package provides a complete ROS 2 Jazzy integration for the Unitree Go2 quadrupedal robot using the CHAMP controller framework. It includes custom configuration packages and robot description models specifically adapted for ROS 2, enabling simulation, control, and autonomous operation capabilities.

## About Unitree Go2

The Go2 is a quadrupedal robot manufactured by Unitree Robotics, designed for both research and commercial applications. It features powerful actuators, advanced sensor integration, and a robust mechanical design capable of navigating various terrains.

## About CHAMP Controller

CHAMP (Coupled Hybrid Automata for Mobile Platforms) is an open-source development framework designed for quadrupedal robots. It provides a hierarchical control system that combines pattern modulation and impedance control techniques for efficient locomotion.

![CHAMP Controller](https://raw.githubusercontent.com/chvmp/champ/master/docs/images/robots.gif)

## Features

- ✅ Complete ROS 2 Jazzy integration
- ✅ URDF model adapted to ROS 2 control framework
- ✅ Gazebo Harmonic simulation support
- ✅ Teleoperation using keyboard
- ✅ RVIZ visualization
- ✅ Integrated gait control and configuration
- ✅ Simulated sensors (in progress):
  - ✅ IMU
  - ✅ 2D LiDAR (Hokuyo)
  - ✅ 3D LiDAR (Velodyne)
  - ✅ 3D LiDAR (4D Lidar L1) (need some imporvments)
  - ✅ Mono Camera
  - ❌ Depth Camera
  - ✅ GPS (NavSat — simulates standard u-blox, ~0.5 m horizontal accuracy)
- ✅ Point cloud visualization in RVIZ
- ✅ Multiple sensor configurations available
- ✅ SLAM with `slam_toolbox`
- ✅ Navigation 2 integration with selectable LiDAR source

## System Requirements

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Sim Harmonic

## Installation

### 1. Install ROS 2 Dependencies

```bash
sudo apt update
sudo apt install ros-jazzy-gazebo-ros2-control
sudo apt install ros-jazzy-xacro
sudo apt install ros-jazzy-robot-localization
sudo apt install ros-jazzy-ros2-controllers
sudo apt install ros-jazzy-ros2-control
sudo apt install ros-jazzy-velodyne
sudo apt install ros-jazzy-velodyne-description
sudo apt install ros-jazzy-slam-toolbox
sudo apt install ros-jazzy-pointcloud-to-laserscan
sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-bringup
sudo apt install ros-jazzy-nav2-navfn-planner
sudo apt install ros-jazzy-nav2-regulated-pure-pursuit-controller
```

### 2. Clone and Install CHAMP Controller and Go2 Simulation Packages

```bash
cd ~/ros2_ws/src
git clone https://github.com/khaledgabr77/unitree_go2_ros2
```

### 3. Install Dependencies

```bash
cd ~/ros2_ws
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

### 4. Build the Workspace

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

## Usage

### Gazebo Simulation

Launch the Gazebo simulation:

```bash
ros2 launch unitree_go2_sim unitree_go2_launch.py
```

![Unitree Go2 Simulation](docs/unitree_go2_sim.png)

[Watch Demo on YouTube](https://youtu.be/NUu7TaZhaQM)

### RVIZ Visualization

The package now includes both `Velodyne 3D LiDAR` and `4D Lidar L1` sensors. You can visualize the point cloud data in RVIZ:

Launch Gazebo with RVIZ:

```bash
ros2 launch unitree_go2_sim unitree_go2_launch.py rviz:=true
```

![RVIZ Visualization](docs/unitree_go2_vis.png)

**Velodyne Lidar and 4D Lidar L1**

![Velodyne Lidar and 4D Lidar L1](docs/1.png)

**Velodyne Lidar Beams**

![Velodyne Lidar Beams](docs/2.png)

**4D Lidar L1 Beams**

![4D Lidar L1 Beams](docs/3.png)

**Velodyne Lidar and 4D Lidar L1 Beams**

![Velodyne Lidar and 4D Lidar L1 Beams](docs/4.png)

**Mono Camera**

![Mono Camera](docs/camera.png)

### Teleoperation

Control the robot using keyboard:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### SLAM Mapping

Launch Gazebo, RViz, the point-cloud-to-laserscan adapter, and `slam_toolbox`:

```bash
ros2 launch unitree_go2_sim go2_slam_launch.py
```

To run SLAM without RViz, use the wrapper RViz argument:

```bash
ros2 launch unitree_go2_sim go2_slam_launch.py launch_rviz:=false
```

The SLAM launch defaults to the Unitree L1 LiDAR:

```bash
ros2 launch unitree_go2_sim go2_slam_launch.py lidar:=unitree_lidar
```

To map with the Velodyne point cloud instead:

```bash
ros2 launch unitree_go2_sim go2_slam_launch.py lidar:=velodyne_points
```

Drive the robot around while SLAM is running:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Save the map once it looks complete in RViz:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/go2_map
```

This creates `~/go2_map.yaml` and `~/go2_map.pgm`.

### Navigation

Launch Gazebo, RViz, AMCL, Nav2, and the LiDAR scan adapter with a saved map:

```bash
ros2 launch unitree_go2_sim go2_nav_launch.py map:=${HOME}/go2_map.yaml
```

The navigation launch also defaults to the Unitree L1 LiDAR. Use Velodyne by passing:

```bash
ros2 launch unitree_go2_sim go2_nav_launch.py map:=${HOME}/go2_map.yaml lidar:=velodyne_points
```

To run Nav2 without RViz:

```bash
ros2 launch unitree_go2_sim go2_nav_launch.py map:=${HOME}/go2_map.yaml launch_rviz:=false
```

Use RViz to set the initial pose with `2D Pose Estimate`, then send a goal with `2D Goal Pose`.

### Navigation Worlds

The base simulation launch accepts a full world file path:

```bash
ros2 launch unitree_go2_sim unitree_go2_launch.py world:=$(ros2 pkg prefix unitree_go2_description)/share/unitree_go2_description/worlds/walled_world.sdf
```

The SLAM and Nav2 launches default to `maze_world.sdf`. You can switch worlds the same way:

```bash
ros2 launch unitree_go2_sim go2_slam_launch.py world:=$(ros2 pkg prefix unitree_go2_description)/share/unitree_go2_description/worlds/default.sdf
```

Available worlds:

| World | Description |
|-------|-------------|
| `default.sdf` | Simple obstacle world with GPS origin metadata |
| `walled_world.sdf` | Small enclosed world with basic obstacles |
| `maze_world.sdf` | Narrow-corridor navigation test world |

### LiDAR Selection for SLAM and Nav2

Both SLAM and Nav2 consume `/scan`. The launch files create `/scan` from one of the simulated point clouds:

| Launch value | Input point cloud | Output |
|--------------|-------------------|--------|
| `lidar:=unitree_lidar` | `/unitree_lidar/points` | `/scan` |
| `lidar:=velodyne_points` | `/velodyne_points/points` | `/scan` |

`unitree_lidar` is the default.

The scan adapter filters in `base_footprint` height so floor returns are not
projected into `/scan`. The Unitree L1 uses `0.12..0.55 m`; the Velodyne uses
`0.25..0.70 m`. To tune these values, edit the heights directly in
`unitree_go2_sim/launch/pointcloud_to_scan_launch.py`.

### TF Stability

By default the simulation publishes a stable static `base_footprint -> base_link`
transform with `base_link_z:=0.225`. This keeps the RViz robot model from
bouncing while SLAM and Nav2 use the planar `base_footprint` frame.

To inspect the full dynamic body estimate instead, opt into the CHAMP body EKF:

```bash
ros2 launch unitree_go2_sim unitree_go2_launch.py dynamic_base_tf:=true
```

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

The world's GPS origin is defined in `unitree_go2_description/worlds/default.sdf` under `<spherical_coordinates>`. Edit `latitude_deg`, `longitude_deg`, and `elevation` to match your actual test site before running navigation experiments:

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

The gait configuration for the robot is found in `unitree_go2_sim/config/gait/gait.yaml`. You can modify the following parameters:

> **Nav2 and SLAM configuration** is in `unitree_go2_sim/config/nav/nav2.yaml` and `unitree_go2_sim/config/nav/slam.yaml` respectively.

| Parameter | Description |
|-----------|-------------|
| Knee Orientation | How the knees should be bent (.>> .>< .<< .<>) |
| Max Linear Velocity X | Maximum forward/reverse speed (m/s) |
| Max Linear Velocity Y | Maximum sideways speed (m/s) |
| Max Angular Velocity Z | Maximum rotational speed (rad/s) |
| Stance Duration | How long each leg spends on the ground while walking |
| Leg Swing Height | Trajectory height during swing phase (m) |
| Leg Stance Height | Trajectory depth during stance phase (m) |
| Robot Walking Height | Distance from hip to ground while walking (m) |
| CoM X Translation | Offset to compensate for weight distribution |
| Odometry Scaler | Multiplier to calculated velocities for dead reckoning |

![Velodyne Lidar and 4D Lidar L1](docs/image.png)

## Project Structure

- `champ/`: Core controllers and state estimation for CHAMP
- `unitree_go2_description/`: URDF models, meshes, and world files
- `unitree_go2_sim/`: Simulation, SLAM, Nav2 launch files, and configuration
  - `config/gait/` — gait tuning parameters
  - `config/joints/` — joint configuration
  - `config/links/` — link configuration
  - `config/nav/` — Nav2 (`nav2.yaml`) and SLAM (`slam.yaml`) parameters
  - `config/ros_control/` — ros2_control hardware interface config

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Acknowledgements

This project builds upon and incorporates work from the following projects:

* [Unitree Robotics](https://github.com/unitreerobotics/unitree_ros) - For the Go2 robot description (URDF model)
* [CHAMP](https://github.com/chvmp/champ) - For the quadruped controller framework
* [CHAMP Robots](https://github.com/chvmp/robots) - For robot configurations and setup examples
* [unitree-go2-ros2](https://github.com/anujjain-dev/unitree-go2-ros2) - ROS 2 package with gazebo classic

## License
