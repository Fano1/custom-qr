import numpy as np
from PIL import Image
from typing import Any, Optional

#Constants

QRcodeVersion: int = 3
w: int = 29
h: int = 29 
error_correction_level: str = "L"
data_mode: str = "byte mode"
data_modeCode: str = "0100"
repeat_bits: str = "11101100 000010001"
max_byte = 440 #55 bytes


#helper functions 
def generateEmptyGrid():
    return np.zeros((w, h), dtype=np.uint8)

def generate_format_string(ec_level_bits, mask_bits):
    data = (ec_level_bits << 3) | mask_bits
    data <<= 10

    generator = 0b10100110111

    for i in range(14, 9, -1):
        if (data >> i) & 1:
            data ^= generator << (i - 10)

    remainder = data & 0b1111111111

    format_bits = ((ec_level_bits << 3) | mask_bits) << 10 | remainder
    format_bits ^= 0b101010000010010

    return format_bits  # 15-bit integer

def generateQRImage(QRgrid, helper):
    # Colors
    BLACK = [0, 0, 0]         # Black for modules
    WHITE = [255, 255, 255]   # White for reserved/structural areas
    YELLOW = [255, 255, 0]    # Yellow for unused spaces

    # Create RGB array
    img_array_rgb = np.zeros((h, w, 3), dtype=np.uint8)

    for r in range(h):
        for c in range(w):
            if QRgrid[r, c] == 1:
                img_array_rgb[r, c] = BLACK
            elif helper.reserved[r, c]:
                img_array_rgb[r, c] = WHITE
            else:
                img_array_rgb[r, c] = YELLOW

    # Scale up for visibility
    scale = 10
    img_array_rgb = np.kron(img_array_rgb, np.ones((scale, scale, 1), dtype=np.uint8))
    img = Image.fromarray(img_array_rgb, mode='RGB')
    img.show()


#QR matrics 
def generateEightBitBIN(data: Optional[Any] , mode: str):
    if mode.lower() == "bm":
        return "0100"
    
    if mode.lower() == "cc":
        con = np.binary_repr(len(data))
        return "0"*len(con)
    
    if mode.lower() == "rb":
        n = len()
        return repeat_bits*()[n:]


class binOperation: 
    def __init__(self, data: Optional[Any], mode: str):
        self.data = data
        self.mode = mode

    def get_modeCode(self): 
        if self.mode == "numberic" or self.mode == "nm":
            return "0001"
        
        if self.mode == "alphanumeric" or self.mode == "am":
            return "0010"
        
        if self.mode == "byte" or self.mode == "bm":
            return "0100"
        
    def get_characterCount(self):
        bin_count = np.binary_repr(len(self.data))
        fullEightBitCount = (8 - len(bin_count)) * "0" + bin_count
        return fullEightBitCount
    
    def get_dataToBin(self):
        #tell ayush shrestha to make this bit
        bin_data = convertToBin(self.data, self.mode)
        return bin_data
    
    def exportBinCode(self):
        fullBinCode =  self.get_modeCode() + self.get_characterCount() + self.get_dataToBin() + self.get_fillRest()
        return fullBinCode
    


class QRCreateOperation:
    def __init__(self, grid, data: str):
        self.grid = grid
        self.reserved = np.zeros_like(grid, dtype=bool)
        self.data = data

    def draw_finderPattern(self, start_row, start_col) -> None:
        # Draw 7x7 finder
        for r in range(7):
            for c in range(7):
                row = start_row + r
                col = start_col + c

                if r in [0, 6] or c in [0, 6]:
                    self.grid[row, col] = 1
                elif 2 <= r <= 4 and 2 <= c <= 4:
                    self.grid[row, col] = 1
                else:
                    self.grid[row, col] = 0

                self.reserved[row, col] = True

        # Draw 1-module white separator around it
        for r in range(-1, 8):
            for c in [-1, 7]:
                row = start_row + r
                col = start_col + c
                if 0 <= row < w and 0 <= col < h:
                    if not self.reserved[row, col]:
                        self.grid[row, col] = 0
                        self.reserved[row, col] = True

        for c in range(-1, 8):
            for r in [-1, 7]:
                row = start_row + r
                col = start_col + c
                if 0 <= row < w and 0 <= col < h:
                    if not self.reserved[row, col]:
                        self.grid[row, col] = 0
                        self.reserved[row, col] = True


    def draw_allignmentPattern(self) -> None:
        center = 22

        for r in range(-2, 3):
            for c in range(-2, 3):
                row = center + r
                col = center + c

                if abs(r) == 2 or abs(c) == 2:
                    self.grid[row, col] = 1
                elif r == 0 and c == 0:
                    self.grid[row, col] = 1
                else:
                    self.grid[row, col] = 0

                self.reserved[row, col] = True


    def draw_timingPattern(self):
        size = len(self.grid)

        for i in range(8, size - 8):
            self.grid[6, i] = (i + 1) % 2
            self.reserved[6, i] = True

            self.grid[i, 6] = (i + 1) % 2
            self.reserved[i, 6] = True

    def draw_darkPizel(self) -> None:
        row = 4 * QRcodeVersion + 9
        col = 8
        self.grid[row, col] = 1
        self.reserved[row, col] = True

    def draw_formatString(self):
        format_bits = generate_format_string(0b01, 0b000)  # L + mask 0
        bits = [(format_bits >> i) & 1 for i in range(14, -1, -1)]
        tl = 8
        tr = 21
        dec = 0

        for i in range(tl + 1):
            self.grid[8, i] = bits[i]
            self.grid[i, 8] = bits[14-i]
            self.reserved[8, i] = True
            self.reserved[i, 8] = True

        for i in range(tr, tr+8):
            self.grid[8, i] = bits[(7 + dec)]
            self.grid[i, 8] = bits[(7 - dec)]
            self.reserved[8, i] = True
            self.reserved[i, 8] = True

            dec += 1

    def draw_data(self):        
        bincodeHelper = binOperation(self.data, "bm")
        binCode = bincodeHelper.exportBinCode()
        print(binCode)

    def draw_ECC():
        pass
    
    def draw_QRcode(self):
        self.draw_finderPattern(0, 0)
        self.draw_finderPattern(0, 22)
        self.draw_finderPattern(22, 0)
        self.draw_allignmentPattern()
        self.draw_timingPattern()
        self.draw_formatString()
        self.draw_darkPizel()
        self.draw_data()
        # self.draw_ECC()
    
    def exportQRcodeGrid(self):
        self.draw_QRcode()
        return self.grid
    

if __name__ == "__main__":
    grid = generateEmptyGrid()
    helper = QRCreateOperation(grid, data="Hello")
    QRgrid = helper.exportQRcodeGrid()
    generateQRImage(QRgrid, helper)


