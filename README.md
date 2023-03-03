# Focusing Jig

## Setup (LINUX PC)

1.  Put this repository in ~/focus_jig
2.  Install python version 3.10
3.  Run ```~/focus_jig$ python3 -m pip install requirements_linux.txt``` 
4.  Allow read and write access to the usb STLINK devices. For Ubuntu users this is done by creating a new rules file
using the command... ```sudo nano /etc/udev/rules.d/90-my-extra-usb.rules``` and then fill the file with...
    ```shell
    # STLINK-V2
    SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="3748", MODE="0666"
    # STLINK-V3
    SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="374f", MODE="0666"
    ```
    save the file and exit nano. Now run the command ```udevadm control --reload``` to reload the usb rules.

   5.  Set up the focusing jig hardware so everything is connected up as outlined below\
       Linux PC <--> Factory Programming PCB <--> Sunrise PCB <--> Forest Pod PCB
6. Run ```~/focus_jig$ python3 focus_automated_LINUX_ONLY.py```
7. There should now be a low frame rate video feed appear on the screen


## Focus a Forest Pod PCB

1. Setup video feed as per the instructions above
2. Place the Forest Pod PCB inside the 3D printed Focus Jig housing. The video feed should now show a grid
3. Twist the camera lens until the middle of the image (where the blue line is) is sharp/in focus. Note: The bar graph
lines to the right of the video feed help show which areas of the image are most in focus.