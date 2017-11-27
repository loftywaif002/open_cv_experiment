import glob
import numpy as np
import cv2
import math
#Change this patth according to your project location
for a in glob.glob('C:\\Users\\Dip\\Desktop\\open_cv_github\\photos\\*.jpg'):
    print(a)
    img = cv2.imread(a)
	#print("Processing image: ", imgpath)

    img = cv2.resize(img, (600, 800))  #Resizing Image Test
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #Convertin to grayscale image
    # First argument is the source image, which should be a grayscale image.
    # Second argument is the threshold value which is used to classify the pixel values.
    # Third argument is the maxVal which represents the value to be given if pixel value is more than (sometimes less than) the threshold value
    retval, thresholdedimage = cv2.threshold(imgray, 190, 255, cv2.THRESH_BINARY)
    # According to docs For better accuracy, use binary images. So before finding contours, apply threshold or canny edge detection.For better accuracy, use binary images.
    # https://docs.opencv.org/3.3.1/d4/d73/tutorial_py_contours_begin.html
    contourimage, contours, hierarchy = cv2.findContours(thresholdedimage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  #Not sure about the 2nd and third parameters
    #cv2.drawContours(img, contours, -1, (0, 190, 0), 3) 
    cv2.drawContours(img, contours, -1, (0, 255, 0), 3)
    cv2.imshow("image with contours", img)
	#print(contours)
    cv2.imwrite("C:\\Users\\Dip\\Desktop\\open_cv_github\\output\\Contoured-image.PNG", img);
    cv2.waitKey()


	# Let's compute the area for each contour co-ordinates.
    areas = [cv2.contourArea(contour) for contour in contours]
    #print(areas,"\n")

	 #Index of the contour with max area.
    max_area_index = np.argmax(areas)
    #print("max_area_index", max_area_index)

	#Get the contour array(The one that represents the pattern in the white image)
    patterncontour = contours[max_area_index]

	#Get the minimal up-right bounding rectangle for our contour pattern.
    x, y, w, h = cv2.boundingRect(patterncontour)
    #print("\n x",x,"y=",y,"w=",w,"h=",h,"\n")


	# ================================ Step:7 - Analyse the rotation of the pattern.============#
    d = {}
    for contour in contours:
	    # moments() help us in finding centers of all contours
        M = cv2.moments(contour)
        if M["m00"] == 0:
            continue
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        if d.get((cX, cY), 0):
            d[(cX, cY)] += 1  # If the coordinates already exits, we just increment the value
        else:
            d[(cX, cY)] = 1  # else add the list to the array.
    three_hits = []
    two_hits = []
    for key in d:
        if d[key] == 3:
            three_hits.append(key)
        if d[key] == 2:
            two_hits.append(key)
	# this will be used if the rotation of the barcode is necessary, for now I will use the rotation of the rectangle
    if len(three_hits) == 3:
        pass
    elif len(three_hits) == 2:
        pass
    else:
        pass

	# =============================Step-8:  Get the rotated angle of the pattern.=============#
	# minAreaRect : gets the  minimum-area bounding the rotated rectangle for a specified contour
    rect = cv2.minAreaRect(patterncontour)
	
	# boxPoints: Helps us finding the four vertices of a rotated rect.
    box = cv2.boxPoints(rect)

# int0: Converts the box vertices into integers.
    box = np.int0(box)

    cv2.drawContours(img, [box], 0, (0, 0, 255), 2)
    rotatedangle = rect[2]

    print("Rotation Angle of the barcode pattern: {0:.2f} ".format(rotatedangle))

# =========================Step-9: Get the the distance between contour corner and bounded rectangle. =====================

# Functions to compute the mid point and distance between two points#
    def mid_point(point_X, point_Y):
        return [(point_X[0] + point_Y[0]) / 2, (point_X[1] + point_Y[1]) / 2]


    def distance(point_X, point_Y):
        return math.sqrt((point_X[0] - point_Y[0]) ** 2 + (point_X[1] - point_Y[1]) ** 2)


# Let's calculate the amount of skew in the image (represented as min_dist in pixels).

    min_dist = 1000

    for point in box:
        temp_dist = distance(patterncontour[0][0], point)
        min_dist = min(min_dist, temp_dist)

    print("Degree from the birds eye view:  {0:.2f} ".format(min_dist))

# A bounded rectangular box obtained in above steps will help us determine the distance between the camera and the barcode.
# Assigning the box co-ordinates to temp variables.
    P = box[0]
    Q = box[1]
    R = box[2]
    S = box[3]

# Calculate the midpoint between each box point lines.
    P_Q = mid_point(P, Q)
    R_S = mid_point(R, S)
    P_S = mid_point(P, S)
    Q_R = mid_point(Q, R)

# Calculate the distance between each parallel box point lines.
    PS_QR_dist = distance(P_S, Q_R)
    PQ_RS_dist = distance(P_Q, R_S)

    if PS_QR_dist > PQ_RS_dist:
        width = PS_QR_dist
        height = PS_QR_dist
    else:
        width = PS_QR_dist
        height = PS_QR_dist

# at 1 foot away the paper appears 450 by 580 pixels
# this is needed for a depth ratio
    width_ratio_1foot = 450
    height_ratio_1foot = 580
# at 2 feet away the paper appears 219 by 285 pixels
    width_ratio_2foot = 219
    height_ratio_2foot = 285

# use scaling factors from 1 foot and 2 feet
    one_foot_height = 1 / (height / height_ratio_1foot)
    one_foot_width = 1 / (width / width_ratio_1foot)

    two_foot_height = 2 / (height / height_ratio_2foot)
    two_foot_width = 2 / (width / width_ratio_2foot)

# Final distance is the average of above 4 parameters.
    distance_away = (one_foot_width + one_foot_height + two_foot_width + two_foot_height) / 4

    print("Image was taken {0:.2f} feet away ".format(distance_away, min_dist, rotatedangle))

    cv2.drawContours(img, contours, max_area_index, (0, 125, 0), 3)
    cv2.imshow("output image", img)
    cv2.imwrite("C:\\Users\\Dip\\Desktop\\open_cv_github\\output\\output-image.PNG", img);  # Editing  the output image.
    cv2.waitKey(0)