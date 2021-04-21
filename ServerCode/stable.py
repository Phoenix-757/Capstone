from bluedot.btcomm import BluetoothServer
from time import sleep
from datetime import datetime
from signal import pause
import numpy as np
import pygame
import math
import ast

(width, height) = (1000,1000)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Mapping tool")
center = (int(width/2),int(height/2))

def reset_display():
#     sleep(0.25)
#     pygame.Surface.fill((255,255,255))
    pygame.draw.circle(screen, (0,0,0),center, 1000)
    pygame.draw.circle(screen, (0,0,255),center,250) #blue circle
    pygame.draw.circle(screen, (0,0,0),center,245) #black circle
    pygame.draw.circle(screen, (0,0,255),center,5) #center
    pygame.display.flip()
    
def data_received(data):
    print(data)
    # Data is split up into packets upon transfer, this creates one file/string for the entire scan
    file = open("STOP.txt", "r")
    string = file.read()
    combine_packets(data)
    if string == "":
        combine_packets(data)
        file_over = open("STOP.txt","w")
        file_over.write("ASDGHFSKDL:HFASDHK:F")
        file_over.close()
      
    
def combine_packets(data):
    packet_finished = False
    if data[0] == "[":
        file_over = open("text.txt","w")
        file_over.write(data)
        file_over.close()
        print("FIRST CHAR = {}".format(data[0]))
        if data[len(data) - 1] == "]":
            packet_finished = True
            print("LAST CHAR = {}".format(data[len(data) - 1]))
    elif data[len(data) - 1] == "]":
        file_append = open("text.txt","a")
        file_append.write(data)
        file_append.close()
        print("LAST CHAR = {}".format(data[len(data) - 1]))
        packet_finished = True
    else:
        file_append = open("text.txt","a")
        file_append.write(data)
        file_append.close()
    if packet_finished == True:
        processed_data = ""
        file_read = open("text.txt","r")
        string = file_read.read()
        print("Test {}".format(processed_data))
        processed_data = ast.literal_eval(str(string)) # ERROR parsing data
        display_data(processed_data)
#         reset_display()
#         file_reset = open("text.txt", "w")
#         file_reset.write("")
#         file_reset.close()
#         array = string.split("][")
#         bad_data = string.find("e")
#         if bad_data == -1: # if no e
#         processed_data = processed_data.index("][")
#             processed_data.split("[")
            
            

        # processed_data is a list of lists containing (quality, angle, distance)
        # processed_data[i][j]
        # [i] -> index in array of scanned information
        # [j] -> quality (0), angle (1), distance (2)

def form_list(data):
    angle = [angle[1] for angle in data]
    distance = [distance[2] for distance in data]
    angle = np.array(angle)
    distance = np.array(distance)
    array = np.stack((angle, distance), axis = 1)
#     print(array)
    return array
      
# Takes in a list of lists containing (quality, angle, distance) and maps them on a pygame window
def display_data(data):
    max_distance = 3000
    data = form_list(data)
    for i in range(0, len(data)):
        angle = data[i][0]
        print("ANGLE: {}".format(angle))
        distance = data[i][1]
        print("DISTANCE: {}".format(distance))
#         max_distance = max([min([5000,distance]), max_distance])
        rads = angle * math.pi / 180.0
        x = distance * math.cos(rads)
        y = distance * math.sin(rads)
        # oob -> just to mark if a value was greater than the max allowed distance, changes color of displayed point
        oob = False
        if x > max_distance:
            x = max_distance
            oob = True
        if y > max_distance:
            y = max_distance
            oob = True
        # 250,250 designates the center point of the circle
        # scalar with the thought of a 500x500 screen, all data within 3k will be displayed
        scalar = (1/6)
        point = (int(int(width/2) + scalar*(x)),int(int(height/2) + scalar*(y)))
        if oob == False:
            pygame.draw.circle(screen,(0,255,0),point,2)
        else:
            pygame.draw.circle(screen,(255,0,0),point,2)
#     sleep(0.1)
#     reset_display()
    
def client_connected():
    print("client connected")
    
def client_disconnected():
    print("client disconnected")
    
print("init")

server = BluetoothServer(
    data_received,
    auto_start = False,
    when_client_connects = client_connected(),
    when_client_disconnects = client_disconnected()
    )

server.start()
def run():
    running = True
    button_down = False
    reset_display()
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and button_down == False:                   
                    if event.key == pygame.K_UP:
                        # send start_motor() forward command
                        print("forward")
                        server.send("w")
                    elif event.key == pygame.K_LEFT:
                        # send turn_left() command
                        print("left")
                        server.send("a")
                    elif event.key == pygame.K_DOWN:
                        # send start_motor() backward command
                        print("back")
                        server.send("s")
                    elif event.key == pygame.K_RIGHT:
                        # send turn_right() command
                        print("right")
                        server.send("d")
                    elif event.key == pygame.K_q:
                        print("scan")
                        server.send("scan")
                    elif event.key == pygame.K_r:
                        print("reset display")
                        reset_display()
                    button_down = True
                elif event.type == pygame.KEYUP and button_down == True:
                    # send stop_motor()
                    print("stop")
                    server.send("stop")
                    button_down = False
                sleep(0.1)
            pygame.display.flip()
#             reset_display()
            #server.send("from server to client {} \n".format(str(datetime.now())))
#         sleep(0.1)
    except KeyboardInterrupt as e:
        print("cancelled by user")
    except Exception as e:
        print("Encountered an exception")
    finally:
        print("stopping")
        file_over = open("text.txt","w")
        file_over.write("")
        file_over.close()
        file_over = open("STOP.txt","w")
        file_over.write("")
        file_over.close()
        server.stop()
        pygame.quit()
    print("stopped")
    
    


run()
