#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  client.py
#  Reference Gambo client
#  
#  Copyright 2017 Evan Carlson <pugduddly@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import sys, time, traceback, requests
from lib.terminalsize import get_terminal_size

headers = {"user-agent": "gambo-client/1.0"}

createdata = {"type": "asdf"}
joindata   = {"userName": "3rr0r"}

sess = requests.Session()

playercolors = ["\033[97m", "\033[1m\033[33m", "\033[1m\033[34m"]
playerpieces = ["_", "1", "2", "3"]

errorcolor = "\033[91m"

console = []
consolesize = 9 # Default

#sepchar = [u'═', u'║', u'╔', u'╗', u'╚', u'╝', u'╠', u'╣', u'╩', u'╦']
sepchar  = [u'─', u'│', u'┌', u'┐', u'└', u'┘', u'├', u'┤', u'┴', u'┬']

spinner = ['|', '/', '─', '\\']
spinnerstate = 0

clearstring = "\033c\033[44m\033[3;J\033[H\033[2J"

playing = False

pnbr = 0
invs = 0

def drawWindowBox(x, y, w, h):
    sys.stdout.write('\033[%d;%dH\033[1m\033[47;97m' % (y + 1, x + 1))
    sys.stdout.write(sepchar[2])
    sys.stdout.flush()
    for x in range(x + 1, x + w - 1):
        sys.stdout.write(sepchar[0])
    sys.stdout.write('\033[0;47;30m')
    sys.stdout.write(sepchar[3])
    sys.stdout.flush()
    for _y in range(y + 2, y + h + 2):
        sys.stdout.write('\033[0;47;30m\033[%d;%dH\033[1m\033[47;97m%s' % (_y, x - w + 3, sepchar[1]))
        for _x in range(x + 2, x + w + 1):
            sys.stdout.write(' ')
        sys.stdout.write('\033[0;47;30m\033[%d;%dH%s\033[0;30;40m  ' % (_y, x + 2, sepchar[1]))
        #drawSpinner()
    sys.stdout.flush()
    sys.stdout.write('\033[%d;%dH\033[1;47;97m' % (_y + 1, x - w + 3))
    sys.stdout.flush()
    sys.stdout.write(sepchar[4])
    sys.stdout.write('\033[0;47;30m')
    sys.stdout.flush()
    for _x in range(x + 1, x + w - 1):
        sys.stdout.write(sepchar[0])
    sys.stdout.write(sepchar[5])
    sys.stdout.flush()
    sys.stdout.write("\033[0;30;40m  \033[%d;%dH" % (_y + 2, x - w + 5))
    sys.stdout.flush()
    for _x in range(x + 2, x + w + 2):
        sys.stdout.write("\033[0;30;40m ")
        sys.stdout.flush()

def drawWindowLine(x, y, w):
    sys.stdout.write('\033[%d;%dH\033[1;47;97m' % (y + 1, x + 1))
    sys.stdout.write(sepchar[6])
    for x in range(x + 1, x + w - 1):
        sys.stdout.write(sepchar[0])
    sys.stdout.write('\033[0;47;30m')
    sys.stdout.write(sepchar[7])

def updateConsole():
    global console, consolesize
    tsize = get_terminal_size()
    if playing:
        #consolesize = tsize[1] - 16
        consolesize = tsize[1] / 3
    else:
        consolesize = tsize[1] - 6
    print "\033[0;2H\033[0;1;44;36mGambo client 1.0"
    drawWindowBox(0, 2, tsize[0] - 2, consolesize)
    print
    if len(console) < consolesize:
        while len(console) < consolesize:
            console.insert(0, '')
    if len(console) > consolesize:
        while len(console) > consolesize:
            console.remove(console[0])
    y = 4
    for line in console:
        if len(line) > tsize[0] - 6:
            line = line[:(tsize[0] - 7)]
            line += u'…'
        print "\033[%d;2H\033[0;47;30m %s" % (y, line)
        y += 1
    print "\033[0m\033[%d;0H" % (consolesize + 3)

def consolePrint(line):
    global console
    console += str(line).split('\n')
    updateConsole()

def drawSpinner():
    global spinnerstate
    tsize = get_terminal_size()
    spinnerstate += 1
    if spinnerstate == 4:
        spinnerstate = 0
    sys.stdout.write("\033[0m\033[0;44;30m\033[1;%dH%s\033[1;0H" % (tsize[0] - 1, spinner[spinnerstate]))
    sys.stdout.flush()

def clearSpinner():
    tsize = get_terminal_size()
    print "\033[0m\033[0;44;30m\033[1;%dH " % (tsize[0] - 1)

def post(uri, data={}, headers=headers, exitOnError=True):
    r = sess.post(uri, data=data, headers=headers)
    if r.status_code != 200:
        consolePrint(errorcolor + "%d from %s: %s" % (r.status_code, ip, r.text))
        if exitOnError:
            sys.exit(1)
    return r

def put(uri, data={}, headers=headers, exitOnError=True):
    r = sess.put(uri, data=data, headers=headers)
    if r.status_code != 200:
        consolePrint(errorcolor + "%d from %s: %s" % (r.status_code, ip, r.text))
        if exitOnError:
            sys.exit(1)
    return r

def get(uri, data={}, headers=headers, exitOnError=True):
    r = sess.get(uri, data=data, headers=headers)
    if r.status_code != 200:
        consolePrint(errorcolor + "%d from %s: %s" % (r.status_code, ip, r.text))
        if exitOnError:
            sys.exit(1)
    return r

def clear():
	sys.stdout.write(clearstring)
	sys.stdout.flush()

