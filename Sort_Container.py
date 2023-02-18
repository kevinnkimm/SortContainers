ip_address = 'localhost' # Enter your IP Address here
project_identifier = 'P3B' # Enter the project identifier i.e. P3A or P3B

# SERVO TABLE CONFIGURATION
short_tower_angle = 315 # enter the value in degrees for the identification tower 
tall_tower_angle = 90 # enter the value in degrees for the classification tower
drop_tube_angle = 180 # enter the value in degrees for the drop tube. clockwise rotation from zero degrees

# BIN CONFIGURATION
# Configuration for the colors for the bins and the lines leading to those bins.
# Note: The line leading up to the bin will be the same color as the bin 

bin1_offset = 0.2 # offset in meters
bin1_color = [1,0,0] # e.g. [1,0,0] for red
bin1_metallic = False

bin2_offset = 0.2
bin2_color = [0,1,0]
bin2_metallic = False

bin3_offset = 0.20
bin3_color = [0,0,1]
bin3_metallic = False

bin4_offset = 0.20
bin4_color = [1,1,1]
bin4_metallic = False
#--------------------------------------------------------------------------------
import sys
sys.path.append('../')
from Common.simulation_project_library import *

hardware = False
if project_identifier == 'P3A':
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    configuration_information = [table_configuration, None] # Configuring just the table
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
else:
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    bin_configuration = [[bin1_offset,bin2_offset,bin3_offset,bin4_offset],[bin1_color,bin2_color,bin3_color,bin4_color],[bin1_metallic,bin2_metallic, bin3_metallic,bin4_metallic]]
    configuration_information = [table_configuration, bin_configuration]
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
    bot = qbot(0.1,ip_address,QLabs,project_identifier,hardware)
#--------------------------------------------------------------------------------
# STUDENT CODE BEGINS
#---------------------------------------------------------------------------------
import random
import time
deposit = True
deposited = False
seeking = True
returned = False
bin_id = 1
start = bot.position()
print(round(start[0], 2))
print(round(start[1], 1))
bot.activate_color_sensor()
bot.activate_line_following_sensor()
color_sensor_reader = bot.read_color_sensor()[0]
previous_val = "none"

def dispense_container():
    #dispenses a random bottle from 1 to 6
    bottle_type = random.randint(1, 6)

    #sets the random container dispensed as True
    container_type = table.dispense_container(bottle_type, True)

    return container_type


def load_container(previous_val):
    global bin_id
    
    #empty list
    items = []     # list of items loaded in the Q-bot
    
    if previous_val == "none":
        dispense = table.dispense_container(random.randint(1,6), True)    # dispenses ranom container and gets conhtainer values
        items.append(dispense)
        pass
    else:
        items.append(previous_val)       #adds the previous container value 
    # appends the bin id
    bin_id = items[0][2]
    mass = items[0][1]
    # loads the container
    arm.move_arm(0.644,0.0,0.2733)
    time.sleep(1)
    arm.control_gripper(45)
    time.sleep(1)
    arm.move_arm(0.4064, 0.0, 0.4826)
    time.sleep(1)
    arm.rotate_base(-90)
    time.sleep(1)
    arm.move_arm(0.019, -0.55, 0.5)
    time.sleep(1)
    arm.control_gripper(-25)
    time.sleep(1)
    arm.move_arm(0.0, -0.2874, 0.77)
    time.sleep(1)
    arm.home()
    time.sleep(1)
    # finishes loading
    while len(items) < 3:                                             # while loop if items in Q-bot are under 3
        dispense2 = table.dispense_container(random.randint(1,6), True)
        print("This is the list items: ",items)
        print(f'This is items {items[0][2]} and new item is {dispense2[2]}')
        
        if (items[0][2] == dispense2[2]) and (mass <= 90):
            # loads container and adds mass if conditions are met
            items.append(dispense2)
            mass = mass + dispense2[1]
            arm.move_arm(0.644,0.0,0.2733)
            time.sleep(1)
            arm.control_gripper(45)
            time.sleep(1)
            arm.move_arm(0.4064, 0.0, 0.4826)
            time.sleep(1)
            arm.rotate_base(-90)
            time.sleep(1)
            arm.move_arm(0.019, -0.55, 0.5)
            time.sleep(1)
            arm.control_gripper(-25)
            time.sleep(1)
            arm.move_arm(0.0, -0.2874, 0.77)
            time.sleep(1)
            arm.home()
            time.sleep(1)
            print(mass)
            # finished loading
        else:
            break           # breaks loop if not true
        
    return ["yes", items[0][2], dispense2] # returns Bin_ID of last container not sorted for the neposition_bott loop


