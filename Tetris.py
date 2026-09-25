import tkinter as tk
from tkinter import Canvas
import random as rand
import threading
import keyboard
import time

#importing copy because copy wan't copy enough for our copy needs
import copy
#(Well its actually cause we need the scope copying that copy.deepcopy offers)

root = tk.Tk()
root.geometry("400x960")

class Tetris:
    def __init__(self, root):
        self.canvas = tk.Canvas(root, width=400, height=960, bg="#00FF00")
        self.canvas.pack()
        self.reference_cooldown = .25
        self.update_cooldown = .25
        root.bind("<Right>", self.MoveRight)
        root.bind("<Left>", self.MoveLeft)
        root.bind("<x>", self.RotateLeft)
        root.bind("<z>", self.RotateRight)
        root.bind("<KeyPress-Down>", self.FastSpeed)
        root.bind("<KeyRelease-Down>", self.NormalSpeed)
        self.lines_num = 0
        self.block_active = False
        self.grid_squares = {}
        self.block_templates = {
            "t_block": [[False, False, True, False], [False, True, True, True]],
            "right_L": [[False, True, True, True], [False, False, False, True]],
            "left_L": [[False, True, True, True], [False, True, False, False]],
            "o_block": [[False, True, True, False], [False, True, True, False]],
            "line_block": [[False, False, False, False], [True, True, True, True]],
            "right_Z": [[False, False, True, True], [False, True, True, False]],
            "left_Z": [[False, True, True, False], [False, False, True, True]]
        }
        self.possible_blocks = ["t_block", "right_L", "left_L", "o_block", "line_block", "right_Z", "left_Z"]
        self.current_block = {}
        self.color = "#1100FF"
        
        
        for row in range(24):
            for col in range(10):
                id = self.canvas.create_rectangle(col * 40, row * 40, col * 40 + 40, row * 40 + 40, fill="#777777", outline="white")
                self.grid_squares.update({(row, col): False})

    def UpdateBoard(self):
        while True:
            #Resetting for next update
            self.next_update = copy.deepcopy(self.grid_squares)
            time.sleep(self.update_cooldown)

            #If there is not a block active on the screen, make one
            
            if not self.block_active:
                self.block_color = rand.choice(self.color)
                self.current_block = {}
                block = rand.choice(self.possible_blocks)
                self.current_block.update({"coords": [], "block": block, "rotation": 0})
                for i in range(2):
                    for k in range(4): 
                        self.next_update[(i, k + 4)] = self.block_templates[self.current_block["block"]][i][k]
                        if self.block_templates[self.current_block["block"]][i][k]:
                            self.current_block["coords"].append((i, k + 4))
                        
                self.block_active = True

            #if there is one, we need to move it down
            else:
                # TLDR;
                # Calculate whether current block moves
                # MoveCheck() does that logic

                # if it does; then move it down, next turn

                # else; that means that the block is not longer moving
                # LineDeletion() will do most of that logic
                
                # Apply changes
                # continue onto RenderBoard()

                marked_coords = []
                does_move = self.MoveCheck()
                if does_move:
                    for coord in self.grid_squares:
                        row, col = coord
                        if (row, col) in self.current_block["coords"]:
                            marked_coords.append(coord)

                    for coord in self.grid_squares:
                        if coord in marked_coords:
                            row, col = coord
                            self.next_update[coord] = False
                            self.next_update[(row + 1, col)] = True
                            self.current_block["coords"].remove(coord)
                            self.current_block["coords"].append((row + 1, col))

                    #This code standardizes next_update and current_block's coords 
                    #This should be happening at the code above this..?
                    #But isnt(?) so I do it here for safe measure
                    for coord in self.grid_squares:
                        row, col = coord
                        if coord in self.current_block["coords"] and self.next_update[(row, col)] == False:
                            self.next_update[(row, col)] = True
                else:
                    self.block_active = False
                    self.LineDeletion()

            self.RenderBoard()


    def LineDeletion(self):
        #TLDR;
        #check every col in a row; 
        #if all are True, delete that row and move the grid down 1
        #repeat for all rows marked

        rows_marked = []

        #check all the cols:
        for row in range(24):
            flag = True
            for col in range(10):
                if self.next_update[row, col] == True:
                    pass
                else:
                    flag = False

            #if all are True:
            if flag:
                rows_marked.append(row)

        #delete that row:
        for row in rows_marked:
            for col in range(10):
                self.next_update[row, col] = False

        self.lines_num += len(rows_marked)

        if self.lines_num > 20:
            self.color = "#CA3737"
            self.reference_cooldown = .075
        elif self.lines_num > 10:
            self.color = "#C9C90C"
            self.reference_cooldown = .15

        iterator_list = copy.copy(rows_marked)

        #move the grid down 1:
        for val in iterator_list:
            row = min(rows_marked)

            #it moves down by making its value equal to the value of the squaure below it
            for i in range(row):
                for col in range(10):
                    #make sure not to generate new coords at row = 24+
                    if row - i + 1 <= row:
                        self.next_update[(row - i + 1, col)] = self.next_update[(row - i, col)]

            rows_marked.remove(val)
        
    def MoveCheck(self):
        #TLDR; 
        #if empty space below current active block: continue loop 
        #else: return False

        #setting it to 25 so any block higher will be registered
        #essentially finding what row is upper most of the block of the current block
        lowest_row = 25
        for coords in self.current_block["coords"]:
            test_row, test_col = coords
            if test_row < lowest_row:
                lowest_row = test_row

        for coords in self.current_block["coords"]:
            block_row, block_col = coords

            #need to skip every blocks physics calculations if it has a block below it in the active block
            #as to avoid a block like the Z block from activating itself
            if (block_row + 1, block_col) in self.current_block["coords"]:
                continue
            else:
                #if block suceeds last check, and there is another block under it, 
                #that means it has hit the main grid and gets deactivated.
                try:
                    if self.grid_squares[(block_row + 1, block_col)] == True:
                        return False
                    else:
                        continue

                #If KeyError happens; that means it has hit the bottom edge, or the 'floor' of the grid and should stop
                #Prints to make sure it is the left_L kind of key error
                except KeyError:
                    print((block_row - 1, block_col))
                    return False

                except Exception as e:
                    print(e)
                    return False
            
        return True

    def RenderBoard(self):
        for row in range(24):
            for col in range(10):
                id = (row * 10 + col) + 1
                if self.next_update[(row, col)] == True:
                    self.canvas.itemconfig(id, fill=self.color)
                else:
                    self.canvas.itemconfig(id, fill="#777777")
        self.grid_squares = copy.deepcopy(self.next_update)
        root.update()

    def MoveDir(self, dir):
        marked_coords = copy.copy(self.current_block["coords"])
                
        for coord in marked_coords:
            row, col = coord
            self.current_block["coords"].remove(coord)
            self.current_block["coords"].append((row, col + dir))
            self.next_update[(row, col)] = False
            self.next_update[(row, col + dir)] = True

        #Standardizes self.next_update with self.current_block
        for coord in self.grid_squares:
            row, col = coord
            if coord in self.current_block["coords"] and self.next_update[(row, col)] == False:
                self.next_update[(row, col)] = True
        self.RenderBoard()

    def LBlockProcessing(self):
        #TLDR; the rotation point is the non-corner block touching two blocks
        #Find that
        for coord in self.current_block["coords"]:
            row, col = coord
                
            #block of elifs detecting if it is the diag of any other piece. 
            if (row + 1, col + 1) in self.current_block["coords"]:
                other_diag = [(row + 1, col + 1), (1, 1)]
            elif (row + 1, col - 1) in self.current_block["coords"]:
                other_diag = [(row + 1, col - 1), (1, -1)]
            elif (row - 1, col + 1) in self.current_block["coords"]:
                other_diag = [(row - 1, col + 1), (-1, 1)]
            elif (row - 1, col - 1) in self.current_block["coords"]:
                other_diag = [(row - 1, col - 1), (-1, -1)]
            else:
                continue

            primary_diag = coord
            break
        
        trans_row, trans_col = other_diag[1]
        test_row, test_col = other_diag[0]
        row, col = primary_diag

        #Testing whether this line has the 2 block in a row pattern, if so this block is the correct block
        if (row - trans_row, col) in self.current_block["coords"]:
            rotation_point = (row, col)
        elif (row, col - trans_col) in self.current_block["coords"]:
            rotation_point = (row, col)
        elif (test_row + trans_row, test_col) in self.current_block["coords"]:
            rotation_point = (row, col)
        elif (test_row, test_col + trans_col) in self.current_block["coords"]:
            rotation_point = (row, col)
        else:
            print("This should not be reachable. If you reached it, congrats")

        return rotation_point

    def ZBlockProcessing(self):
        match self.current_block["rotation"]:
            case 0:
                #If there is a block below this block; which is only true for the rotation point at the Z blocks when at rotation 0
                for coord in self.current_block["coords"]:
                    row, col = coord
                    if (row + 1, col) in self.current_block["coords"]:
                        return (row, col)
            case 90:
                #If there is a block to the right of this block; which is only true for the rotation point at the Z blocks when at rotation 90
                for coord in self.current_block["coords"]:
                    row, col = coord
                    if (row, col + 1) in self.current_block["coords"]:
                        return (row, col)
            case 180:
                #If there is a block to the above this block; which is only true for the rotation point at the Z blocks when at rotation 180
                for coord in self.current_block["coords"]:
                    row, col = coord
                    if (row - 1, col) in self.current_block["coords"]:
                        return (row, col)
            case 270:
                #If there is a block to the left of this block; which is only true for the rotation point at the Z blocks when at rotation 90
                for coord in self.current_block["coords"]:
                    row, col = coord
                    if (row, col - 1) in self.current_block["coords"]:
                        return (row, col)
    
    def Rotate(self, theta):
        flag = False
        lowest_row = 25
        for coords in self.current_block["coords"]:
            test_row, test_col = coords
            if test_row < lowest_row:
                lowest_row = test_row

        #As in not found; we check if it is found later
        other_diag = False
        match self.current_block["block"]:
            case "o_block":
                pass
            
            case "right_L":
                rotation_point = self.LBlockProcessing()
                        
            case "left_L":
                rotation_point = self.LBlockProcessing()

            case "right_Z":
                rotation_point = self.ZBlockProcessing()

            case "left_Z":
                rotation_point = self.ZBlockProcessing()

            case "t_block":
                #TLDR; the only block touching 3 other blocks is the rotation point. 
                #So find that
                for coord in self.current_block["coords"]:
                    row, col = coord
                    flags = []
                    if (row + 1, col) in self.current_block["coords"]:
                        flags.append(1)
                    if (row - 1, col) in self.current_block["coords"]:
                        flags.append(2)
                    if (row, col + 1) in self.current_block["coords"]:
                        flags.append(3)
                    if (row, col - 1) in self.current_block["coords"]:
                        flags.append(4)
                    if len(flags) == 3:
                        rotation_point = coord
                        break
            
            case "line_block":
                match self.current_block["rotation"]:
                    case 0:
                        least_col = 25
                        for coord in self.current_block["coords"]:
                            row, col = coord
                            if col < least_col:
                                least_col = col
                        for coord in self.current_block["coords"]:
                            row, col = coord
                            if col == least_col + 1:
                                rotation_point = coord
                    case 90:
                        highest_row = 0
                        for coord in self.current_block["coords"]:
                            row, col = coord
                            if row > highest_row:
                                highest_row = row
                        for coord in self.current_block["coords"]:
                            row, col = coord
                            if row == highest_row - 1:
                                rotation_point = coord
                    case 180:
                        highest_col = 0
                        for coord in self.current_block["coords"]:
                            row, col = coord
                            if col > highest_col:
                                highest_col = col
                        for coord in self.current_block["coords"]:
                            row, col = coord
                            if col == highest_col - 1:
                                rotation_point = coord
                    case 270:
                        least_row = 25
                        for coord in self.current_block["coords"]:
                            row, col = coord
                            if row < least_row + 1:
                                least_row = row
                        for coord in self.current_block["coords"]:
                            row, col = coord
                            if row == least_row:
                                rotation_point = coord
                    case _:
                        print("This code is unreachable for a reason")
                
        marked_coords = []
        row, col = rotation_point
        for coord in self.current_block["coords"]:
            #TLDR;
            #Transform all points so that the rotation_point is at the origin (0, 0)
            #Apply relavant rotation (depending on whether theta is 90 or -90)
            #Transform value back to where it should be

            #Rotating the rotation_point shouldn't do anything; but just to be safe
            if coord == rotation_point:
                continue

            #copies test values to be transformed
            test_row, test_col = coord
            test2_row = test_row
            test2_col = test_col

            #standardizes test_row and test_col so the rotation point is at the origin
            test2_row -= row
            test2_col -= col

            if theta == 90:
                #Applys a 90 degree counter-clockwise rotation
                #(x, y) => (-y, x)
                #Then put it back where it started with a translation (-y + row, x + col)
                new_coord = (-test2_col + row, test2_row + col)
                self.current_block["rotation"] += 90
                self.current_block["rotation"] = self.current_block["rotation"] % 360

            elif theta == -90:
                #Applys a 270 degree counter-clockwise rotation (or 90 degrees clockwise)
                #(x, y) => (y, -x)
                #Then put it back where it started with a translation (y + row, -x + col)
                new_coord = (test2_col + row, -test2_row + col)
                self.current_block["rotation"] -= 90
                self.current_block["rotation"] = self.current_block["rotation"] % 360

            #Check if you can actually rotate here
            test3_row, test3_col = new_coord
            if test3_row < 0 or test3_row > 23 or test3_col < 0 or test3_col > 9:
                flag = True
            elif (self.grid_squares[new_coord] == True and not new_coord in self.current_block["coords"]):
                flag = True

            #Store both the new value and the old value to be erased
            marked_coords.append([(test_row, test_col), new_coord])

        #if the values are actually valid, do the transformation
        if not flag:
            for list in marked_coords:
                old_coord = list[0]
                new_coord = list[1]
                row, col = coord
                self.current_block["coords"].remove(old_coord)
                self.current_block["coords"].append(new_coord)
                self.next_update[old_coord] = False
                self.next_update[new_coord] = True

            #Standardizes self.next_update with self.current_block; cause the code above this has some stupid bug I've thrown myself at for 2 days at this point
            #Just giving up and using this to fix it
            for coord in self.grid_squares:
                row, col = coord
                if coord in self.current_block["coords"] and self.next_update[(row, col)] == False:
                    self.next_update[(row, col)] = True
            self.RenderBoard()

    def MoveRight(self, event):
        flag = False
        for coord in self.grid_squares:
            row, col = coord

            #if (row, col + 1) makes col > 9; it throws an error
            #this doesn't destroy the script, it is an intended error to prevent execution
            if coord in self.current_block["coords"]:
                if col + 1 <= 9 and (self.grid_squares[row, col + 1] == False or (row, col + 1) in self.current_block["coords"]):
                    pass
                else:
                    flag = True
                    break
        if not flag:
            self.MoveDir(1)

    def MoveLeft(self, event):
        flag = False
        for coord in self.grid_squares:
            row, col = coord

            #if (row, col - 1) makes col < 0; it throws an error
            #this doesn't destroy the script, it is an intended error to prevent execution
            if coord in self.current_block["coords"]:
                if col - 1 >= 0 and (self.grid_squares[row, col - 1] == False or (row, col - 1) in self.current_block["coords"]):
                    pass
                else:
                    flag = True
                    break
        if not flag:
            self.MoveDir(-1)

    def RotateLeft(self, event):
        self.Rotate(-90)

    def RotateRight(self, event):
        self.Rotate(90)

    def FastSpeed(self, event):
        self.update_cooldown = self.reference_cooldown/10

    def NormalSpeed(self, event):
        self.update_cooldown = self.reference_cooldown

Game = Tetris(root)

try:
    Game.UpdateBoard()
except Exception as e:
    print(e)