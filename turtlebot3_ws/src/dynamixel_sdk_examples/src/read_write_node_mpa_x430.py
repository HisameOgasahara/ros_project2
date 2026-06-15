#!/usr/bin/env python3

# Copyright 2021 ROBOTIS CO., LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Wonho Yun, Will Son

# 내가 보는 코드 정리용
# send value : ros2 topic pub -1 /set_position dynamixel_sdk_custom_interfaces/SetPosition "{id: 1, position: 4000}"
# read value : ros2 service call /get_position dynamixel_sdk_custom_interfaces/srv/GetPosition "{id: 1}"
# run : asilia@ubuntu:~/colcon_ws/src/DynamixelSDK/ros/dynamixel_sdk_examples/src$ python read_write_node.py 

from dynamixel_sdk import COMM_SUCCESS
from dynamixel_sdk import PacketHandler
from dynamixel_sdk import PortHandler
from dynamixel_sdk_custom_interfaces.msg import SetPosition, SetTorque
from dynamixel_sdk_custom_interfaces.srv import GetPosition
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
from std_msgs.msg import Bool

# Control table address
ADDR_OPERATING_MODE = 11  # Control table address is different in Dynamixel model
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_POSITION = 132
ADDR_PROFILE_VELOCITY = 112
ADDR_PROFILE_ACCELERATION = 108
ADDR_DRIVE_MODE = 10

# Protocol version
PROTOCOL_VERSION = 2.0  # Default Protocol version of DYNAMIXEL X series.

# Default settings
DXL_IDS = [11, 12, 13, 14, 15, 16]      # [11, 12, 13, 14, 15] for open manipulator x
BAUDRATE = 1000000  # Dynamixel default baudrate : 57600
DEVICE_NAME = '/dev/ttyACM0'  # Check which port is being used on your controller

TORQUE_ENABLE = 1  # Value for enabling the torque
TORQUE_DISABLE = 0  # Value for disabling the torque
POSITION_CONTROL = 3  # Value for position control mode


