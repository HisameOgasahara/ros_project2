# 외부에서 가져와야 할 코드와 리소스

이 문서는 현재 백업에 포함된 `turtlebot3_ws`를 Jetson에서 재현할 때, 외부에서 받아야 하거나 별도 설치해야 하는 항목을 정리한다.

## 기준

`external_repos.repos` 확인 기준:

출처:

```text
https://github.com/EchidnaRezero/ros2_practice_robot/blob/main/external_repos.repos
```

```yaml
repositories:
  src/turtlebot3:
    type: git
    url: https://github.com/Robot-tree/2026_amrManipulator.git
    version: turtlebot3
  src/turtlebot3_msgs:
    type: git
    url: https://github.com/Robot-tree/2026_amrManipulator.git
    version: turtlebot3_msgs
  src/sllidar_ros2:
    type: git
    url: https://github.com/Slamtec/sllidar_ros2.git
    version: main
```

## `external_repos.repos`에서 확인되는 항목

| 경로 | 외부 저장소 | 브랜치 |
|---|---|---|
| `src/turtlebot3` | `https://github.com/Robot-tree/2026_amrManipulator.git` | `turtlebot3` |
| `src/turtlebot3_msgs` | `https://github.com/Robot-tree/2026_amrManipulator.git` | `turtlebot3_msgs` |
| `src/sllidar_ros2` | `https://github.com/Slamtec/sllidar_ros2.git` | `main` |

현재 백업에는 위 세 항목의 소스가 이미 `turtlebot3_ws/src` 아래에 포함되어 있다.

## `external_repos.repos`에는 없지만 현재 백업에 포함한 항목

| 경로 | 성격 | 포함한 이유 |
|---|---|---|
| `src/turtlebot3_simulations` | TurtleBot3 시뮬레이션 패키지 | 문서 구조와 수업 백업 구조에 맞춤 |
| `src/dynamixel_sdk` | Dynamixel SDK ROS 패키지 | 크기가 작고 매니퓰레이터 재현에 필요 |
| `src/dynamixel_sdk_custom_interfaces` | Dynamixel custom msg/srv | `SetPosition.runtime`, `SetTorque`, `GetPosition` 사용 |
| `src/dynamixel_sdk_examples` | Dynamixel read/write 노드 | `read_write_node_omx.py`가 실제 매니퓰레이터 제어에 사용됨 |
| `src/rtreebot` | 미션용 웹-ROS2-Nav2 제어 패키지 | 날짜별 백업에서 복원한 최종 미션 코드 |
| `src/camera_ros` | 카메라/DetectNet 노드 | `/camera`, `/detectnet/result` 발행 |
| `src/mediapipe_hand_tracker` | 손동작 인식 노드 | `/mediapipe/start`와 `/manipulator/motion_id` 연결 |
| `src/manipulator` | 로봇팔 GUI/제어 패키지 | 저장 모션 실행과 `/move_resume` 발행 |
| `src/patrol_robot` | Nav2 waypoint 테스트 | 좌표 검증용 중간 실습 코드 |
| `src/user_interfaces` | custom interface 실습 | 수업 기록 보존 |

## 별도 다운로드가 필요한 모델 리소스

| 파일 | 배치 위치 | 출처 |
|---|---|---|
| `ssd-mobilenet.onnx` | `turtlebot3_ws/src/camera_ros/camera_ros/ssd-mobilenet.onnx` | Hugging Face `pomupomu2/ros2`에서 다운로드 |
| `ssd-mobilenet.onnx.1.1.8001.GPU.FP16.engine` | `turtlebot3_ws/src/camera_ros/camera_ros/` | Jetson에서 ONNX 실행 시 생성되는 TensorRT 캐시 |

`ssd-mobilenet.onnx`는 Git 리포에는 포함하지 않는다. 모델 관련 파일은 Hugging Face `pomupomu2/ros2`에서 받아 `camera_ros/camera_ros/` 아래에 둔다.

