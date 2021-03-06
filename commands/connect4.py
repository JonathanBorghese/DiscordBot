
#⚪🔴🔵🟡
#add custom board size

import discord

connect_data = []
connect_first = False

def getStringArray(arr, w, h):
    empty = "⚪"
    red = "🔴"
    blue = "🔵"
    win = "🟡"

    winning = False

    board = ""
    for y in range(h):
        for x in range(w):
            if arr[x][y] == 1:
                board += red
            elif arr[x][y] == 2:
                board += blue
            elif arr[x][y] == -1:
                board += win
                winning = True
            else:
                board += empty
        board += "\n"

    if not winning:
        board += ":one::two::three::four::five::six::seven:"

    return board

def checkWon(arr, w, h, id, x, y):
    def check_valid(xx, yy):
        return xx >= 0 and yy >= 0 and xx < w and yy < h

    def check_dir(x_spd, y_spd):
        count = 0
        new_x = x + x_spd
        new_y = y + y_spd
        while check_valid(new_x, new_y) and arr[new_x][new_y] == id:
            count += 1
            new_x += x_spd
            new_y += y_spd
        return count

    # return the left/up most coordinate and direction if won and None otherwise
    # 7 ^ 9
    # < 5 >
    # 1 v 3

    if check_dir(1, 0) + check_dir(-1, 0) >= 3:
        return [x - check_dir(-1, 0), y, 6] #left

    if check_dir(0, 1) + check_dir(0, -1) >= 3:
        return [x, y - check_dir(0, -1), 2] #top

    if check_dir(1, -1) + check_dir(-1, 1) >= 3:
        l = check_dir(-1, 1)
        return [x - l, y + l, 9]    #bottom left

    if check_dir(1, 1) + check_dir(-1, -1) >= 3:
        l = check_dir(-1, -1)
        return [x - l, y - l, 3]   #top left
    return None

async def on_message_delete(message):
    global connect_data
    for d in connect_data:
        if message.id == d[0]:
            connect_data.remove(d)

async def on_reaction_remove(reaction, user):
    await on_reaction_add(reaction, user)

async def on_reaction_add(reaction, user):
    global connect_data

    for d in connect_data:
        #check if the correct person reacted
        if user.id == d[1][d[2]]:
            #check that the reaction is for the correct board
            if d[0] == reaction.message.id:

                posx = ord(reaction.emoji[0]) - 49
                posy = None

                boardChanged = False

                #find first y thats not 0
                for y in range(d[5] - 1, -1, -1):
                    if d[3][posx][y] == 0:
                        d[3][posx][y] = d[2] + 1
                        posy = y
                        boardChanged = True
                        break

                #change whose turn it is
                if boardChanged:
                    playerNum = d[2]
                    # update players turn
                    d[2] += 1
                    if d[2] >= len(d[1]):
                        d[2] = 0

                    #print new board
                    embed1 = discord.Embed(
                        title = "Connect Four",
                        color = 0xff9933,
                        description = "<@" + str(d[1][0]) + "> vs <@" + str(d[1][1]) + ">\n\n" + getStringArray(d[3], d[4], d[5])  + "\n\n **Current Turn:** " + d[6][d[2]]
                    )

                    #check winning
                    status = checkWon(d[3], d[4], d[5], playerNum + 1, posx, posy)
                    if status != None:

                        #set new array values
                        xx = status[0]
                        yy = status[1]
                        wid = d[3][xx][yy]
                        dir = status[2]

                        if dir == 2:
                            while yy < d[5] and d[3][xx][yy] == wid:
                                d[3][xx][yy] = -1
                                yy += 1
                        elif dir == 6:
                            while xx < d[4] and d[3][xx][yy] == wid:
                                d[3][xx][yy] = -1
                                xx += 1
                        elif dir == 3:
                            while xx < d[4] and yy < d[5] and d[3][xx][yy] == wid:
                                d[3][xx][yy] = -1
                                xx += 1
                                yy += 1
                        elif dir == 9:
                            while xx < d[4] and yy >= 0 and d[3][xx][yy] == wid:
                                d[3][xx][yy] = -1
                                xx += 1
                                yy -= 1
                        else:
                            print("Connect4.checkWon(): invalid direction output")


                        des = getStringArray(d[3], d[4], d[5])

                        embed2 = discord.Embed(
                            title = d[6][playerNum] + " won!",
                            color = 0xff9933,
                            description = des + "\n\nEz Clap."
                        )
                        connect_data.remove(d)
                        await reaction.message.channel.send(embed=embed2)

                    await reaction.message.edit(embed=embed1)

                    if status != None:
                        return

async def connect4(message, client):
    global connect_first
    if not connect_first:
        connect_first = True
        client.event(on_reaction_add)
        client.event(on_reaction_remove)
        client.event(on_message_delete)

    #width <= 10
    width = 7
    #height <= 12
    height = 6

    arr = [[0 for y in range(height)] for x in range(width)]

    if len(message.mentions) == 0:
        return

    player2 = message.mentions[0]

    embed = discord.Embed(
        title = "Connect Four",
        color = 0xff9933,
        description = message.author.mention + " vs " + player2.mention + "\n\n" + getStringArray(arr, width, height) + "\n\n **Current Turn:** " + message.author.display_name
    )

    players = [message.author.id, player2.id]
    names = [message.author.display_name, player2.display_name]

    msg = await message.channel.send(embed=embed)

    connect_data.append([msg.id, players, 0, arr, width, height, names])

    await msg.add_reaction("1️⃣")
    await msg.add_reaction("2️⃣")
    await msg.add_reaction("3️⃣")
    await msg.add_reaction("4️⃣")
    await msg.add_reaction("5️⃣")
    await msg.add_reaction("6️⃣")
    await msg.add_reaction("7️⃣")

