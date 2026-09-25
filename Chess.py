import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import math
import time

#importing copy because the normal copy() wasn't copy enough for our copy needs
import copy
#(we need copy.deepcopy() for dictionary scope copying)

root = tk.Tk()

root.geometry("800x800")
class ChessBoard:
    def __init__(self, root):
        self.canvas = tk.Canvas(root, width=800, height=800, bg="white")
        self.canvas.pack()
        self.selected_piece = None
        self.side_playing = "white"
        self.in_check = False

        #giant list of the starting places of each chess piece
        default_filepath = "D:/Python projects/Games/Chess/"
        self.filepaths = {
            "blackRook": default_filepath + "Rooks/blackRook.png",
            "blackKnight": default_filepath + " Knights/blackKnight.png",
            "blackBishop": default_filepath + "Bishops/blackBishop.png",
            "blackQueen": default_filepath + "Queens/blackQueen.png",
            "blackKing": default_filepath + "Kings/blackKing.png",
            "blackPawn": default_filepath + "Pawns/blackPawn.png",
            "whitePawn": default_filepath + "Pawns/whitePawn.png",
            "whiteRook": default_filepath + "Rooks/whiteRook.png",
            "whiteKnight": default_filepath + "Knights/whiteKnight.png",
            "whiteBishop": default_filepath + "Bishops/whiteBishop.png",
            "whiteQueen": default_filepath + "Queens/whiteQueen.png",
            "whiteKing": default_filepath + "Kings/whiteKing.png",
        }
        self.piece_locations = {
            "blackRook1": {"coords": (0,0), "has_moved": False},
            "blackKnight1": {"coords": (0,1), "has_moved": False},
            "blackBishop1": {"coords": (0,2), "has_moved": False},
            "blackQueen": {"coords": (0,3), "has_moved": False},
            "blackKing": {"coords": (0,4), "has_moved": False},
            "blackBishop2": {"coords": (0,5), "has_moved": False},
            "blackKnight2": {"coords": (0,6), "has_moved": False},
            "blackRook2": {"coords": (0,7), "has_moved": False},
            "blackPawn1": {"coords": (1,0), "has_moved": False},
            "blackPawn2": {"coords": (1,1), "has_moved": False},
            "blackPawn3": {"coords": (1,2), "has_moved": False},
            "blackPawn4": {"coords": (1,3), "has_moved": False},
            "blackPawn5": {"coords": (1,4), "has_moved": False},
            "blackPawn6": {"coords": (1,5), "has_moved": False},
            "blackPawn7": {"coords": (1,6), "has_moved": False},
            "blackPawn8": {"coords": (1,7), "has_moved": False},
            "whitePawn1": {"coords": (6,0), "has_moved": False},
            "whitePawn2": {"coords": (6,1), "has_moved": False},
            "whitePawn3": {"coords": (6,2), "has_moved": False},
            "whitePawn4": {"coords": (6,3), "has_moved": False},
            "whitePawn5": {"coords": (6,4), "has_moved": False},
            "whitePawn6": {"coords": (6,5), "has_moved": False},
            "whitePawn7": {"coords": (6,6), "has_moved": False},
            "whitePawn8": {"coords": (6,7), "has_moved": False},
            "whiteRook1": {"coords": (7,0), "has_moved": False},
            "whiteKnight1": {"coords": (7,1), "has_moved": False},
            "whiteBishop1": {"coords": (7,2), "has_moved": False},
            "whiteQueen": {"coords": (7,3), "has_moved": False},
            "whiteKing": {"coords": (7,4), "has_moved": False},
            "whiteBishop2": {"coords": (7,5), "has_moved": False},
            "whiteKnight2": {"coords": (7,6), "has_moved": False},
            "whiteRook2": {"coords": (7,7), "has_moved": False}
        }
        self.piece_movements = {
            "Bishop": [(1,1),(1,-1),(-1,1),(-1,-1)],
            "Rook": [(-1,0), (0,-1), (1,0), (0,1)],
            "Queen": [(-1,0), (0,-1), (1,0), (0,1), (1,1),(1,-1),(-1,1),(-1,-1)],
            "blackPawn": [(-1,0), (-1,-1),(-1,1)],
            "whitePawn": [(-1,0), (-1,-1),(-1,1)],
            "Knight": [(-2,-1),(2,1),(-2,1),(2,-1),(-1,-2),(1,2),(-1,2),(1,-2)],
            "King": [(-1,0), (0,-1), (1,0), (0,1), (1,1),(1,-1),(-1,1),(-1,-1)]
            }
        
        
        self.images = {}
        self.square_dict = {}
        self.canvas.bind('<Button-1>', lambda event: self.UpdateBoard(event))
        for row in range(8):
            for col in range(8):
                #If XNOR of col%2 and row%2, so if both are 1 or both are 0, but not mixed
                if not col%2 ^ row%2:
                    color = "white"
                else:
                    color = "#C4C4C4"
                square_id = self.canvas.create_rectangle(col * 100, row * 100, col * 100 + 100, row * 100 + 100,fill=color)

                self.square_dict.update({square_id: [color, row, col]})

        #Makes the game board for the first time
        self.UpdateImages()

    def UpdateImages(self):
        for image_id in self.images.values():
            self.canvas.delete(image_id)
        self.images.clear()
        for piece, value in self.piece_locations.items():
            coords = self.piece_locations[piece]["coords"]
            row, col = coords
            if piece[len(piece) - 1:len(piece)].isalpha():
                filepath = self.filepaths[piece]
            else:
                filepath = self.filepaths[piece[0:len(piece) - 1]]
            image = tk.PhotoImage(file=filepath, width=60, height=60)
            image_id = self.canvas.create_image(col*100 + 50, row*100 + 50, image=image)
            self.images.update({image: image_id})              

    def UpdateBoard(self, event):
        pawn_list = ["whitePawn", "blackPawn"]
        castle_id = []
        piece = None
        piece_found = False
        row = event.y // 100
        col = event.x // 100
        highlighted_squares = []
        ran = False
        id = (row * 8 + col) + 1

        #Code that runs if cell selected is possible capture square
        if self.canvas.itemcget(id, "fill") == "#D41313":
            for piece, value in self.piece_locations.items():
                if value["coords"] == (row, col):
                    marked_piece = piece
            copy_dict = copy.deepcopy(self.piece_locations)
            self.piece_locations.pop(marked_piece)
            self.piece_locations[self.selected_piece]["coords"] = (row, col)
            self.piece_locations[self.selected_piece]["has_moved"] = True
            check_status, king = self.CheckDetection(self.side_playing)

            if not self.in_check:
                if "Pawn" in self.selected_piece and row == 0:
                    while True:
                        promotion_choice = simpledialog.askstring("What piece to be promoted to", "Rook, Bishop, Knight, or Queen?").lower().strip()
                        match promotion_choice:
                            case "queen":
                                promotion_choice = "Queen"
                            case "rook":
                                promotion_choice = "Rook"
                            case "bishop":
                                promotion_choice = "Bishop"
                            case "knight":
                                promotion_choice = "Knight"
                            case _:
                                tk.messagebox.showinfo(default="ok", message="Invalid promotion piece", title="Notice")
                                continue
                        pieces_with_numbers = ["Knight", "Bishop", "Rook"]
                        self.piece_locations.pop(self.selected_piece)
                        if promotion_choice in pieces_with_numbers:
                            self.selected_piece = self.side_playing + promotion_choice + "3"
                        else:
                            self.selected_piece = self.side_playing + promotion_choice
                        self.piece_locations.update({self.selected_piece: {"coords": (row, col), "has_moved": True}})
                        break

            if check_status == "Check":  
                self.piece_locations = copy.deepcopy(copy_dict)
                tk.messagebox.showinfo(default="ok", message="You are in check", title="Check notice")
            else:
                self.ChangeSides()

        #Code that runs if cell selected is possible movement square
        elif self.canvas.itemcget(id, "fill") == "#a7a700":
            #Sets the piece's location to the location of the yellow square (moves the piece)
            if not self.in_check:
                if self.selected_piece == "whiteKing" and self.piece_locations[self.selected_piece]["has_moved"] == False:
                    if (row, col) == (7,2):
                        self.piece_locations["whiteRook1"]["coords"] = (row, col+1)
                    if (row, col) == (7,6):
                        self.piece_locations["whiteRook2"]["coords"] = (row, col-1)
                elif self.selected_piece == "blackKing" and self.piece_locations[self.selected_piece]["has_moved"] == False:
                    if (row, col) == (7,1):
                        self.piece_locations["blackRook2"]["coords"] = (row, col+1)
                    if (row, col) == (7,5):
                        self.piece_locations["blackRook1"]["coords"] = (row, col-1)

                if "Pawn" in self.selected_piece and row == 0:
                    while True:
                        promotion_choice = simpledialog.askstring("What piece to be promoted to", "Rook, Bishop, Knight, or Queen?").lower().strip()
                        match promotion_choice:
                            case "queen":
                                promotion_choice = "Queen"
                            case "rook":
                                promotion_choice = "Rook"
                            case "bishop":
                                promotion_choice = "Bishop"
                            case "knight":
                                promotion_choice = "Knight"
                            case _:
                                tk.messagebox.showinfo(default="ok", message="Invalid promotion piece", title="Notice")
                                continue
                        pieces_with_numbers = ["Knight", "Bishop", "Rook"]
                        self.piece_locations.pop(self.selected_piece)
                        if promotion_choice in pieces_with_numbers:
                            self.selected_piece = self.side_playing + promotion_choice + "3"
                        else:
                            self.selected_piece = self.side_playing + promotion_choice
                        self.piece_locations.update({self.selected_piece: {"coords": (row, col), "has_moved": True}})
                        break
            
            copy_dict = copy.deepcopy(self.piece_locations)
            self.piece_locations[self.selected_piece]["coords"] = (row, col)
            self.piece_locations[self.selected_piece]["has_moved"] = True
            check_status, king = self.CheckDetection(self.side_playing)
            if check_status == "Check":
                self.piece_locations = copy.deepcopy(copy_dict)
                tk.messagebox.showinfo(default="ok", message="You are in check", title="Check notice")

                #Code doesn't need a while True cause it isn't doing anything to the game state
                #It'll just loop right back here
            else:
                self.ChangeSides()

        #Code that runs if cell selected is not colored
        else:
            #Checks whether the square clicked on has a piece or not
            for piece, value in self.piece_locations.items():
                coords = value["coords"]
                if coords == (self.square_dict[id][1], self.square_dict[id][2]):
                    ran = True
                    if not self.canvas.itemcget(id, "fill") == "#8D0202":
                        self.canvas.itemconfig(id, fill="yellow")
                    current_piece = piece
                    self.selected_piece = piece
                    break

            #If there is a piece on the clicked square run this code, if not reset the board 
            if ran:
                current_piece, piece_color = self.StandardizePiece(current_piece)

                #Make sure that your not playing for the other side
                if piece_color == self.side_playing:
                    #main loop, dr and dc are directional tuples (ex. (-1, 1)), self.piece_movements has them all
                    for dr, dc in self.piece_movements[current_piece]:
                        piece_found = False
                        copyrow = row + dr
                        copycol = col + dc

                        #Castling check
                        if not self.in_check:
                            possible_kings = ["whiteKing", "blackKing"]
                            if self.selected_piece in possible_kings:
                                if not self.piece_locations[self.selected_piece]["has_moved"]:
                                    if self.selected_piece == "whiteKing":
                                        if not self.piece_locations["whiteRook1"]["has_moved"] and self.CheckEmptySpace("whiteRook1", self.selected_piece):
                                            castle_id.append(7 * 8 + 3)
                                            self.canvas.itemconfig(7 * 8 + 3, fill="#a7a700")
                                        if not self.piece_locations["whiteRook2"]["has_moved"] and self.CheckEmptySpace("whiteRook2", self.selected_piece):
                                            castle_id.append(7 * 8 + 7)
                                            self.canvas.itemconfig(7 * 8 + 7, fill="#a7a700")
                                    if self.selected_piece == "blackKing":
                                        if not self.piece_locations["blackRook1"]["has_moved"] and self.CheckEmptySpace("blackRook1", self.selected_piece):
                                            castle_id.append(7 * 8 + 6)
                                            self.canvas.itemconfig(7 * 8 + 6, fill="#a7a700")
                                        if not self.piece_locations["blackRook2"]["has_moved"] and self.CheckEmptySpace("blackRook2", self.selected_piece):
                                            castle_id.append(7 * 8 + 2)
                                            self.canvas.itemconfig(7 * 8 + 2, fill="#a7a700")

                        #General piece movement otherwise
                        if "Pawn" in current_piece:
                            if self.piece_locations[self.selected_piece]["has_moved"] == False:
                                range_num = 2
                            else:
                                range_num = 1
                        elif current_piece == "Knight" or current_piece == "King":
                            range_num = 1
                        else:
                            range_num = 8
                        for _ in range(range_num):
                            if copyrow < 0 or copyrow > 7 or copycol < 0 or copycol > 7:
                                break
                            test_id = (copyrow * 8 + copycol) + 1

                            #Checking if the piece is a pawn, and then if the pawn can capture something
                            if "Pawn" in current_piece:
                                if (dr, dc) == (-1,-1) or (dr, dc) == (-1,1):
                                    for piece, value in self.piece_locations.items():
                                        coords = value["coords"]
                                        
                                        if (copyrow, copycol) == coords:
                                            piece_found = True
                                            test_color = piece[0:5] 
                                            break
                                    if not piece_found:
                                        break
                                    else:
                                        highlighted_squares.append([test_id, True, test_color])
                                        break

                            for piece, value in self.piece_locations.items():
                                coords = value["coords"]

                                if (copyrow, copycol) == coords:
                                    piece_found = True
                                    test_color = piece[0:5] 
                                    break
                            if not piece_found:
                                copyrow += dr
                                copycol += dc
                                highlighted_squares.append([test_id, False, None])
                            elif piece_found and current_piece not in pawn_list:
                                highlighted_squares.append([test_id, True, test_color])
                                break
                            else:
                                break
                    for test_id in range(1,65):
                        if not test_id == id and not test_id in castle_id and not self.canvas.itemcget(test_id, "fill") == "#8D0202":
                            color = self.square_dict[test_id][0]
                            self.canvas.itemconfig(test_id, fill=color)
                        for list in highlighted_squares:
                            valid_id = list[0]
                            captured = list[1]
                            color = list[2]
                            if piece_color == color:
                                continue
                            if captured:
                                self.canvas.itemconfig(valid_id, fill="#D41313")
                            else:
                                self.canvas.itemconfig(valid_id, fill="#a7a700")
                #If you clicked on the other sides piece
                else:
                    self.ResetBoard(False)
            #if you didn't click on any piece
            else:
                self.ResetBoard(False)

    def ChangeSides(self):
        self.FlipBoard()
        self.side_playing = self.OppColor(self.side_playing)
        check_status, king = self.CheckDetection(self.side_playing)
        king_row, king_col = self.piece_locations[king]["coords"]
        if check_status == "Check":
            self.canvas.itemconfig((king_row * 8 + king_col) + 1, fill="#8D0202")
            self.in_check = True
            if not self.LegalMoveCheck():
                tk.messagebox.showinfo(default="ok", message=f"{self.side_playing} has lost the game by checkmate", title="End of game")
        else:
            self.in_check = False

    def CheckDetection(self, side_playing):
        pawn_capturing = False
        king = side_playing + "King"
        king_row, king_col = self.piece_locations[king]["coords"]
        for piece, dict in self.piece_locations.items():
            #rand is here so I can standarize piece for all uses EXCEPT pawn coverage
            rand = piece 
            piece, color = self.StandardizePiece(rand)
            if color == king[0:5]: 
                continue
            elif piece == "Knight":
                range_num = 1
            else:
                range_num = 8
            row, col = dict["coords"]
            for dr, dc in self.piece_movements[piece]:
                if "Pawn" in piece and (dc == -1 or dc == 1):
                    range_num = 1
                    pawn_capturing = True
                elif "Pawn" in piece:
                    if self.piece_locations[rand]["has_moved"] == False:
                        range_num = 2
                    else:
                        range_num = 1
                    pawn_capturing = False
                piece_found = False
                copy_row = row + dr
                copy_col = col + dc   
                for _ in range(range_num):            
                    if copy_row < 0 or copy_row > 7 or copy_col < 0 or copy_col > 7:
                        break
                    for test_piece, value in self.piece_locations.items():
                        if value["coords"] == (copy_row, copy_col):
                            if value["coords"] == (king_row, king_col):
                                if "Pawn" in piece and not pawn_capturing:
                                    continue
                                else:
                                    return "Check", king
                            piece_found = True
                            break
                    if piece_found:
                        break
                    else:
                        copy_row += dr
                        copy_col += dc         
        return "Fine", king

    def OppColor(self, color):
        if color == "white":
            return "black"
        elif color == "black":
            return "white"
        else:
            #Not A Color, stole from JS's NaN
            return "NaC"
        
    def LegalMoveCheck(self):
        flag = False
        pawn_capturing = False
        pawn_valid_capture = False
        for piece, dict in self.piece_locations.items():
            rand = piece
            piece, piece_color = self.StandardizePiece(rand)
            if piece_color == self.OppColor(self.side_playing):
                continue
            if piece == "Knight" or piece == "King":
                range_num = 1
            else:
                range_num = 8
            row, col = dict["coords"]
            for dr, dc in self.piece_movements[piece]:
                if "Pawn" in piece and (dc == -1 or dc == 1):
                    range_num = 1
                    pawn_capturing = True
                elif "Pawn" in piece:
                    if self.piece_locations[rand]["has_moved"] == True:
                        range_num = 1
                    else:
                        range_num = 2
                    pawn_capturing = False
                copy_dict = copy.deepcopy(self.piece_locations)
                copy_row = row
                copy_col = col
                for _ in range(range_num):  
                    copy_row += dr
                    copy_col += dc          
                    if copy_row < 0 or copy_row > 7 or copy_col < 0 or copy_col > 7:
                        continue
                    #x, y is piece and dict.... Im just out of terms for this stuff;
                    #or the brainpower to find more
                    for x, y in self.piece_locations.items():
                        if y["coords"] == (copy_row, copy_col) and "Pawn" in piece and not pawn_capturing:
                            flag = True
                            break
                        elif y["coords"] == (copy_row + dr, copy_col + dc) and (dc == -1 or dc == 1):
                            pawn_valid_capture = True
                    if flag:
                        break

                    if "Pawn" in piece and (dc == 1 or dc == -1) and not pawn_valid_capture:
                        continue

                    for x, y in self.piece_locations.items():
                        if y["coords"] == (copy_row, copy_col) and x[0:5] == self.side_playing:
                            flag = True
                            break
                    if flag:
                        break
                    self.piece_locations[rand]["coords"] = (copy_row, copy_col)
                    
                    check_status, king = self.CheckDetection(self.side_playing)
                    self.piece_locations = copy.deepcopy(copy_dict)
                    if check_status == "Fine":
                        return True
        return False
    
    def StandardizePiece(self, piece):
        color = piece[0:5]
        if "Pawn" in piece:
            piece = piece[0:len(piece) - 1]
        elif not "King" in piece and not "Queen" in piece:
            piece = piece[5:len(piece) - 1]
        else:
            piece = piece[5:len(piece)]
        return piece, color

    def ResetBoard(self, ignore):
        for test_id in range(1,65):
            if not self.canvas.itemcget(test_id, "fill") == "#8D0202" or ignore:
                color = self.square_dict[test_id][0]
                self.canvas.itemconfig(test_id, fill=color)

    def CheckEmptySpace(self, piece, king):
        rook_row, rook_col = self.piece_locations[piece]["coords"]
        king_row, king_col = self.piece_locations[king]["coords"]
        if rook_col > king_col:
            step = -1
            change_const = -1
        else:
            step = 1
            change_const = 1
        for i in range(rook_col + change_const, king_col, step):
            for piece, dict in self.piece_locations.items():
                if dict["coords"] == (rook_row, i):
                    return False
        return True

    def FlipBoard(self):
        for piece, value in self.piece_locations.items():
            row = value["coords"][0]
            col = value["coords"][1] 
            match row:
                case 0:
                    value["coords"] = (7, col)
                    row = 7
                case 1:
                    value["coords"] = (6, col)
                    row = 6
                case 2:
                    value["coords"] = (5, col)
                    row = 5
                case 3:
                    value["coords"] = (4, col)
                    row = 4
                case 4:
                    value["coords"] = (3, col)
                    row = 3
                case 5:
                    value["coords"] = (2, col)
                    row = 2
                case 6:
                    value["coords"] = (1, col)
                    row = 1
                case 7:
                    value["coords"] = (0, col)
                    row = 0
            match col:
                case 0:
                    value["coords"] = (row, 7)
                case 1:
                    value["coords"] = (row, 6)
                case 2:
                    value["coords"] = (row, 5)
                case 3:
                    value["coords"] = (row, 4)
                case 4:
                    value["coords"] = (row, 3)
                case 5:
                    value["coords"] = (row, 2)
                case 6:
                    value["coords"] = (row, 1)
                case 7:
                    value["coords"] = (row, 0)
        self.UpdateImages()
        self.ResetBoard(True)

chess = ChessBoard(root)
root.mainloop()
