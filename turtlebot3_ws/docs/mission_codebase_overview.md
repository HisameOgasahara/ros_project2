# 미션 코드베이스 개요

이 문서는 현재 백업한 `turtlebot3_ws`가 어떤 미션을 수행하는지, 폴더 구조가 어떻게 되어 있는지, Jetson에서 어떤 순서로 실행하는지 정리한다.

## [A] 전체 그림: 앱 주문에서 로봇 완료까지

화살표는 앞 단계가 다음 단계로 명령이나 완료 신호를 보낸다는 뜻이다.

```text
사용자 휴대폰 user.html
  -> WebSocket ws://JETSON_IP:3000
rtreebot delivery_bridge_node.py
  -> /move_request
rtreebot delivery_ctrl.py
  -> Nav2 NavigateToPose
  -> /mediapipe/start 또는 /inference_switch
camera_ros 또는 mediapipe_hand_tracker
  -> /manipulator/motion_id
manipulator manipulatorCtrl.py
  -> /set_position
  -> /move_resume
rtreebot delivery_ctrl.py
  -> /move_finish
rtreebot delivery_bridge_node.py
  -> WebSocket robot_update
user.html
```

쉽게 말하면, 휴대폰에서 공구 배송이나 회수를 요청하면 Jetson의 ROS2 노드들이 로봇 이동, 카메라 인식, 로봇팔 동작, 완료 알림을 순서대로 처리한다.

## [A1] 미션: 웹앱 기반 공구 배송과 회수

미션은 `HOME`에서 대기하는 AMR+Manipulator 로봇이 사용자의 주문을 받아 방 A 또는 방 B로 공구를 배송하고, 사용이 끝난 공구를 다시 회수하는 시나리오다.

1. 사용자가 로봇 IP로 웹앱에 접속한다.
2. 지도에서 방 A 또는 방 B를 선택한다.
3. `driver`, `block`, `pen`, `wrench` 중 필요한 물품을 선택한다.
4. 주문 버튼을 누르면 요청이 대기열에 들어간다.
5. 로봇은 대기열 순서대로 목적지로 이동한다.
6. 배송 중인 물품과 로봇 위치가 웹앱에 표시된다.
7. 배송이 끝난 물품은 사용 완료 또는 회수 요청 상태로 바뀐다.
8. 회수 요청도 대기열에 들어가고 로봇이 순서대로 처리한다.
9. 끝난 요청은 완료 목록에 남는다.

## [A2] 요청 형식

웹앱은 WebSocket으로 JSON을 보내고, 브릿지 노드는 ROS2 문자열 토픽으로 바꾼다.

| 요청 | WebSocket action | ROS2 `/move_request` 예시 | 의미 |
|---|---|---|---|
| 배송 | `create_order` | `A_driver_call` | A 방으로 driver 배송 |
| 배송 | `create_order` | `B_pen_call` | B 방으로 pen 배송 |
| 회수 | `retrieve_item` | `A_driver_recall` | A 방에서 driver 회수 |
| 회수 | `retrieve_item` | `B_wrench_recall` | B 방에서 wrench 회수 |

허용 값은 방 `A`, `B`, 물품 `driver`, `block`, `pen`, `wrench`, 모드 `call`, `recall`이다.

## [B] 현재 백업 구조

```text
turtlebot3_ws/
  src/
    camera_ros/
    dynamixel_sdk/
    dynamixel_sdk_custom_interfaces/
    dynamixel_sdk_examples/
    manipulator/
    mediapipe_hand_tracker/
    patrol_robot/
    rtreebot/
    sllidar_ros2/
    turtlebot3/
    turtlebot3_msgs/
    turtlebot3_simulations/
    user_interfaces/
  maps/
    map_6f.yaml
    map_6f.pgm
  docs/
    external_dependencies.md
    known_path_issues.md
    mission_codebase_overview.md
```

## [B1] 패키지 역할

