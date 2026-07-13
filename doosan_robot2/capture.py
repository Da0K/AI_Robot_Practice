import cv2

from camera import RealSenseD435

def main():
    camera = RealSenseD435(color_resolution=720, depth_mode="720P")
    color_img, depth_img = camera.get_image()

    color_intrinsics_mat, depth_intrinsics_mat = camera._init_intrinsics()

    print(f'Color_intrinsics_mat: {color_intrinsics_mat}')
    print(f'Depth_intrinsics_mat: {depth_intrinsics_mat}')

    cv2.imshow("Original Color image", color_img)
    cv2.imshow("Original Depth image", depth_img)
    cv2.imwrite("./color_img.png", color_img)
    cv2.imwrite("./depth_img.png", depth_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    print(f'Color image shape: {color_img.shape}')
    print(f'Color pixel value: {color_img[360][640]}')

    print(f'Depth image shape: {depth_img.shape}')
    print(f'Depth image Y: {depth_img.shape[0]}')
    print(f'Depth image X: {depth_img.shape[1]}')
    print(f'Depth value: {depth_img[360][640]} m')

if __name__ == "__main__":
    main()