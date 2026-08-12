import time
import cv2 
import numpy as np 
from ArucoDetection_definitions import *
import keyboard
from IK import *

# Load camera calibration parameters
calibration_data = np.load("camera_calibration_data.npz")
mtx = calibration_data["mtx"]  # Camera matrix
dist = calibration_data["dist"]  # Distortion coefficients

start_time = time.time()

desired_aruco_dictionary1 = "DICT_4X4_50"
desired_aruco_dictionary2 = "DICT_6X6_50"

ARUCO_DICT = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
}

def get_markers(vid_frame, aruco_dictionary, aruco_parameters):
    aruco_detector = cv2.aruco.ArucoDetector(aruco_dictionary, aruco_parameters)
    bboxs, ids, rejected = aruco_detector.detectMarkers(vid_frame)
    ids_sorted = [id_number[0] for id_number in ids] if ids is not None else ids
    return bboxs, ids_sorted

current_square_points = [[10, 400], [400, 400], [400, 10], [10, 10]]
current_center_Corner = [[0, 0]]
marker_location_hold = True

def main():
    print(f"[INFO] Detecting '{desired_aruco_dictionary1}' markers...")
    this_aruco_dictionary1 = cv2.aruco.getPredefinedDictionary(ARUCO_DICT[desired_aruco_dictionary1])
    this_aruco_parameters1 = cv2.aruco.DetectorParameters()
    this_aruco_dictionary2 = cv2.aruco.getPredefinedDictionary(ARUCO_DICT[desired_aruco_dictionary2])
    this_aruco_parameters2 = cv2.aruco.DetectorParameters()
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        exit()
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break
        
        # Undistort frame using camera calibration parameters
        frame = cv2.undistort(frame, mtx, dist, None, mtx)
        
        markers, ids = get_markers(frame, this_aruco_dictionary1, this_aruco_parameters1)
        frame_clean = frame.copy()
        left_corners, corner_ids = getMarkerCoordinates(markers, ids, 0)
        
        if marker_location_hold and corner_ids is not None:
            for count, id in enumerate(corner_ids):
                if id <= 4:
                    current_square_points[id - 1] = left_corners[count]
        left_corners = current_square_points
        corner_ids = [1, 2, 3, 4]
        
        cv2.aruco.drawDetectedMarkers(frame, markers)
        draw_corners(frame, left_corners)
        draw_numbers(frame, left_corners, corner_ids)
        frame_with_square, squareFound = draw_field(frame, left_corners, corner_ids)
        
        if squareFound:
            img_wrapped = four_point_transform(frame_clean, np.array(left_corners))
            h, w, c = img_wrapped.shape
            
            marker_foam, ids_foam = get_markers(img_wrapped, this_aruco_dictionary2, this_aruco_parameters2)
            centerCorner = getMarkerCenter_foam(marker_foam)
            
            if marker_location_hold and centerCorner:
                current_center_Corner[0] = centerCorner[0]
            centerCorner[0] = current_center_Corner[0]
            
            draw_corners(img_wrapped, centerCorner)
            img_wrapped = cv2.line(img_wrapped, (centerCorner[0][0], 0), (centerCorner[0][0], h), (0, 0, 255), 2)
            img_wrapped = cv2.line(img_wrapped, (0, centerCorner[0][1]), (w, centerCorner[0][1]), (0, 0, 255), 2)
            
            cv2.imshow('img_wrapped', img_wrapped)
        
        cv2.imshow('frame_with_square', frame_with_square)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        if keyboard.is_pressed('p'):
            x_coordinate = (1 - (centerCorner[0][1] / h)) * 37  # Convert pixels to cm
            y_coordinate = ((centerCorner[0][0] / w) * 54) - 27  
            print("Object Position (cm) relative to area:", round(x_coordinate, 2), ",", round(y_coordinate, 2))
            compute_ik_for_target([x_coordinate / 100, -y_coordinate / 100, 0.25])
    
    cap.release()
    cv2.destroyAllWindows()
    return current_center_Corner

if __name__ == '__main__':
    foam_center = main()
