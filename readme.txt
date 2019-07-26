Description

This implementation aims to measure the elbow angle from a webcam and write it to the serial port.

For measuring the angle, this is how my algorithm will operate:
1. Extract only the arm
2. Make the image bipolar
3. Fit a convex hull around the arm.
4. The elbow will form a convexity defect. Ideally, the hand, elbow, and the shoulder should be returned as the 3 points of that defect.
5. Use the cosine formular to extract the angle formed by these 3 points around the elbow.
6. Write the angle to the serial port. 
