cmake_minimum_required(VERSION 3.5)
project(my_robot)

# Default to C++14 (optional but recommended)
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

# Find ament
find_package(ament_cmake REQUIRED)

# Install directories (same idea, different variable)
install(
  DIRECTORY config launch meshes urdf world
  DESTINATION share/${PROJECT_NAME}
)
install(PROGRAMS
  scripts/teleop_controller.py
  scripts/pid_controller.py
  DESTINATION lib/${PROJECT_NAME}
)

# Required for ROS 2 packages
ament_package()