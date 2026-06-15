#!/usr/bin/env python3

import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool, Int32


class ItemDetectorNode(Node):
    def __init__(self):
        super().__init__("item_detector_node")

        # 활성화 상태
        self.active = False

        # 클래스 카운트 초기화
        self.reset_counts()

        # 시작 신호 구독
        self.create_subscription(
            Bool,
            "/item_detector/start",
            self.start_callback,
            10
        )

        # detectnet 결과 구독
        self.create_subscription(
            String,
            "/detectnet/result",
            self.result_callback,
            10
        )
        
        # publisher for manipulator
        self.manipulator_pub = self.create_publisher(
            Int32, "/manipulator/motion_id", 10
        )
        
        self.get_logger().info("Item Detector Node 시작. /item_detector/start 대기 중...")


    # -----------------------------
    # 카운트 초기화 함수
    # -----------------------------
    def reset_counts(self):
        self.pen_count = 0
        self.driver_count = 0
        self.wrench_count = 0
        self.block_count = 0


    # -----------------------------
    # 시작 토픽 콜백
    # -----------------------------
    def start_callback(self, msg: Bool):
        if msg.data:
            self.get_logger().info("아이템 감지 시작")
            self.active = True
            self.reset_counts()
        else:
            self.get_logger().info("아이템 감지 중지")
            self.active = False


    # -----------------------------
    # detectnet 결과 콜백
    # -----------------------------
    def result_callback(self, msg: String):

        # 활성화 상태가 아니면 무시
        if not self.active:
            return

        try:
            detections = json.loads(msg.data)
        except Exception as e:
            self.get_logger().error(f"JSON 파싱 오류: {e}")
            return

        # 클래스별 카운트 증가
        for obj in detections:
            class_name = obj.get("class", "")

            if class_name == "pen":
                self.pen_count += 1
            elif class_name == "driver":
                self.driver_count += 1
            elif class_name == "block":
                self.block_count += 1
            elif class_name == "wrench":
                self.wrench_count += 1
            
        # 임계값 확인
        self.check_threshold()


    # -----------------------------
    # 임계값 검사
    # -----------------------------
    def check_threshold(self):
        threshold = 3
        motion_id = 0
        if self.pen_count > threshold:
            self.trigger_detected("pen")
        elif self.driver_count > threshold:
            self.trigger_detected("driver")
        elif self.block_count > threshold:
            self.trigger_detected("block")
        elif self.wrench_count > threshold:
            self.trigger_detected("wrench")
        
    # -----------------------------
    # 감지 완료 처리
    # -----------------------------
    def trigger_detected(self, class_name):
        self.get_logger().info(f"{class_name} detected over 10")
        motion_id = 0
        if class_name == "block": motion_id = 1
        elif class_name == "wrench": motion_id = 2
        elif class_name == "driver": motion_id = 3
        elif class_name == "pen": motion_id = 4
        self.manipulator_pub.publish(Int32(data=motion_id))
        # 초기화
        self.reset_counts()
        self.active = False

        self.get_logger().info("Initialized, waiting /item_detector/start ...")


def main():
    rclpy.init()
    node = ItemDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