| 패키지 | 분류 | 역할 |
|---|---|---|
| `rtreebot` | 최종 미션 | 웹 주문 브릿지와 Nav2 배송/회수 제어 |
| `camera_ros` | 최종 미션 | CSI 카메라 발행과 DetectNet 결과 발행 |
| `mediapipe_hand_tracker` | 최종 미션 | 손동작 확인 뒤 매니퓰레이터 모션 시작 |
| `manipulator` | 최종 미션 | Dynamixel 로봇팔 GUI 티칭과 저장 모션 재생 |
| `dynamixel_sdk` | 장비 의존 코드 | Dynamixel 통신 SDK ROS 패키지 |
| `dynamixel_sdk_custom_interfaces` | 장비 의존 코드 | `/set_position`, `/set_torque`, `/get_position` 인터페이스 |
| `dynamixel_sdk_examples` | 장비 의존 코드 | 실제 Dynamixel read/write 노드 |
| `sllidar_ros2` | 로봇 기반 코드 | LiDAR scan 발행 |
| `turtlebot3` | 로봇 기반 코드 | TurtleBot3 bringup, navigation2, description |
| `turtlebot3_msgs` | 로봇 기반 코드 | TurtleBot3 메시지 |
| `turtlebot3_simulations` | 시뮬레이션 | Gazebo 기반 TurtleBot3 시뮬레이션 |
| `patrol_robot` | 중간 실습 | Nav2 waypoint 이동 테스트 |
| `user_interfaces` | 중간 실습 | ROS2 custom msg/srv/action 실습 기록 |

## [B2] `rtreebot` 내부 구조

```text
turtlebot3_ws/src/rtreebot/
  package.xml
  setup.py
  setup.cfg
  resource/
    rtreebot
  rtreebot/
    __init__.py
    delivery_bridge_node.py
    delivery_ctrl.py
  web/
    user.html
  docs/
    communication_test.md
    warning.md
```

`rtreebot`은 `reference/src/src`에 패키지 폴더로 남아 있던 코드가 아니라 날짜별 백업에서 복원한 최종 미션 코드다.

## [C] 런타임 패키지 흐름

화살표는 런타임 데이터가 흐르는 방향이다.

```text
rtreebot
  delivery_bridge_node.py
    -> publishes /move_request
    <- subscribes /move_finish

rtreebot
  delivery_ctrl.py
    <- subscribes /move_request
    -> sends Nav2 NavigateToPose goals
    -> publishes /mediapipe/start for delivery
    -> publishes /inference_switch for recall
    <- subscribes /move_resume
    -> publishes /move_finish

camera_ros
  publisher.py
    -> publishes /camera and /detectnet/result
    <- subscribes /inference_switch

mediapipe_hand_tracker
  hand_tracker_node.py
    <- subscribes /camera and /mediapipe/start
    -> publishes /manipulator/motion_id

manipulator
  manipulatorCtrl.py
    <- subscribes /manipulator/motion_id
    -> publishes /set_position and /move_resume
```

## [C1] 핵심 패키지 동작

| 패키지 | 동작 |
|---|---|
| `rtreebot` | WebSocket 요청을 `/move_request`로 바꾸고, Nav2 이동과 완료 신호를 관리 |
| `camera_ros` | `/camera`를 발행하고, 회수 모드에서 `/detectnet/result`를 발행 |
| `mediapipe_hand_tracker` | `/mediapipe/start` 이후 손동작을 확인해 `/manipulator/motion_id` 발행 |
| `manipulator` | `saved_motions.json`을 읽어 Dynamixel ID 11~15에 `/set_position` 발행 |
| `patrol_robot` | 최종 미션 전 waypoint 이동 검증에 사용한 중간 실습 코드 |

물품별 `motion_id`는 다음과 같다.

| 물품 | motion_id |
|---|---:|
| `block` | 1 |
| `wrench` | 2 |
| `driver` | 3 |
| `pen` | 4 |

## [D] Git에 포함한 리소스

