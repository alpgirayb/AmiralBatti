



def get_ship_location():
    row=input('Please enter a ship row 1-8').upper()
    while row not in '12345678':
        print("Please enter a valid row")
        row=input('Please enter a ship row 1-8')
    column=input('Please enter a ship column A-H').upper()
    while column not in 'ABCDEFGH':
        print("Please enter a valid column")
        column=input('Please enter a ship column A-H')
    return int(row)-1,let_to_num[column]

def hit_confirm(board):
        count = 0
        for row in board:
            for column in row:
                if column == 'X':
                    count += 1
        return count