def drawGame(r):
    tsize = get_terminal_size()
    tsp = consolesize + 5
    print "\033[%d;0H" % (tsp)
    print "\033[%d;1H\033[0;1;44;36m player %s's turn" % (tsp + 1, r.json()["playerTurn"]["userName"])
    plrs = "players: %s%s, %s%s" % (playercolors[1], r.json()["players"][0]["userName"], playercolors[2], r.json()["players"][1]["userName"])
    plrs2 = "players: %s, %s" % (r.json()["players"][0]["userName"], r.json()["players"][1]["userName"])
    print "\033[%d;%dH%s" % (tsp + 1, tsize[0] - len(plrs2), plrs)
    inv = r.json()["players"][pnbr - 1]["inventory"]
    invt = ""
    invl = 0
    for a in inv:
        invt += "\033[0;7m%s%d " % (playercolors[pnbr], a)
        invl += 2
    wbw, wbh = invs + 4, 5
    wbx, wby = (tsize[0] / 2) - ((invs + 4) / 2) - 1, ((((tsize[1] - 1) - (tsp)) / 2) - (int(wbh / 2))) + (tsp + 1) - 3
    drawWindowBox(wbx, wby, wbw, wbh)
    drawWindowLine(wbx, wby + 2, wbw)
    print "\033[%d;%dH%s" % (wby + 2, (tsize[0] / 2) - (invl / 2), invt)
    print "\033[0m"
    board = r.json()["board"]
    y = wby + 4
    for a in board:
        x = (tsize[0] / 2) - len(board[0])
        for b in a:
            print "\033[%d;%dH\033[7m%s%s " % (y, x, playercolors[b[0]], playerpieces[b[1]])
            x += 2
        y += 1
    sys.stdout.write("\033[%d;0H\033[0;47;30m\033[2K\033[%d;2H" % (tsize[1] - 1, tsize[1] - 1))
    sys.stdout.flush()

def main():
    global playing, pnbr, invs
    if len(sys.argv) == 1:
        print "argv[1] != IP"
        print "argv[2] != username"
        return 1
    if len(sys.argv) == 2:
        print "argv[2] != username"
        return 1
    tsize = get_terminal_size()
    joindata["userName"] = sys.argv[2]
    print clearstring
    consolePrint("attempting to create game")
    drawSpinner()
    ip = sys.argv[1]
    r = post('http://%s:4000/api/games' % (ip), createdata)
    drawSpinner()
    gid = r.json()["id"]
    consolePrint("got game %s from %s" % (gid, ip))
    consolePrint("game type is %s" % (r.json()["type"]))
    consolePrint("attempting join")
    drawSpinner()
    r = put('http://%s:4000/api/games/%s/join' % (ip, gid), joindata)
    drawSpinner()
    pnbr = r.json()["players"][len(r.json()["players"]) - 1]["playerNumber"]
    consolePrint("joined game %s as player %d" % (gid, pnbr))
    drawSpinner()
    if "playerTurn" not in r.json():
        consolePrint("waiting for other player...")
        found_player = False
        while not found_player:
            time.sleep(0.25)
            #r = sess.get('http://%s:4000/api/games/%s' % (ip, gid), headers=headers)
            r = get('http://%s:4000/api/games/%s' % (ip, gid))
            found_player = r.json()["status"] == "READY_FOR_MOVE"
            drawSpinner()
        clearSpinner()
        consolePrint("player %s joined game %s as player %d" % (r.json()["players"][len(r.json()["players"]) - 1]["userName"], gid, r.json()["players"][len(r.json()["players"]) - 1]["playerNumber"]))
    invs = len(r.json()["players"][pnbr - 1]["inventory"]) * 2
    playing = True
    while playing:
        tsize = get_terminal_size()
        clear()
        updateConsole()
        drawGame(r)
        if r.json()["playerTurn"]["userName"] == joindata["userName"]:
            print "type from(piece size or x,y):to(x,y) to move:",
            move = raw_input().strip()
            if move != "":
                mv = [x.strip().split(",") for x in move.split(":")]
                mv = [[int(y) for y in x] for x in mv]
                if len(mv[0]) == 1: mv[0] = mv[0][0]
                md = {"from": mv[0], "to": mv[1]}
                #print mv, md
                consolePrint("attempting to move piece")
                r = sess.put('http://%s:4000/api/games/%s/move' % (ip, gid), data=md, headers=headers)
                if r.status_code != 200:
                    hasJSON = False
                    try:
                        hasJSON = r.json()
                    except ValueError:
                        pass
                    if hasJSON and "errors" in r.json():
                        for error in r.json()["errors"]:
                            consolePrint(errorcolor + error["message"])
                    else:
                        consolePrint(errorcolor + "%d from %s: %s" % (r.status_code, ip, r.text))
                else:
                    consolePrint("moved piece to %s" % (mv[1]))
        else:
            print "waiting for player %s to move" % (r.json()["playerTurn"]["userName"])
            try:
                waiting = True
                while waiting:
                    time.sleep(0.25)
                    r = get('http://%s:4000/api/games/%s' % (ip, gid))
                    waiting = r.json()["playerTurn"]["userName"] != joindata["userName"]
                    drawSpinner()
                clearSpinner()
            except KeyError:
                pass
        r = get('http://%s:4000/api/games/%s' % (ip, gid))
        if r.json()["status"] == "GAME_OVER":
            playing = False
    playing = True # don't mess up console :)
    consolePrint("game over")
    consolePrint("winner is %s (player %d)" % (r.json()["winner"]["userName"], r.json()["winner"]["playerNumber"]))
    consolePrint("bye")
    drawGame(r)
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print "\033[0m\033cGoodbye"
    except Exception, e:
		print "\033[0m\033c%s" % (traceback.format_exc())

