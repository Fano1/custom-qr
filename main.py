import numpy as np

#Constants

QRcodeVersion: int = 3
w: int = 29
h: int = 29 
error_correction_level: str = "L"
data_mode: str = "byte mode"
data_modeCode: str = "0100"

#Mappings
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

def generateQRImage():
    pass

#QR matrics operation

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
        characterCount = bin(len(self.data))

    def draw_ECE():
        pass
    
    def draw_QRcode(self):
        self.draw_finderPattern(0, 0)
        self.draw_finderPattern(0, 22)
        self.draw_finderPattern(22, 0)
        self.draw_allignmentPattern()
        self.draw_timingPattern()
        self.draw_formatString()
        self.draw_darkPizel()
    
    def exportQRcodeGrid(self):
        self.draw_QRcode()
        return self.grid
    


grid = generateEmptyGrid()
helper = QRCreateOperation(grid, data="Hello")
QRgrid = helper.exportQRcodeGrid()

for r in range(h):
    line = ""
    for c in range(w):
        if QRgrid[r, c] == 1:
            line += "\033[41m  \033[0m"  # Red (black module)
        else:
            if helper.reserved[r, c]:
                line += "\033[47m  \033[0m"  # White (reserved structural white)
            else:
                line += "\033[43m  \033[0m"  # Yellow (unassigned data space)
    print(line)



