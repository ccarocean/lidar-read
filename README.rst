LiDAR Data Reception for the Garmin LiDAR-Lite v3HP
===================================================

Title: lidar-read

Options
-------


Installation
------------
Create virtual environment:

.. code-block::

    python -m venv --prompt=lidar .venv
    source .venv/bin/activate

Inside Virtual Environment:

.. code-block::

    setup.py install


How to run
----------
Source Virtual Environment:

.. code-block::

    source .venv/bin/activate

Run as root:

.. code-block::

    sudo .venv/bin/python -m lidar


Related Files
-------------
- Private key for station must be located in /home/ccaruser/keys
- Data directory must exist at /home/ccaruser/data/lidar


Author
------
Adam Dodge

University of Colorado Boulder

Colorado Center for Astrodynamics Research

Jet Propulsion Laboratory

Purpose
-------
This program runs on a raspberry pi and reads data from a Garmin LiDAR-Lite v3HP. It initially configures the LiDAR to
the correct settings, and then takes data at a rate close to 200Hz. Every minute it sends a post api request to the web
server located on cods.colorado.edu where the data is stored and analyzed. The data is also stored onboard the raspberry
pi as a backup. This program also blinks an LED to show someone that it is running just by looking at the system.