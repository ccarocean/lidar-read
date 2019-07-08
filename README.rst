LiDAR Data Reception for the Garmin LiDAR-Lite v3HP
===================================================

Title: lidar-read

Options
-------
Required argument:
    -l LOCATION, --location LOCATION        GPS Location (ex. harv)

Optional arguments:
    -h, --help                  Show help message and exit
    --led LED                   LED Pin. default is 21


Installation
------------
Create virtual environment:

.. code-block::

    python -m venv --prompt=lidar .venv
    source .venv/bin/activate

Inside Virtual Environment:

.. code-block::

    python setup.py install


How to run
----------
Source Virtual Environment:

.. code-block::

    source .venv/bin/activate

Run:

.. code-block::

    lidar-read -l <location>


Related Files
-------------
- Private key for station must be located in /home/ccaruser/.keys


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
server located on cods.colorado.edu where the data is stored and analyzed. This program also blinks an LED to show
someone that it is running just by looking at the system.