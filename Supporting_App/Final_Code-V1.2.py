
from os import system
import bluetooth
import time
import socket
from PIL import Image as Image1
import numpy as np
from wand.image import Image
import ffmpeg
import tkinter as tk
from tkinter import filedialog
from PIL import ImageDraw, ImageFont
import cv2

def send_values(sock, chunk, colourkey, colour):

    chunk.append(ord(colourkey))
    chunk.extend(colour[0:500])
    sock.send(chunk)
    chunk.clear()
    time.sleep(0.0001)
    chunk.append(ord(colourkey))
    chunk.extend(colour[500:1000])
    sock.send(chunk)
    chunk.clear()
    time.sleep(0.0001)
    chunk.append(ord(colourkey))
    chunk.extend(colour[1000:1500])
    sock.send(chunk)
    chunk.clear()
    time.sleep(0.0001)
    chunk.append(ord(colourkey))
    chunk.extend(colour[1500:2000])
    sock.send(chunk)
    chunk.clear()
    time.sleep(0.0001)
    chunk.append(ord(colourkey))
    chunk.extend(colour[2000:2500])
    sock.send(chunk)
    chunk.clear()
    time.sleep(0.0001)

def menu():
    choice = input("Plese select a mode Slideshow, upload, video, text (1,2 3 or 4): ")
    system('cls')
    return choice

def slideshow_mode(sock):
    slide = bytearray()
    slide.append(ord('s'))
    sock.send(slide)
    slide.clear()


def upload_mode(sock):
    up = bytearray()
    up.append(ord('w'))
    sock.send(up)
    up.clear()
    while True:
        Pic = input("Please press enter to continue or 2 to exit: ")
        if Pic != '2':
            root = tk.Tk()
            root.withdraw()

            file_path = filedialog.askopenfilename(
                title="Select a file",
                filetypes=[("All Files", "*.*")]  
            )
            contrast = input("Please enter Contrast Level (1-5): ")
            if contrast == '1':
                blackpoint = 0.2
            elif contrast == '2':
                blackpoint = 0.3
            elif contrast == '3':
                blackpoint = 0.45
            elif contrast == '4':
                blackpoint = 0.55
            elif contrast == '5':
                blackpoint = 0.6
            else:
                blackpoint = 0.3
            img = cv2.imread(file_path)
            f = 500 
            h, w = img.shape[:2]
            # Create coordinate arrays for each pixel
            x, y = np.meshgrid(np.arange(w), np.arange(h))
    
            # Image center
            cx, cy = w / 2.0, h / 2.0
    
            # For vertical pre-distortion, keep x unchanged.
            map_x = x.astype(np.float32)
 
            # Apply the inverse mapping for vertical cylindrical projection:
            map_y = f * np.arctan((y - cy) / f) + cy

            # Remap the image using these maps.
            warped = cv2.remap(img, map_x, map_y.astype(np.float32), 
                               interpolation=cv2.INTER_LINEAR, 
                               borderMode=cv2.BORDER_CONSTANT)

            cv2.imwrite('warped_output.jpg', warped)

            with Image(filename='warped_output.jpg') as imag:
                imag.level(blackpoint,0.9,gamma=1.1)
                imag.save(filename= 'output_contrasted.jpg')
    


            image = Image1.open('output_contrasted.jpg')      #reads teh image as an object
            new_image = image.resize((50,50))            #uses thumbnail() to resize image
            new_image.save('Final.jpg')                 #saves the resized image as a new file

            a = np.asarray(new_image)   #converts the image object to an array

            red = []
            blue = []
            green = []

            for row in a:                                             
                for x in row:
                    red.append(x[0])
                    green.append(x[1])
                    blue.append(x[2])


            chunk = bytearray()

            send_values(sock, chunk, 'r', red)

            send_values(sock, chunk, 'g', green)

            send_values(sock, chunk, 'b', blue)

            print("sent")
            system('cls')
        else:
            system('cls')
            break

