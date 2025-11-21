import http
import cv2 as cv
import numpy as np

# define range of yellow color in HSV
lower_yellow = np.array([18, 69, 107])
upper_yellow = np.array([35, 255, 255])

# define range of black color is HSV
lower_black = np.array([0, 0, 9])
upper_black = np.array([179, 255, 255])

# kernel used for morphological operations
kernel = np.ones((5, 5), np.uint8)

# Predefined coral letter based on yellow:black ratio
# Format: [Coral Letter, Yellow:Black Ratio]
y_b_ratio_pre = {"A": 4.20, "B": 6.34, "C": 7.69, "D": 7.27}


def main():
    cap = cv.VideoCapture("http://172.25.250.1:8554/")
    if not cap.isOpened():
        print("Failed to open video")
        return

    max_yellow_pixels = 0
    best_frame = None
    best_frame_x_min = 0
    best_frame_x_max = 0
    best_frame_y_min = 0
    best_frame_y_max = 0

    while True:
        # read image
        ret, frame = cap.read()
        if not ret:
            print("End of video or failed to read frame")
            break
        if is_blurry(frame):
            print("Frame is blurry, skipping...")
            continue

        # Convert to HSV
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        # Threshold yellow and black using acceptable range
        yellow_mask = cv.inRange(hsv, lower_yellow, upper_yellow)
        black_mask = cv.inRange(hsv, lower_black, upper_black)

        # If not enough yellow detected, skip frame
        yellow_pixel_count = cv.countNonZero(yellow_mask)
        if yellow_pixel_count < 2500:
            continue

        # Clean noise
        yellow_mask = cv.morphologyEx(yellow_mask, cv.MORPH_OPEN, kernel)
        yellow_mask = cv.morphologyEx(yellow_mask, cv.MORPH_CLOSE, kernel)

        # Combine yellow chunks together
        yellow_mask = cv.dilate(yellow_mask, kernel, iterations=2)

        black_mask = cv.morphologyEx(black_mask, cv.MORPH_OPEN, kernel)
        black_mask = cv.morphologyEx(black_mask, cv.MORPH_CLOSE, kernel)

        # Find contours
        yellow_contours, _ = cv.findContours(
            yellow_mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE
        )

        if yellow_contours:
            # Combine all contours into one bounding box
            x_min = min([cv.boundingRect(c)[0] for c in yellow_contours])
            y_min = min([cv.boundingRect(c)[1] for c in yellow_contours])
            x_max = max(
                [
                    cv.boundingRect(c)[0] + cv.boundingRect(c)[2]
                    for c in yellow_contours
                ]
            )

            # ignore base of coral, black stand
            # calculate a percentage of the coral box
            y_max_initial = max(
                [
                    cv.boundingRect(c)[1] + cv.boundingRect(c)[3]
                    for c in yellow_contours
                ]
            )

            y_max = (int)((y_max_initial - y_min) * 0.9) + y_min

            # Draw rectangle
            cv.rectangle(
                frame, (x_min, y_min), (x_max, y_max), (0, 255, 255), 2
            )

            # Reverse mask to make black areas white and white areas black
            black_mask = cv.bitwise_not(black_mask)

            # Eliminate black areas outside the bounding box
            black_mask_temp = np.zeros_like(black_mask)
            black_mask_temp[y_min:y_max, x_min:x_max] = black_mask[
                y_min:y_max, x_min:x_max
            ]
            black_mask = black_mask_temp

            # Alternatively, count by the number of black pixels in the bounding box
            black_pixel_count = cv.countNonZero(
                black_mask[y_min:y_max, x_min:x_max]
            )

            # Give percentage of black pixels in bounding box
            black_per = (
                black_pixel_count / ((y_max - y_min) * (x_max - x_min))
            ) * 100
            print(
                f"Percentage of black pixels in bounding box: {black_per:.2f}%"
            )

            yellow_pixel_count = cv.countNonZero(
                yellow_mask[y_min:y_max, x_min:x_max]
            )
            print(
                f"Number of yellow contours detected: {len(yellow_contours)}"
            )
            yellow_per = (
                yellow_pixel_count / ((y_max - y_min) * (x_max - x_min))
            ) * 100
            print(
                f"Percentage of yellow pixels in bounding box: {yellow_per:.2f}%"
            )

            if (
                yellow_pixel_count > max_yellow_pixels
                and yellow_per < 40
                and len(yellow_contours) < 3
            ):
                max_yellow_pixels = yellow_pixel_count
                best_frame = frame.copy()
                best_frame_x_min = x_min
                best_frame_x_max = x_max
                best_frame_y_min = y_min
                best_frame_y_max = y_max_initial

            coral_letter = determine_letter(
                frame, x_min, x_max, y_min, y_max
            )
            # Show results
            cv.imshow("frame", frame)
            cv.imshow("yellow_mask", yellow_mask)
            cv.imshow("black_mask", black_mask)
            if cv.waitKey(33) & 0xFF == ord("q"):
                break

    if best_frame is not None:
        coral_letter = determine_letter(
            best_frame,
            best_frame_x_min,
            best_frame_x_max,
            best_frame_y_min,
            best_frame_y_max,
        )
        # download best frame
        cv.imwrite("best_frame.png", best_frame)
        cv.imshow("Best Frame with Most Yellow", best_frame)
        print(f"Determined Coral Letter: {coral_letter}")
        print(f"Yellow to black ratio: {yellow_pixel_count / (black_pixel_count + 1):.2f}")
        print("-----")
        print(f"Prior ratio: {y_b_ratio_pre.get(coral_letter)}")
        growth_status = growth_determination(
            yellow_pixel_count / (black_pixel_count + 1), coral_letter
        )
        print(f"Growth Status: {growth_status}")
        cv.waitKey(0)
    cap.release()
    cv.destroyAllWindows()


