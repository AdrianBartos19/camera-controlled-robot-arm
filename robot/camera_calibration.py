import cv2
import numpy as np
import glob


chessboard_size = (10, 7)  
square_size = 0.025  


objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
objp *= square_size  

objpoints = []  
imgpoints = []  


images = glob.glob('calibration_images/*.jpg')

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)

        # Draw detected corners (for visualization)
        cv2.drawChessboardCorners(img, chessboard_size, corners, ret)
        cv2.imshow("Chessboard Detection", img)
        cv2.waitKey(500)

cv2.destroyAllWindows()

# 🛠️ Perform Camera Calibration
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# Save calibration results
np.savez("camera_calibration_data", mtx=mtx, dist=dist)

# 📜 Print Calibration Results
print("Camera Matrix:\n", mtx)
print("Distortion Coefficients:\n", dist)
