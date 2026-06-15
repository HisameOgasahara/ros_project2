#!/usr/bin/env bash
set -euo pipefail

WS_PORT="${WS_PORT:-3000}"
ROS_DISTRO_SETUP="${ROS_DISTRO_SETUP:-/opt/ros/galactic/setup.bash}"
WORKSPACE_SETUP="${WORKSPACE_SETUP:-$HOME/turtlebot3_ws/install/setup.bash}"

if [ -f "$ROS_DISTRO_SETUP" ]; then
  # shellcheck disable=SC1090
  source "$ROS_DISTRO_SETUP"
fi

if [ -f "$WORKSPACE_SETUP" ]; then
  # shellcheck disable=SC1090
  source "$WORKSPACE_SETUP"
else
  echo "Workspace setup file not found: $WORKSPACE_SETUP" >&2
  exit 1
fi

echo "Starting ROS2 delivery bridge on ws://0.0.0.0:${WS_PORT}"
ros2 run rtreebot delivery_bridge --ros-args -p ws_port:="$WS_PORT"