def is_blurry(image, threshold=300.0):
    """
    Detect if an image is blurry using the Laplacian variance method.

    Args:
        image (numpy.ndarray): The input image.
        threshold (float): Variance threshold below which the image is considered blurry.

    Returns:
        bool: True if the image is blurry, false otherwise.
    """
    # Convert the image to grayscale
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    # Compute the Laplacian of the image
    laplacian = cv.Laplacian(gray, cv.CV_64F)

    # Compute the variance of the Laplacian
    variance = laplacian.var()
    print(f"Laplacian variance: {variance}")

    # Determine if the image is blurry
    return variance < threshold


def determine_letter(frame, x_min, x_max, y_min, y_max):
    """
    Determine the letter based on the design of the root of the coral.

    Split the bottom 33% of the bounded box into sections and analyze the color distribution.

    Args:
        black_percentage (float): Percentage of black pixels.
        yellow_percentage (float): Percentage of yellow pixels.
        black_contours_count (int): Number of black contours detected.
        yellow_contours_count (int): Number of yellow contours detected.

    Returns:
        coral_letter (string): Letter representing determined coral (or Z for unknown)
        root_region (numpy.ndarray): Extracted root region of the coral with visualization boxes.
    """
    # Default letter if no conditions are met
    letter = "Z"

    # Extract the a third of the bounded box
    height = y_max - y_min
    width = x_max - x_min
    root_y_start = y_max - int(0.33 * height)
    root_region = frame[root_y_start:y_max, x_min:x_max]

    # Convert to HSV
    hsv_root = cv.cvtColor(root_region, cv.COLOR_BGR2HSV)

    # Threshold yellow and black using acceptable range
    yellow_mask_root = cv.inRange(hsv_root, lower_yellow, upper_yellow)

    section_width = width // 10
    section_sums = []
    for i in range(10):
        section = yellow_mask_root[
            :, i * section_width: (i + 1) * section_width
        ]
        section_sum = cv.countNonZero(section)
        section_sums.append(section_sum)

    # Draw boxes for visualization
    for i in range(10):
        cv.rectangle(
            root_region,
            (i * section_width, 0),
            ((i + 1) * section_width, root_region.shape[0]),
            (0, 255, 0),
            1,
        )
    # Determine middle section based on box with highest yellow pixel count
    # adding 1 to convert from 0-indexed to 1-indexed
    middle_index = section_sums.index(max(section_sums))
    threshold = (
        (sum(section_sums) - max(section_sums)) / (len(section_sums) - 1) * 0.8
    )
    print(f"Average sum: {threshold}")
    print(f"Section sums: {section_sums}, Middle index: {middle_index}")

    # Prevent out of bounds hit
    if (middle_index > 5) or (middle_index < 4):
        return letter

    if (
        (section_sums[middle_index - 2] > threshold)
        and (section_sums[middle_index + 2] > threshold)
        and (section_sums[middle_index + 4] > threshold)
        and (section_sums[middle_index - 4] > threshold)
    ) or (
        (section_sums[middle_index + 1] > threshold)
        and (section_sums[middle_index - 2] > threshold)
        and (section_sums[middle_index - 4] > threshold)
        and (section_sums[middle_index + 3] > threshold)
    ):
        letter = "D"
    elif (
        (section_sums[middle_index - 2] > threshold)
        and (section_sums[middle_index + 2] > threshold)
        and (section_sums[middle_index + 3] > threshold)
    ) or (
        (section_sums[middle_index - 2] > threshold)
        and (section_sums[middle_index + 2] > threshold)
        and (section_sums[middle_index - 3] > threshold)
    ):
        letter = "A"
    elif (section_sums[middle_index - 2] > threshold) and (
        section_sums[middle_index + 2] > threshold
    ):
        letter = "C"
    else:
        letter = "B"
    return letter


def growth_determination(yellow_to_black_ratio, letter):
    """
    Determine growth status based on yellow to black ratio and coral letter.

    Args:
        yellow_to_black_ratio (float): The ratio of yellow to black pixels.
        letter (str): The coral letter.

    Returns:
        growth_status (str): Growth status ("Increase", "Stable", "Decrease").
    """
    # Find the predefined ratio for the given letter
    predefined_ratio = y_b_ratio_pre.get(letter)

    if predefined_ratio is None:
        return "Unknown"

    # Determine growth status based on ratio comparison
    if yellow_to_black_ratio >= predefined_ratio * 1.1:
        return "Increase"
    elif yellow_to_black_ratio >= predefined_ratio:
        return "Stable"
    else:
        return "Decrease"


if __name__ == "__main__":
    main()