def transfer_container():
    global deposit
    global deposited
    global seeking
    global bin_id
    global returned
    global color_sensor_reader
    line_following = bot.line_following_sensors() == [1, 1] 

# Continuously check the line following sensor
  
    #when seeking is True, bot moves forward in a straight line
    while seeking == True:
        color_sensor_reader = bot.read_color_sensor()[0]
        if bot.line_following_sensors() == [1, 1]:
            bot.set_wheel_speed([0.1,0.1])
        elif bot.line_following_sensors() == [1, 0]:
            bot.set_wheel_speed([0.05, 0.1])
        elif bot.line_following_sensors() == [0, 1]:
            bot.set_wheel_speed([0.1, 0.05])
        else:
            bot.set_wheel_speed([0.05, 0.1])
            
            
        #conditions to target the correct bin through the rgb value and if the bot is going in a straight line
        if bin_id == "Bin01" and color_sensor_reader == [1, 0, 0] and line_following == True:
            time.sleep(3.5)
            bot.set_wheel_speed([0,0])
            seeking = False
            deposit = True
        
        elif bin_id == "Bin02" and color_sensor_reader == [0, 1, 0] and line_following == True:
            time.sleep(2)
            bot.set_wheel_speed([0,0])
            seeking = False
            deposit = True
       
        elif bin_id == "Bin03" and color_sensor_reader == [0, 0, 1] and line_following == True:
            time.sleep(3.5)
            bot.set_wheel_speed([0,0])
            seeking = False
            deposit = True
       
        elif bin_id == "Bin04" and color_sensor_reader == [1, 1, 1] and line_following == True:
            time.sleep(2)
            bot.set_wheel_speed([0,0])
            seeking = False
            deposit = True
    
def deposit_container():
    global deposit
    global deposited
    global seeking
    global bin_id
    global returned
    
    #uses conditionals to determine the whether the containers have been deposited
    if deposit == True and deposited == False:
        bot.stop()
        print("Bot has stopped")
        bot.activate_linear_actuator()
        
        #loops through the rotate_hopper function
        for i in range(2):
            bot.rotate_hopper(45*i)
            time.sleep(0.1)
        
        #deactivates the deposit function
        bot.rotate_hopper(-90)
        time.sleep(2)
        bot.deactivate_linear_actuator()
        deposited = False
        deposit = False
        returned = True

def return_container():

    #activates the line following sensor
    bot.activate_line_following_sensor()

    position_bot = bot.position()

    #loops the bot to return to its original start position
    while (round(position_bot[0], 1) != round(start[0], 1)) or (round(position_bot[1], 1)) != round(start[1], 1):

        #follows the straight line
        if bot.line_following_sensors() == [1, 1]:
            bot.set_wheel_speed([0.1,0.1])
        elif bot.line_following_sensors() == [1, 0]:
            bot.set_wheel_speed([0.05, 0.1])
        elif bot.line_following_sensors() == [0, 1]:
            bot.set_wheel_speed([0.1, 0.05])
        else:
            bot.set_wheel_speed([0.05, 0.1])
        position_bot = bot.position()
        
    bot.stop()
           

def main():
    global deposit
    global deposited
    global seeking
    global bin_id
    global returned
    global color_sensor_reader
    global bot_position
    global previous_val

    #loops through every function above
    while True:
        position_bot = load_container(previous_val)
        previous_val = position_bot[2]
        bot_position = bot.position()
        
        transfer_container()

        #calls the deposit_container function if these conditions hold true
        if deposit == True and deposited == False:
            deposit_container()

        #calls the return container function if container has been returned
        if returned == True:
            return_container()
            
        seeking = True

main()
   












#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------
    