class ReadWriteNode(Node):

    def __init__(self):
        super().__init__('read_write_node')

        # 먼저 포트 핸들러와 패킷 핸들러 초기화
        self.port_handler = PortHandler(DEVICE_NAME)
        self.packet_handler = PacketHandler(PROTOCOL_VERSION)
        print('\n=============Now Starting Dynamixel=============')

        # 포트 열기
        if not self.port_handler.openPort():
            self.get_logger().error('Failed to open the port!')
            return
        self.get_logger().info('Succeeded to open the port.')

        # Baudrate 설정
        if not self.port_handler.setBaudRate(BAUDRATE):
            self.get_logger().error('Failed to set the baudrate!')
            return
        self.get_logger().info('Succeeded to set the baudrate.')

        # 각 Dynamixel 모터 설정 (포트가 열리고 Baudrate가 설정된 후 호출)
        for dxl_id in DXL_IDS:
            self.setup_dynamixel(dxl_id)

        self.curTorque = False
        
        # QoS 프로파일 설정
        qos = QoSProfile(depth=10)

        # 토픽 구독
        self.subscription = self.create_subscription(
            SetPosition,
            'set_position',
            self.set_position_callback,
            qos
        )

        self.torqueSubscription = self.create_subscription(
            SetTorque, 'set_torque', self.set_torque_callback, qos
        )

        # 서비스 생성
        self.srv = self.create_service(GetPosition, 'get_position', self.get_position_callback)

    def setup_dynamixel(self, dxl_id):
        print('\n==========Now Setting Dynamixel ID:0%d==========' % dxl_id)
        dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(
            self.port_handler, dxl_id, ADDR_OPERATING_MODE, POSITION_CONTROL
        )
        if dxl_comm_result != COMM_SUCCESS:
            self.get_logger().error(f'Failed to set Position Control Mode: {self.packet_handler.getTxRxResult(dxl_comm_result)}')
        else:
            self.get_logger().info('Succeeded to set Position Control Mode.')

        dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(
            self.port_handler, dxl_id, ADDR_DRIVE_MODE, 4)
        if dxl_comm_result != COMM_SUCCESS:
            self.get_logger().error(f'Failed to set Drive Mode: {self.packet_handler.getTxRxResult(dxl_comm_result)}')
        else:
            self.get_logger().info('Succeeded to set Drive Mode to Time-based profile.')

        dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(
            self.port_handler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
        self.curTorque = True
        if dxl_comm_result != COMM_SUCCESS:
            self.get_logger().error(f'Failed to enable torque: {self.packet_handler.getTxRxResult(dxl_comm_result)}')
        else:
            self.get_logger().info('Succeeded to enable torque.')

    def set_torque_callback(self, msg):
        dxl_id = msg.id
        torque_val = TORQUE_ENABLE if msg.torque else TORQUE_DISABLE
        status = 'ON' if msg.torque else 'OFF'
        dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(
            self.port_handler, dxl_id, ADDR_TORQUE_ENABLE, torque_val
        )
        if dxl_comm_result != COMM_SUCCESS:
            self.get_logger().error(f'[{dxl_id}] Torque {status} Failed: \
                                     {self.packet_handler.getTxRxResult(dxl_comm_result)}')
        else:
            self.get_logger().info(f'[{dxl_id}] Torque {status}')

    def set_position_callback(self, msg):
        goal_position = msg.position

        dxl_comm_result, dxl_error = self.packet_handler.write4ByteTxRx(
            self.port_handler, msg.id, ADDR_PROFILE_VELOCITY, int(msg.runtime*1000))
        if dxl_comm_result != COMM_SUCCESS:
            self.get_logger().error(f'Error: {self.packet_handler.getTxRxResult(dxl_comm_result)}')
        elif dxl_error != 0:
            self.get_logger().error(f'Error: {self.packet_handler.getRxPacketError(dxl_error)}')
        else:
            self.get_logger().info(f'Set [ID: {msg.id}] [Velocity: {int(msg.runtime*1000)}]')
        
        dxl_comm_result, dxl_error = self.packet_handler.write4ByteTxRx(
            self.port_handler, msg.id, ADDR_PROFILE_ACCELERATION, int(msg.runtime*250))
        if dxl_comm_result != COMM_SUCCESS:
            self.get_logger().error(f'Error: {self.packet_handler.getTxRxResult(dxl_comm_result)}')
        elif dxl_error != 0:
            self.get_logger().error(f'Error: {self.packet_handler.getRxPacketError(dxl_error)}')
        else:
            self.get_logger().info(f'Set [ID: {msg.id}] [Acceleration: 500]')

        dxl_comm_result, dxl_error = self.packet_handler.write4ByteTxRx(
            self.port_handler, msg.id, ADDR_GOAL_POSITION, goal_position)
        if dxl_comm_result != COMM_SUCCESS:
            self.get_logger().error(f'Error: {self.packet_handler.getTxRxResult(dxl_comm_result)}')
        elif dxl_error != 0:
            self.get_logger().error(f'Error: {self.packet_handler.getRxPacketError(dxl_error)}')
        else:
            self.get_logger().info(f'Set [ID: {msg.id}] [Goal Position: {msg.position}]')

    def get_position_callback(self, request, response):
        dxl_present_position, dxl_comm_result, dxl_error = self.packet_handler.read4ByteTxRx(
            self.port_handler, request.id, ADDR_PRESENT_POSITION
        )

        if dxl_comm_result != COMM_SUCCESS:
            self.get_logger().error(f'Error: {self.packet_handler.getTxRxResult(dxl_comm_result)}')
        elif dxl_error != 0:
            self.get_logger().error(f'Error: {self.packet_handler.getRxPacketError(dxl_error)}')
        else:
            self.get_logger().info(f'Get [ID: {request.id}] [Present Position: {dxl_present_position}]')

        response.position = dxl_present_position
        return response

    def __del__(self):
        for dxl_id in DXL_IDS:
            self.packet_handler.write1ByteTxRx(
                self.port_handler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE
            )
        self.port_handler.closePort()
        self.get_logger().info('Shutting down read_write_node')


def main(args=None):
    rclpy.init(args=args)
    node = ReadWriteNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

