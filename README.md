# README #
### What is this repository for? ###

* CCTV Motion Tracking

### Message to Friends and Family ###

Id like to share with my family and friends one of my biggest achievements for this year. Something i have been thinking of building for too long. I wanted to build something that could track heavy machinery production lines in order to calculate their efficiency and to pinpoint their utilization flaws.

Today i finally completed my own personal project that utilizes security cams (CCTV stream) and processes them to detect motion and translates them into their perspective status.

I was happy to learn python in a fair amount of time and took use of the OpenCV library in order to detect motion and hence detect the machinery status.

I built a special algorithm to accurately describe the machinery status as either sleeping of running.
The program notifies the user with windows toast notification on any change of running status to the machine.

Then I connected the program to a webhook that can send live notifications warning on the stoppage of any machinery, in addition to a notification message for the resume status, along side with the amount of time this machinery was kept idle.

The program is currently running in production on a number of machines simultaneously and each one sends its own notifs to my own mobile device and i finally get to receive live updates of the status of all the companies machinery.



### Motion Detection ###

I am targeting a certain frame from the stream depending on the location of the CCTV camera and the machinery. Each machine is compared from different cameras to find the best perspective that shows the clearest movements. In some cases I had to use extra sticker paper on certain areas in order to emphasis the machinery movement.

In an actual scenario, the tracking should be taken into consideration before installing the CCTV cameras. While in my case I operated on an existing environment. which btw the program showed very good results.

In the end, all these factors will affect the efficiency of the tracking which I have built a separate "installation" script that calculates it.

as for the transformations, I used a gray scale filter before calculating the deltas. Then I ran a threshold filter on the differences, and finally the delta frame is then dilated. And of course the configuration values for all theses filters also tested in the "installation" script in order to get the best possible efficiency.


### How do I get set up? ###

* Configuration
    - prepare an empty folder `logs_motion` for the logs to live in
    - edit `config_cam.ini` to store camera configs
    - create `config_stream.ini` to store camera access credentials, and  to store IFTTT credentials for webhooks
        ```
        [stream]
        ip_address = YOUR_STREAM_LOCAL_IP
        username = YOUR_STREAM_USERNAME
        password = YOUR_STREAM_PASSWORD

        [ifttt]
        ifttt_key = 'YOUR_KEY'
        ifttt_event = 'YOUR_EVENT_NAME'
        ```
* Dependencies
    - pip install opencv-python
    - pip install tkinter
    - pip install simpledialog
    - pip install matplotlib
    - pip install numpy
    - pip install plotly
    - pip install win10toast
    - pip install win10toast-persist
    - pip install requests
* Running the Scripts
    - Use motion.py to setup the camera environments
    - Use motion_tracking.py as the main script to track (with alerts)
* Database configuration
    - data is written currently in txt files
* How to run tests
    - no tests yet
* Deployment instructions
    - specify the setup for the machines through config_stream.ini
    - Use the batch files to run as many instances for each machine


### Main Scripts ###

* [Motion.py](motion.py)
    - the main file to detect motion
    - shows a frame to select the area to be monitored
    - uses `config_cam.ini` to fetch camera configs
    - uses `config_stream.ini` to fetch camera access credentials
* [Motion_Tracking.py](motion_tracking.py)
    - the production version of `motion.py`
    - takes an arg input for the camera name to detect
    - uses `config_cam.ini` to fetch camera configs
    - uses `config_stream.ini` to fetch camera access credentials
    - has some flags to enable logging and notification events
    
* [Facial2.py](facial2.py)
    - under development
    - aimed to be moved to another project
### Logging ###

There are three types of logs currently in this project. all dumped into the `logs_motion` folder

1. Motion Detection in `log_motion_{machinename}.txt`
    - records motion detected for each frame in a file
    - this file can be later parsed with `plot_motion.py` to show a plot frame
    - this file can be later parsed with `parse_motion.py` to generate an HTML file with an interactive chart
    with the name `chart_motion_{machinename}.html`
2. Status Change in `log_globalmotion_change_{machinename}.txt`
    - logs moments when status is changed to moving
    - logs moments when status is changed to stopped
    - status is actually changed to moving when a window of 30 secs records more than half of its frames as moving
    - status is actually changed to stopped when a window of 30 secs records more than half of its frames as stopped
3. Deepsleep alerting in `log_deepsleep_warn_{machinename}.txt`
    - logs moments a machine goes to deep sleep (status is stopped for 20 mins)
    - logs moments a machine comes out of deep sleep (moves after being in deep sleep)

### Who is invited to join? ###

* Repo owner or admin
* Other community or team contact

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines