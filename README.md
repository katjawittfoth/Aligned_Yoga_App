
<div align="left">
    <img src="code/aligned/app/static/images/logo.svg",style="height:50px;"> <style="font-size: 50px">      Yoga Pose Correction App
</div>

# Project Description
Aligned is a yoga pose correction web application that processes images and videos of a user’s yoga poses and provides feedback on how to improve the pose. The app was built using Flask and runs on an Amazon EC2 instance with GPU.

The overall process is as follows:

* User logs in and selects which pose to evaluate
* App provides instructions on how to execute the pose
Once ready, the user records a video of themselves doing the pose within the app (using webcam)
Video is automatically processed using [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose), an open-source, deep learning-based library for keypoint detection developed at Carnegie Mellon University.
* The app uses the keypoints from OpenPose as features *to classify different pose faults using a rule-based system.
* Feedback is provided to the user on how they can safely improve their pose.

<i> Note that the app's website is not currently available due to the high cost of running AWS EC2 instance.</i>

* [Watch Demo Video](https://youtu.be/t8HMLYR1-FE)
* [Slide Deck for final presentation to VCs](https://github.com/katjawittfoth/Aligned_Yoga_App/blob/master/Aligned_VC_Presentation_Deck.pdf)
* [Flask routes](https://github.com/katjawittfoth/Aligned_Yoga_App/blob/master/code/aligned/app/routes.py)
* [Video processing script](https://github.com/katjawittfoth/Aligned_Yoga_App/blob/master/code/aligned/process_openpose_user.py)
* [Modeling](https://github.com/katjawittfoth/Aligned_Yoga_App/blob/master/code/aligned/modeling.py)