현재 백업에는 `ssd-mobilenet.onnx.sha256sum`과 `labels.txt`만 포함되어 있다.

## 실제 코드에는 있지만 필수 여부가 낮은 항목

| 항목 | 현재 상태 | 영향 |
|---|---|---|
| `src/item_detector` | Jetson Downloads에서 가져와 포함 | 회수 시 `/item_detector/start`를 받아 `/detectnet/result`와 연결 |

현재 기준에서 `/item_detector/start`는 회수 흐름에 포함된다. `delivery_ctrl.py`는 recall 도착 후 `/inference_switch=True`와 `/item_detector/start=True`를 발행하고, `item_detector`는 Jetson에서 가져온 패키지를 `work_ref_jetson_ready`에 포함했다.

item-motion 기준:

```text
block  -> 1
wrench -> 2
driver -> 3
pen    -> 4
```

## apt 또는 ROS 패키지로 필요한 항목

| 항목 | 용도 |
|---|---|
| ROS2 Galactic | Jetson 실행 기준 ROS2 배포판 |
| `python3-colcon-common-extensions` | `colcon build` |
| `ros-galactic-navigation2` | Nav2 실행 |
| `ros-galactic-nav2-bringup` | Navigation2 bringup launch |
| `ros-galactic-cartographer` | SLAM 재현 시 필요 |
| `ros-galactic-cartographer-ros` | Cartographer ROS 연동 |
| `ros-galactic-gazebo-*` | Gazebo 시뮬레이션 재현 시 필요 |
| `rosidl_default_generators` | `user_interfaces`, `dynamixel_sdk_custom_interfaces` 빌드 |
| `ament_cmake` | CMake 기반 ROS2 패키지 빌드 |

## Python 또는 Jetson Python 환경

| 항목 | 설치 위치 | 용도 |
|---|---|---|
| `websockets` | 기본 Python 또는 ROS2 실행 Python | `rtreebot.delivery_bridge_node` |
| `opencv-python` | `/home/jetson/mp_env` 또는 실행 Python | 영상 처리 |
| `numpy` | `/home/jetson/mp_env` 또는 실행 Python | 영상 배열 처리 |
| `mediapipe==0.10.9` | `/home/jetson/mp_env` | `mediapipe_hand_tracker` |
| `jetson_inference` | Jetson 환경 | `camera_ros.publisher` DetectNet |
| `jetson_utils` | Jetson 환경 | CSI 카메라 입력 |

`mediapipe_hand_tracker/hand_tracker_node.py`는 `/home/jetson/mp_env/bin/python3`를 shebang으로 사용한다.

Jetson Inference 원본:

```text
https://github.com/dusty-nv/jetson-inference
```

## 하드웨어와 로컬 설정

| 항목 | 용도 |
|---|---|
| CSI 카메라 | `camera_ros.publisher` 입력 |
| LiDAR 포트 | `sllidar_ros2` 실행 |
| TurtleBot3 base 포트 | `/dev/ttyRtreeCon` |
| LiDAR 포트 | `/dev/ttyLidar` |
| OpenRB/Dynamixel 포트 | `/dev/ttyManipCon` |
| udev rules | 포트 이름 고정 |
| GitHub Pages UI | `https://hisameogasahara.github.io/ros_webclient/` |
| Cloudflare quick tunnel WSS | `start_mission_tmux.sh` 실행 후 UI에 입력 |

## 문서 역할

| 문서 | 역할 |
|---|---|
| `turtlebot3_ws/docs/external_dependencies.md` | 외부에서 받아야 할 코드, 모델, 시스템 의존성 |
| `turtlebot3_ws/docs/mission_codebase_overview.md` | 미션, 코드 구조, 포함 리소스, 실행 순서 |
| `turtlebot3_ws/docs/known_path_issues.md` | 현재 백업 구조와 하드코딩 경로 차이 |
