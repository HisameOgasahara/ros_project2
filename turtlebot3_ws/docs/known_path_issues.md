# 경로 확인 이슈

이 문서는 현재 백업 구조와 실제 코드 안의 하드코딩 경로가 다른 부분을 기록한다. 목표는 리팩토링이 아니라 재현 백업이므로, 코드는 그대로 두고 실행 전에 확인할 지점만 남긴다.

## 하드코딩 경로

| 파일 | 현재 코드의 경로 | 현재 백업 구조 기준 |
|---|---|---|
| `turtlebot3_ws/src/manipulator/launch/manipulatorCtrl.launch.py` | `/home/jetson/turtlebot3_ws/src/DynamixelSDK/ros/dynamixel_sdk_examples/src/read_write_node_omx.py` | `~/turtlebot3_ws/src/dynamixel_sdk_examples/src/read_write_node_omx.py` |
| `turtlebot3_ws/src/manipulator/launch/manipulatorGUI.launch.py` | `/home/jetson/turtlebot3_ws/src/DynamixelSDK/ros/dynamixel_sdk_examples/src/read_write_node_omx.py` | `~/turtlebot3_ws/src/dynamixel_sdk_examples/src/read_write_node_omx.py` |
| `turtlebot3_ws/src/camera_ros/camera_ros/publisher.py` | `/home/jetson/turtlebot3_ws/src/camera_ros/camera_ros/` | `~/turtlebot3_ws/src/camera_ros/camera_ros/` |
| `turtlebot3_ws/src/mediapipe_hand_tracker/mediapipe_hand_tracker/hand_tracker_node.py` | `/home/jetson/mp_env/...` | Jetson의 `mp_env` 존재 여부 확인 |

## 고정값

| 파일 | 값 | 확인 내용 |
|---|---|---|
| `turtlebot3_ws/src/rtreebot/web/user.html` | `ws://10.59.121.144:3000` | 실제 Jetson IP로 변경 |
| `turtlebot3_ws/src/manipulator/launch/*.launch.py` | `/dev/ttyManipCon` | udev symlink 존재 확인 |
| `turtlebot3_ws/src/turtlebot3/turtlebot3_bringup/launch/robot.launch.py` | `/dev/ttyRtreeCon`, `/dev/ttyLidar` | udev symlink 존재 확인 |
| `turtlebot3_ws/src/camera_ros/camera_ros/publisher.py` | `CAMERA_INPUT_URI` 기본 `csi://0` | IMX219 CSI와 `nvargus-daemon` 상태 확인 |

## 처리 기준

현재 작업 트리는 Jetson 실사용 기준으로 정리되어 있다. 실행이 막히면 위 경로를 먼저 확인하고, Jetson-only 모델/지도/가상환경은 삭제식 덮어쓰기 대상에서 제외한다.
