from __future__ import print_function
import sys
import cv2
import numpy
from random import randint
import serial
from simple_pid import PID
trackerTypes = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']


def createTrackerByName(trackerType):
    # Create a tracker based on tracker name
    if trackerType == trackerTypes[0]:
        tracker = cv2.TrackerBoosting_create()
    elif trackerType == trackerTypes[1]:
        tracker = cv2.TrackerMIL_create()
    elif trackerType == trackerTypes[2]:
        tracker = cv2.TrackerKCF_create()
    elif trackerType == trackerTypes[3]:
        tracker = cv2.TrackerTLD_create()
    elif trackerType == trackerTypes[4]:
        tracker = cv2.TrackerMedianFlow_create()
    elif trackerType == trackerTypes[5]:
        tracker = cv2.TrackerGOTURN_create()
    elif trackerType == trackerTypes[6]:
        tracker = cv2.TrackerMOSSE_create()
    elif trackerType == trackerTypes[7]:
        tracker = cv2.TrackerCSRT_create()
    else:
        tracker = None
        print('Incorrect tracker name')
        print('Available trackers are:')
        for t in trackerTypes:
            print(t)

    return tracker


# Obtain the center of box in a frame
def calculateCenter(box):
    x = int(box[0]) + (int(bbox[2]) / 2)
    y = int(box[1]) + (int(box[3]) / 2)
    return int(x), int(y)

# Serial for Arduino
arduino = serial.Serial('COM9', 250000)


# Create a video capture object to read videos
cap = cv2.VideoCapture(0)
frames_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
frames_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)




# PID Controller for roll
pid_roll = PID(0.6, 0.01, 1.5)
pid_roll.setpoint = frames_width/2
pid_roll.output_limits = (-500, 500)


# PID Controller for pitch
pid_pitch = PID(0.6, 0.01, 1.5)
pid_pitch.setpoint = frames_width/2
pid_pitch.output_limits = (-500, 500)


# Read first frame
success, frame = cap.read()

# quit if unable to read the video file
if not success:
    print('ERROR: Failed to read frame!')
    sys.exit(1)
else:
    print('Frame loaded successfully')

## Select boxes
bboxes = []
colors = []

# OpenCV's selectROI function doesn't work for selecting multiple objects in Python
# So we will call this function in a loop till we are done selecting all objects
while True:
    # draw bounding boxes over objects
    # selectROI's default behaviour is to draw box starting from the center
    # when fromCenter is set to false, you can draw box starting from top left corner
    success, frame = cap.read()
    bbox = cv2.selectROI('MultiTracker', frame)
    bboxes.append(bbox)
    colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))
    print("Press q to quit selecting boxes and start tracking")
    print("Press any other key to select next object")
    k = cv2.waitKey(0) & 0xFF
    if (k == 113):  # q is pressed
        break

print('Selected bounding boxes {}'.format(bboxes))

# Specify the tracker type
trackerType = "MOSSE"

# Create MultiTracker object
multiTracker = cv2.MultiTracker_create()

# Initialize MultiTracker
for bbox in bboxes:
    multiTracker.add(createTrackerByName(trackerType), frame, bbox)

# Process video and track objects
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # get updated location of objects in subsequent frames
    success, boxes = multiTracker.update(frame)

    # draw tracked objects
    for i, newbox in enumerate(boxes):
        p1 = (int(newbox[0]), int(newbox[1]))
        p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
        cv2.rectangle(frame, p1, p2, colors[i], 2, 1)

        x, y = calculateCenter(newbox)
        cv2.circle(frame, (x, y), 4,(255, 255, 0), -1)

        # Update pitch and roll with drone position and PID Controllers
        roll = 1500 + pid_roll(x)
        pitch = 1500 + pid_pitch(y)

        arduino.write(f"{int(roll)} {int(pitch)}".encode('ascii'))

        print(f"Post PID => Roll: {int(roll)}\nPitch: {int(pitch)}\n\n")


    # show frame
    cv2.imshow('MultiTracker', frame)

    # quit on ESC button
    if cv2.waitKey(1) & 0xFF == 27:  # Esc pressed
        break