def stream_mode(sock):
    up = bytearray()
    up.append(ord('w'))
    sock.send(up)
    up.clear()

    frame_width = 50
    frame_height = 50
    fixed_fps = 5
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[("All Files", "*.*")]  
    )

    stream = ffmpeg.input(file_path)

    stream = stream.filter('scale', frame_width, frame_height).filter('fps', fps=fixed_fps).filter('eq', contrast=4)

    process = (
        stream
        .output('pipe:', format='rawvideo', pix_fmt='rgb24')
        .run_async(pipe_stdout=True, pipe_stderr=True)
    )

    try:
        while True:
            in_bytes = process.stdout.read(frame_width * frame_height * 3)
            if not in_bytes:
                err = process.stderr.read(10024)
                print("FFmpeg stderr:", err.decode('utf-8', errors='ignore'))
                wait = input()
                break  

            frame = np.frombuffer(in_bytes, np.uint8).reshape((frame_height, frame_width, 3))

            red_bytes = []     
            green_bytes = []  
            blue_bytes = []    

            for row in frame:  
                for x in row:
                    red_bytes.append(x[0])
                    green_bytes.append(x[1])
                    blue_bytes.append(x[2])

            chunk = bytearray()

            send_values(sock, chunk, 'r', red_bytes)

            send_values(sock, chunk, 'g', green_bytes)

            send_values(sock, chunk, 'b', blue_bytes)

            red_bytes.clear()    
            green_bytes.clear()  
            blue_bytes.clear()

    except Exception as e:
        print("Error:", e)
    finally:
        process.stdin.close()
        process.stderr.close()
        process.stdout.close()
        process.wait()


def Text_mode(sock):
    up = bytearray()
    up.append(ord('w'))
    sock.send(up)
    up.clear()

    choice = input("Choose a colour from red, blue, green, yellow, violet, light blue (1-6): ")
    
    if choice == '1':
        colour = (255,0,0)
    elif choice == '2':
        colour = (0,0,255)
    elif choice == '3':
        colour = (0,255,0)
    elif choice == '4':
        colour = (255,255,0)
    elif choice == '5':
        colour = (255,0,255)
    elif choice == '6':
        colour = (0,255,255)

    img = Image1.new('RGB', (50, 50), color=(0, 0, 0))
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype('verdana.ttf', 8)
    line_1 = input("Input line 1(CAPS ONLY, MAX LENGTH 9): ")
    line_2 = input("Input line 2(CAPS ONLY, MAX LENGTH 9): ")
    line_3 = input("Input line 3(CAPS ONLY, MAX LENGTH 9): ")
    line_4 = input("Input line 4(CAPS ONLY, MAX LENGTH 9): ")
    d.text((0,2), line_1, font=fnt, fill=colour)
    d.text((0,12), line_2, font=fnt, fill=colour)
    d.text((0,22), line_3, font=fnt, fill=colour)
    d.text((0,32), line_4, font=fnt, fill=colour)
    img.save('text_image.jpg')

    #fnt = ImageFont.truetype('verdana.ttf', 12)
    #line_1 = input("Input line 1(CAPS ONLY, MAX LENGTH 9): ")
    #line_2 = input("Input line 2(CAPS ONLY, MAX LENGTH 9): ")
    ##line_3 = input("Input line 3(CAPS ONLY, MAX LENGTH 9): ")
    #line_4 = input("Input line 4(CAPS ONLY, MAX LENGTH 9): ")
    #d.text((0,2), line_1, font=fnt, fill=colour)
    #d.text((0,15), line_2, font=fnt, fill=colour)
    ##d.text((0,22), line_3, font=fnt, fill=colour)
    #d.text((0,28), line_4, font=fnt, fill=colour)
    #img.save('text_image.jpg')

    a = np.asarray(img)   #converts the image object to an array

    red = []
    blue = []
    green = []

    for row in a:                                             
        for x in row:
            red.append(x[0])
            green.append(x[1])
            blue.append(x[2])

    chunk = bytearray()
    send_values(sock, chunk, 'r', red)

    send_values(sock, chunk, 'g', green)

    send_values(sock, chunk, 'b', blue)

    print("sent")
    system('cls')



def main():
    bd_addr = "fc:e8:c0:7b:41:72"

    port = 1
    socket=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    socket.connect((bd_addr, port))
    while True:
        mode = menu()
        if mode == '1':
            slideshow_mode(socket)
        elif mode == '2':
            upload_mode(socket)
        elif mode == '3':
            stream_mode(socket)
        elif mode == '4':
            Text_mode(socket)

if __name__ == '__main__':
    main()


