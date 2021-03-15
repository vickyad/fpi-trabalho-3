init = False
kernel_size = 3


def on_trackbar(val):
    global kernel_size
    if val % 2 != 0:
        kernel_size = val


def brightness_contrast(brightness=0):
    brightness = cv2.getTrackbarPos('Brightness', 'Result')
    contrast = cv2.getTrackbarPos('Contrast', 'Result')

    effect = controller(frame, brightness, contrast)

    return effect


def controller(img, brightness=255, contrast=127):
    brightness = int((brightness - 0) * (255 - (-255)) / (510 - 0) + (-255))
    contrast = int((contrast - 0) * (127 - (-127)) / (254 - 0) + (-127))

    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            max = 255
        else:
            shadow = 0
            max = 255 + brightness
        b_alpha = (max - shadow) / 255
        b_gamma = shadow

        cal = cv2.addWeighted(img, b_alpha, img, 0, b_gamma)
    else:
        cal = img

    if contrast != 0:
        c_alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
        c_gamma = 127 * (1 - c_alpha)

        # The function addWeighted calculates
        # the weighted sum of two arrays
        cal = cv2.addWeighted(cal, c_alpha, cal, 0, c_gamma)

        # putText renders the specified text string in the image.

    cv2.putText(cal, 'B:{},C:{}'.format(brightness, contrast), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    return cal


def get_filtered_frame(frame_src, op):
    global init

    # GAUSSIAN BLUR
    if op == 1:
        if not init:
            cv2.createTrackbar('Kernel', 'Result', 3, 30, on_trackbar)
            init = True
        frame_src = cv2.GaussianBlur(frame_src, (kernel_size, kernel_size), 0)
    # CANNY
    elif op == 2:
        frame_src = cv2.Canny(frame_src, 50, 150)
    # SOBEL
    elif op == 3:
        grad_x = cv2.Sobel(frame_src, cv2.CV_16S, 1, 0, ksize=3, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
        grad_y = cv2.Sobel(frame_src, cv2.CV_16S, 0, 1, ksize=3, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)

        abs_grad_x = cv2.convertScaleAbs(grad_x)
        abs_grad_y = cv2.convertScaleAbs(grad_y)

        frame_src = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
    # NEGATIVE
    elif op == 4:
        frame_src = 255 - frame_src
    # BRIGHTNESS AND CONTRAST
    elif op == 5:
        if not init:
            cv2.createTrackbar('Brightness', 'Result', 255, 2 * 255, brightness_contrast)
            # Contrast range -127 to 127
            cv2.createTrackbar('Contrast', 'Result', 127, 2 * 127, brightness_contrast)

            init = True

        frame_src = brightness_contrast(0)
    # GRAYSCALE
    elif op == 6:
        frame_src = cv2.cvtColor(frame_src, cv2.COLOR_BGR2GRAY)
    # RESIZE
    elif op == 7:
        height, width, layers = frame_src.shape
        new_h = int(height / 2)
        new_w = int(width / 2)
        frame_src = cv2.resize(frame_src, (new_w, new_h))
    # ROTATE 90
    elif op == 8:
        flipped = cv2.transpose(frame_src)
        frame_src = cv2.flip(flipped, 1)
    # HORIZONTAL FLIP
    elif op == 9:
        frame_src = cv2.flip(frame_src, 1)
    # VERTICAL FLIP
    elif op == 0:
        frame_src = cv2.flip(frame_src, -1)

    return frame_src


if __name__ == '__main__':
    import cv2

    menu = """
    Operations menu
    q - Quit
    1 - Gaussian Blur
    2 - Canny operation
    3 - Sobel operation
    4 - Negative operation
    5 - Brightness and Contrast operation
    6 - Grayscale video
    7 - Resize operation
    8 - 90 degrees rotation
    9 - Horizontal flip
    0 - Vertical flip
    """
    operation = -1

    # Configurations to download video
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

    # Get webcam image
    cap = cv2.VideoCapture(0)

    # Create window to display results
    cv2.namedWindow('Result')

    # Display menu options
    print(menu)

    while True:
        ret, frame = cap.read()
        cv2.imshow('Original', frame)

        filtered_frame = get_filtered_frame(frame, operation)
        cv2.imshow('Result', filtered_frame)

        # Program will terminate when 'q' key is pressed
        pressed_key = cv2.waitKey(1)
        if pressed_key == ord('q'):
            break
        # GAUSSIAN BLUR
        elif pressed_key == ord('1'):
            init = False
            operation = 1
        # CANNY
        elif pressed_key == ord('2'):
            init = False
            operation = 2
        # SOBEL
        elif pressed_key == ord('3'):
            init = False
            operation = 3
        # NEGATIVE
        elif pressed_key == ord('4'):
            init = False
            operation = 4
        # BRIGHTNESS AND CONTRAST
        elif pressed_key == ord('5'):
            init = False
            operation = 5
        # GRAY SCALE
        elif pressed_key == ord('6'):
            init = False
            operation = 6
        # RESIZE
        elif pressed_key == ord('7'):
            init = False
            operation = 7
        # ROTATION
        elif pressed_key == ord('8'):
            init = False
            operation = 8
        # MIRROR HORIZONTALLY
        elif pressed_key == ord('9'):
            init = False
            operation = 9
        # MIRROR VERTICALLY
        elif pressed_key == ord('0'):
            init = False
            operation = 0

        # Save frame
        out.write(filtered_frame)

    # Releasing all the resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()
