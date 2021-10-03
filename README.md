# README #
### What is this repository for? ###

* CCTV Motion Tracking

### Message to Friends and Family ###

Id like to share with my family and friends one of my biggest achievements for this year. Something i have been thinking of building for too long. I wanted to build something that could track heavy machinery production lines in order to calculate their efficiency and to pinpoint their utilization flaws.
Today i finally completed my own personal project that utilizes security cams (CCTV stream) and processes them to detect motion and translates them into their perspective status.
I was happy to learn python in a fair amount of time and took use of the OpenCV library in order to detect motion and hence detect the machinery status.
I build a special algorithm to accurately describe the machinery status as either sleeping of running.
The program notifies the user with windows toast notification on any change of running status to the machine.
Then I connected the program to a webhook that can send live notifications warning on the stoppage of any machinery, in addition to a notification message for the resume status, along side with the amount of time this machinery was kept idle.
The program is currently running in production on a number of machines simultaneously and each one sends its own notifs to my own mobile device and i finally get to receive live updates of the status of all the companies machinery.



### Motion Detection ###

I am targeting a certain frame from the stream depending on the location of the CCTV camera and the machinery. Each machine is compared from different cameras to find the best perspective that shows the clearest movements. In some cases I had to use extra sticker paper on certain areas in order to emphasis the machinery movement.

In an actual scenario, the tracking should be taken into consideration before installing the CCTV cameras. While in my case I operated on an existing environment. which btw the program showed very good results.

In the end, all these factors will affect the efficiency of the tracking which I have built a separate "installation" script that calculates it.

as for the transformations, I used a gray scale filter before calculating the deltas. Then I ran a threshold filter on the differences, and finally the delta frame is then dilated. And of course the configuration values for all theses filters also tested in the "installation" script in order to get the best possible efficiency.


### How do I get set up? ###

* Summary of set up
* Configuration
    - Use motion.py to setup the camera environments
    - Use motion_tracking.py as the main script to track (with alerts)
* Dependencies
    pip install opencv-python
    pip install tkinter
    pip install simpledialog
    pip install matplotlib
    pip install numpy
    pip install plotly
    pip install win10toast
    pip install win10toast-persist
    pip install requests
* Database configuration
    - data is written currently in txt files
* How to run tests
    - no tests yet
* Deployment instructions
    - specify the setup for the machines through config_stream.ini
    - Use the batch files to run as many instances for each machine

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who is invited to join? ###

* Repo owner or admin
* Other community or team contact