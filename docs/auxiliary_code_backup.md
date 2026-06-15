# 보조 코드 백업 구조

이 문서는 `auxiliary_code_backup/`에 따로 보관한 테스트, 보조, 디버깅, 훈련, 추론, XAI 코드를 설명한다.

## 전체 구조

```text
auxiliary_code_backup/
  ai_training_xai/
    dataset_tools/
    object_training/
    onnx_gradcam/
    ssd_reference/
  manipulation_teaching/
  network_connectivity/
```

## 폴더별 역할

| 폴더 | 원본 | 역할 |
|---|---|---|
| `ai_training_xai/dataset_tools/` | `reference/git_code/26_06_05/cvExtend`, `26_06_07/augmentation_source` | VOC/XML 변환, train/val 분리, 데이터 증강 |
| `ai_training_xai/object_training/` | `reference/git_code/26_06_07` | Colab 학습, ONNX 변환, 데이터셋 감사, Grad-CAM 실행 스크립트 |
| `ai_training_xai/onnx_gradcam/` | `reference/git_code/26_06_08` | ONNX 추론과 Grad-CAM 확인 노트북 |
| `ai_training_xai/ssd_reference/` | `reference/git_code/26_06_05/github_code_study_backup` | SSD 학습/추론/XAI 외부 참고 코드 |
| `manipulation_teaching/` | `reference/git_code/26_06_05/2026_robot-manipulator/docs`, `26_06_09` | 매니퓰레이터 티칭 문서, Dynamixel limit 확인, 조작 메모 |
| `network_connectivity/` | `reference/git_code/26_06_12/phone_jetson_ws_test` | 휴대폰과 Jetson WebSocket 연결 테스트 |

## 사용 기준

`turtlebot3_ws/`는 실제 Jetson 미션 재현용 코드다. `auxiliary_code_backup/`는 미션 개선, 디버깅, 모델 훈련/추론, 장비 튜닝에 이어지는 코드만 둔다.

`turtlebot3_ws/`에 이미 같은 내용으로 들어간 파일은 이 폴더에서 제외한다.

ROS2 토픽, 서비스, 액션 기초 실습처럼 미션 보조와 직접 관련이 낮은 예제는 이 폴더에 두지 않는다.

미션 설명, waypoint 메모, 실행 순서처럼 문서로 충분한 내용은 `turtlebot3_ws/docs/mission_codebase_overview.md`에서 관리한다.

날짜만 의미하는 중간 폴더는 두지 않는다. `ssd_reference/` 아래의 `mbnet/`, `pytorch-ssd/`는 코드 import 구조 때문에 보존한다.

`ai_training_xai/ssd_reference/`에는 SSD 학습과 Grad-CAM 확인을 위해 가져온 외부 참고 코드 성격의 파일이 포함되어 있다.

모델 파일, 훈련 데이터셋, zip 원본 백업은 Git에 포함하지 않는다. 필요한 모델은 `turtlebot3_ws/docs/external_dependencies.md`의 Hugging Face 안내를 따른다.

## 주요 연결 문서

| 문서 | 내용 |
|---|---|
| `turtlebot3_ws/docs/mission_codebase_overview.md` | 실제 미션 코드베이스, 구조, 실행 순서 |
| `turtlebot3_ws/docs/external_dependencies.md` | 외부 코드, 모델, 시스템 의존성 |
| `turtlebot3_ws/docs/known_path_issues.md` | 하드코딩 경로와 현재 백업 구조 차이 |
