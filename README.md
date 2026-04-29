# 🤖 MY_robot — ROS 2 + Ignition Gazebo Simulation

> A fully simulated robot built with ROS 2 (Humble) and Ignition Gazebo (Fortress), featuring a SolidWorks-designed model exported to URDF/SDF, PID control, and ROS-based teleoperation.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#-project-structure)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Build](#️-build)
- [Usage](#-usage)
- [Notes & Troubleshooting](#-notes--troubleshooting)
- [Features](#-features)

---

## Overview

This project simulates a robot in Ignition Gazebo, bridged with ROS 2. The robot was designed in **SolidWorks** and exported to URDF/SDF for simulation. It includes launch files for simulation and visualization, a PID-based controller, and a teleoperation node.

---

## 📁 Project Structure

```
MY_robot/
├── solidworks_files/              # Original SolidWorks CAD model (.SLDPRT / .SLDASM)
│                                  # Used to generate the robot URDF via sw_urdf_exporter
└── src/
    └── my_robot/
        ├── config/                    # ROS 2 parameter configs
        ├── launch/
        │   ├── main_gazebo.launch.py  # Master launch (sim + bridge + rviz)
        │   ├── robot_gazebo.launch.py # Spawn robot in Gazebo
        │   ├── bridge.launch.py       # ROS–Ignition topic bridge
        │   └── rviz.launch.py         # RViz2 visualization
        ├── meshes/                    # 3D mesh assets
        ├── scripts/
        │   ├── pid_controller.py      # PID-based motion controller
        │   └── teleop_controller.py   # Keyboard teleoperation node
        ├── urdf/                      # Robot URDF/SDF model
        └── world/                     # Gazebo world files
```

---

## 📦 Requirements

| Dependency | Version | Install |
|---|---|---|
| ROS 2 | Humble | `sudo apt install ros-humble-desktop` |
| Ignition Gazebo | Fortress | `sudo apt install ignition-fortress` |
| ROS–Ignition Bridge | — | `sudo apt install ros-humble-ros-ign` |
| colcon | latest | `sudo apt install python3-colcon-common-extensions` |

> **OS:** Ubuntu 22.04 is recommended for ROS 2 Humble + Ignition Fortress compatibility.

---

## 🔧 Installation

### 1. Install ROS 2 Humble

```bash
sudo apt update
sudo apt install ros-humble-desktop
source /opt/ros/humble/setup.bash
```

To avoid sourcing manually every session, add it to your shell profile:

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
```

### 2. Install Ignition Gazebo (Fortress)

```bash
sudo apt install ignition-fortress
```

### 3. Install the ROS–Ignition Bridge

```bash
sudo apt install ros-humble-ros-ign
```

### 4. Install colcon Build Tool

```bash
sudo apt install python3-colcon-common-extensions
```

---

## 🛠️ Build

Navigate to the workspace root and build with colcon:

```bash
cd ~/ROS_PROJECT/MY_robot
colcon build
```

Then source the workspace overlay:

```bash
source install/setup.bash
```

> **Tip:** Add `source ~/ROS_PROJECT/MY_robot/install/setup.bash` to your `~/.bashrc` to auto-source on every terminal session.

---

## 🚀 Usage

Run each command in a **separate terminal**, with the workspace sourced in each one.

### Step 1 — Launch the Simulation

```bash
ros2 launch my_robot main_gazebo.launch.py
```

### Step 2 — Start the ROS–Ignition Bridge

```bash
ros2 launch my_robot bridge.launch.py
```

### Step 3 — Run the Teleoperation Controller

```bash
ros2 run my_robot teleop_controller
```

---

## 🔍 Notes & Troubleshooting

### Gazebo fails to launch (WSL / headless / virtual machine)

If you're running inside WSL or a system without a proper GPU, Gazebo may fail due to graphics rendering issues. Use software rendering as a workaround:

```bash
LIBGL_ALWAYS_SOFTWARE=1 QT_QPA_PLATFORM=xcb ros2 launch my_robot main_gazebo.launch.py
```

### Always source before running

Every new terminal session needs the workspace sourced:

```bash
source /opt/ros/humble/setup.bash
source ~/ROS_PROJECT/MY_robot/install/setup.bash
```

### Rebuild after making changes

If you modify any source files, rebuild before running:

```bash
colcon build --symlink-install
source install/setup.bash
```

---

## ✨ Features

- 🌍 **Ignition Gazebo simulation** — physics-based robot environment using Fortress
- 🦾 **SolidWorks CAD model** — robot designed in SolidWorks and exported to URDF via `sw_urdf_exporter`
- 📐 **Custom URDF/SDF** — simulation-ready robot model with joints, links, and inertial properties
- 🎛️ **PID controller** — closed-loop motion control via ROS 2 node
- 🕹️ **Teleoperation** — keyboard-based robot driving over ROS 2 topics
- 🔗 **ROS–Ignition bridge** — bidirectional topic translation between ROS 2 and Ignition
- 📊 **RViz2 visualization** — real-time robot state and sensor display

---
