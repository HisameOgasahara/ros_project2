#!/usr/bin/env bash
set -euo pipefail

SESSION="${SESSION:-rtree-mission}"
WORKSPACE_DIR="${WORKSPACE_DIR:-$HOME/turtlebot3_ws}"
ROS_DISTRO_SETUP="${ROS_DISTRO_SETUP:-/opt/ros/galactic/setup.bash}"
WORKSPACE_SETUP="${WORKSPACE_SETUP:-$WORKSPACE_DIR/install/setup.bash}"
ZERO_COUNT="${ZERO_COUNT:-10}"

source_ros() {
  cd "$WORKSPACE_DIR"
  # shellcheck disable=SC1090
  source "$ROS_DISTRO_SETUP"
  # shellcheck disable=SC1090
  source "$WORKSPACE_SETUP"
}

publish_zero_cmd_vel() {
  source_ros
  echo "Publishing zero /cmd_vel ${ZERO_COUNT} times..."
  for _ in $(seq 1 "$ZERO_COUNT"); do
    ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
      "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" \
      >/dev/null 2>&1 || true
    sleep 0.1
  done
  echo "Zero /cmd_vel sent."
}

send_ctrl_c() {
  local window_name="$1"
  if tmux list-windows -t "$SESSION" -F '#W' 2>/dev/null | grep -qx "$window_name"; then
    tmux send-keys -t "$SESSION:$window_name" C-c
    echo "Sent Ctrl-C to tmux window: $window_name"
  else
    echo "Window not found, skipped: $window_name"
  fi
}

stop_motion_stack() {
  publish_zero_cmd_vel
  send_ctrl_c nav
  send_ctrl_c bringup
  echo
  echo "Motion stack stop requested. bridge/mission/vision/manipulator windows are still alive."
}

stop_all() {
  publish_zero_cmd_vel
  echo "Stopping all mission tmux windows..."
  tmux kill-session -t "$SESSION" 2>/dev/null || true
}

while true; do
  clear
  cat <<EOF
=== SAFETY CONTROL ===

1) Stop bringup/nav motion
2) Stop all mission tmux
q) Quit this safety menu only

Session: $SESSION
EOF
  printf '\nSelect: '
  read -r choice

  case "$choice" in
    1)
      stop_motion_stack
      printf '\nPress Enter to return to menu...'
      read -r _
      ;;
    2)
      stop_all
      exit 0
      ;;
    q|Q)
      exit 0
      ;;
    *)
      echo "Unknown choice: $choice"
      sleep 1
      ;;
  esac
done
