

import os, sys, json, datetime, re  # Provides OS-dependent functionality, system-specific parameters, JSON handling, and date/time manipulation
import pandas as pd             # Provides data structures and data analysis tools
import numpy as np              # Supports large, multi-dimensional arrays and matrices
import requests
import time
from tqdm import tqdm
import glob as glob



hunt_blue = "#002C99"
hunt_purple = "#63007E"
hunt_red = "#C2002E"



#greys
hunt_gray10 = "#EAEBEB"
hunt_gray30 = "#C2C3C5"
hunt_gray50 = "#999B9F"
hunt_darkgray= "#333740"



hunt_dark_blue = "#001F71"
hunt_darker_blue = "#00154B"
hunt_dark_purple = "#500066"
hunt_darker_purple = "#280033"
hunt_light_purple = "#DCA3EB"

hunt_dark_red = "#79001D"
hunt_darker_red = "#3A000B"

hunt_acc_aq_blue = "#5DC2D0"
# hunt_acc_red = "#001F71"
hunt_acc_orange = "#D77900"
hunt_acc_green = "#00B188"
hunt_acc_sky_blue = "#89B8EA"



accent_colors = [hunt_blue, hunt_acc_aq_blue, hunt_red, hunt_acc_orange, hunt_acc_green, hunt_purple, hunt_gray30, hunt_darkgray, hunt_acc_sky_blue]
r_and_e_colors = {'black':hunt_blue, "two_or_more":hunt_acc_green, "other":hunt_gray30, "white":hunt_acc_sky_blue, "hispanic":hunt_acc_orange, "aapi":hunt_purple,"native":hunt_acc_aq_blue,"pacific_islander": hunt_darker_purple, "all":hunt_darkgray}
