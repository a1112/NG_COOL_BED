import cv2
import numpy as np

# 读取图像
image = cv2.imread(fr"G:\LG\NG_COOL_BED\config\camera\calibrate\calibrate_1\L1-4.jpg")
h, w = image.shape[:2]

# ----------------------------
# 需要替换为你的相机标定参数！
# ----------------------------
# 相机内参矩阵（假设值）
camera_matrix = np.array([
    [1000, 0, w/2],   # fx, 0, cx
    [0, 1000, h/2],    # 0, fy, cy
    [0, 0, 1]
], dtype=np.float32)

# 畸变系数 [k1, k2, p1, p2, k3]
dist_coeffs = np.array([-0.6, 0.05, 0.01, 0.01, 0], dtype=np.float32)

# 畸变矫正
undistorted = cv2.undistort(image, camera_matrix, dist_coeffs)

# 显示结果
cv2.imwrite("undistorted.jpg", undistorted)
cv2.waitKey(0)