| 경로 | 원본 | 크기 | 용도 |
|---|---|---:|---|
| `turtlebot3_ws/maps/map_6f.yaml` | `reference/map_candidates/map_6f.yaml` | 125B | Navigation2 지도 설정 |
| `turtlebot3_ws/maps/map_6f.pgm` | `reference/map_candidates/map_6f.pgm` | 193565B | 6층 기준 지도 이미지 |
| `turtlebot3_ws/src/manipulator/manipulator/saved_motions.json` | `reference/src/src/manipulator/manipulator/saved_motions.json` | 4580B | 실제 매니퓰레이터 모션 |
| `turtlebot3_ws/src/manipulator/manipulator/saved_motions_1.json` | `reference/src/src/manipulator/manipulator/saved_motions_1.json` | 1148B | 보조 매니퓰레이터 모션 백업 |
| `turtlebot3_ws/src/camera_ros/camera_ros/labels.txt` | `reference/src/src/camera_ros/camera_ros/labels.txt` | 42B | 객체 인식 클래스 이름 |
| `turtlebot3_ws/src/camera_ros/camera_ros/ssd-mobilenet.onnx.sha256sum` | `reference/src/src/camera_ros/camera_ros/ssd-mobilenet.onnx.sha256sum` | 65B | 모델 파일 검증용 checksum |

## [E] Jetson 실행 순서

### 터미널 1: HTML 서버

```bash
cd ~/turtlebot3_ws/src/rtreebot/web
python3 -m http.server 8000 --bind 0.0.0.0
```

폰에서는 아래 주소로 접속한다.

```text
http://JETSON_IP:8000/user.html
```

### 터미널 2: Robot Bringup

```bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_bringup robot.launch.py
```

### 터미널 3: Navigation2

```bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_navigation2 navigation2.launch.py map:=$HOME/turtlebot3_ws/maps/map_6f.yaml
```

### 터미널 4: WebSocket/ROS 브릿지

```bash
ros2 run rtreebot delivery_bridge
```

### 터미널 5: 배송 제어

```bash
ros2 run rtreebot delivery_ctrl
```

### 터미널 6: 카메라와 인식

```bash
ros2 run camera_ros publisher
```

배송 손동작 인식을 같이 쓸 때:

```bash
ros2 run mediapipe_hand_tracker hand_tracker_node
```

### 터미널 7: 매니퓰레이터

```bash
ros2 launch manipulator manipulatorCtrl.launch.py
```

토픽 확인:

```bash
ros2 topic echo /move_request
ros2 topic echo /move_resume
ros2 topic echo /move_finish
ros2 topic echo /detectnet/result
```

HOME 복귀 트리거:

```bash
ros2 topic pub --once /move_resume std_msgs/Bool "data: true"
```

## [F] PDF와 실제 코드의 차이

| 항목 | PDF/이미지 기준 | 실제 코드 백업 기준 |
|---|---|---|
| 방 | HOME, A 중심 설명 뒤 B 추가 미션 | `delivery_ctrl.py`에 A/B/HOME 좌표 존재 |
| 브릿지 파일명 | `websocket.py`처럼 설명된 페이지가 있음 | 실제 핵심 파일은 `delivery_bridge_node.py` |
| 로봇팔 모션 수 | PDF 기준 9개 모션 계획 | 실제 `saved_motions.json`은 4개 모션 |
| 회수 인식 | 회수 요청 흐름과 `/inference_switch` 설명 | `/item_detector/start`는 코드 흔적만 있고 구독 노드는 없음 |
| `rtreebot` 패키지 | PDF에 패키지 구조 제시 | 날짜별 백업 파일에서 복원한 코드가 기준 |

## [G] 문서 구성

| 문서 | 역할 |
|---|---|
| `turtlebot3_ws/docs/mission_codebase_overview.md` | 미션, 코드 구조, 포함 리소스, 실행 순서 |
| `turtlebot3_ws/docs/external_dependencies.md` | 외부에서 받아야 할 코드, 모델, 시스템 의존성 |
| `turtlebot3_ws/docs/known_path_issues.md` | 현재 백업 구조와 하드코딩 경로 차이 |
