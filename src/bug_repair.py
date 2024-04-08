import pyautogui
import time
import win32gui
import win32gui
import win32api
import win32con
import ctypes

pyautogui.FAILSAFE=False

def bug_repair(location, proxy_num=0):
    for i in range(len(location)):
        # 移动鼠标到第一个move的目标位置
        if i == 0:
            pyautogui.moveTo(location[i][0], location[i][1], duration=0.5)
        else:
            pyautogui.moveTo(location[i][0], location[i][1]+proxy_num*50, duration=0.5)
        pyautogui.click()
        time.sleep(0.5)


    
def record_location(num):
    location = []
    print("start")
    for i in range(num):
        time.sleep(2)
        location.append(pyautogui.position())
        print(pyautogui.position())
    print(location)
    return location


if __name__ == '__main__':
    time.sleep(2)
    # record location of the mouse 
    location = []
    num = 2
    location = record_location(num)
    time.sleep(2)

    bug_repair(location)






