import numpy as np
import matplotlib.pyplot as plt
import serial
from time import sleep
from ikpy.chain import Chain

robot_chain = Chain.from_urdf_file("arm_urdf.urdf", active_links_mask=[0, 1, 1, 1, 1, 1, 0])

try:
    ser = serial.Serial("COM3", 9600, timeout=1)
    sleep(2)
except serial.SerialException:
    print("⚠️ Error: Could not open COM3.")

def map_joint_angle(name, ik_angle, ik_min, ik_max, servo_min, servo_max):
    return servo_min + ((ik_angle - ik_min) * (servo_max - servo_min) / (ik_max - ik_min))

def compute_ik_for_target(target_position):

    """ print(target_position)
    return """
    target_position[1] = -target_position[1]
    
    theta_base_deg = np.degrees(np.arctan2(target_position[1], target_position[0]))
    
    initial_positions = [theta_base_deg] + [0] * (len(robot_chain.active_links_mask) - 1)
    joint_angles = robot_chain.inverse_kinematics(target_position, initial_position=initial_positions)
    joint_angles_degrees = np.degrees(joint_angles)

    servo_angles = {
        "base": map_joint_angle("base", joint_angles_degrees[1], -90, 90, 235, 55),
        "shoulder": map_joint_angle("shoulder", joint_angles_degrees[2], -90, 90, 225, 55),
        "elbow": map_joint_angle("elbow", joint_angles_degrees[3], -90, 90, 235, 55),
        "wrist": map_joint_angle("wrist", joint_angles_degrees[4], -90, 90, 235, 55),
        "wrist_rotate": map_joint_angle("wrist_rotate", joint_angles_degrees[5], -90, 90, 235, 55),
        "gripper": map_joint_angle("gripper", joint_angles_degrees[6], 0, 55, 0, 55),
    }

    if servo_angles["base"] < 160:
        servo_angles["base"] += 2
    else:
        servo_angles["base"] -= 4

    command = " ".join(f"{i}{int(angle)}" for i, angle in enumerate(servo_angles.values())) + "\n"
    
    if ser.is_open:
        ser.write(command.encode())
    
    return servo_angles

