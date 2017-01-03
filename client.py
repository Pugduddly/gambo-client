#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  client.py
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

import sys, time, requests

headers = {"user-agent": "gambo-client/1.0"}

createdata = {"type": "asdf"}
joindata   = {"userName": "3rr0r"}

sess = requests.Session()

playercolors = ["\033[97m", "\033[1m\033[33m", "\033[1m\033[34m"]
playerpieces = ["_", "1", "2", "3"]

errorcolor = "\033[91m"

console = []
consolesize = 7

def updateConsole():
    global console
    print "\033[0;0H"
    print "Gambo client 1.0"
    print "----------------"
    print
    if len(console) > consolesize:
        while len(console) > consolesize:
            console.remove(console[0])
    y = 4
    for line in console:
        print "\033[0m\033[%d;0H%s" % (y, line)
        y += 1
    print "\033[0m\033[11;0H"

def consolePrint(line):
    global console
    console += [line]
    updateConsole()

def main():
    if len(sys.argv) == 1:
        print "argv[1] != IP"
        print "argv[2] != username"
        return 1
    if len(sys.argv) == 2:
        print "argv[2] != username"
        return 1
    joindata["userName"] = sys.argv[2]
    print "\033c"
    consolePrint("attempting to create game")
    ip = sys.argv[1]
    r = sess.post('http://%s:4000/api/games' % (ip), data=createdata, headers=headers)
    if r.status_code != 200:
        consolePrint(errorcolor + "%d from %s: %s" % (r.status_code, ip, r.text))
        return 1
    gid = r.json()["id"]
    consolePrint("got game %s from %s" % (gid, ip))
    consolePrint("game type is %s" % (r.json()["type"]))
    consolePrint("attempting join")
    r = sess.put('http://%s:4000/api/games/%s/join' % (ip, gid), data=joindata, headers=headers)
    if r.status_code != 200:
        consolePrint(errorcolor + "%d from %s: %s" % (r.status_code, ip, r.text))
        return 1
    pnbr = r.json()["players"][len(r.json()["players"]) - 1]["playerNumber"]
    consolePrint("joined game %s as player %d" % (gid, pnbr))
    if "playerTurn" not in r.json():
        consolePrint("waiting for other player...")
        found_player = False
        while not found_player:
            time.sleep(0.25)
            r = sess.get('http://%s:4000/api/games/%s' % (ip, gid), headers=headers)
            found_player = r.json()["status"] == "READY_FOR_MOVE"
        consolePrint("player %s joined game %s as player %d" % (r.json()["players"][len(r.json()["players"]) - 1]["userName"], gid, r.json()["players"][len(r.json()["players"]) - 1]["playerNumber"]))
    playing = True
    while playing:
        print "\033c"
        updateConsole()
        print "\033[11;0H"
        print "----------------"
        print "players: %s, %s" % (r.json()["players"][0]["userName"], r.json()["players"][1]["userName"])
        print "player %s's turn" % (r.json()["playerTurn"]["userName"])
        print "inventory:",
        inv = r.json()["players"][pnbr - 1]["inventory"]
        for a in inv:
            print "\033[7m%s%d" % (playercolors[pnbr], a),
        print "\033[0m"
        print "board:"
        board = r.json()["board"]
        for a in board:
            for b in a:
                print "\033[7m%s%s" % (playercolors[b[0]], playerpieces[b[1]]), 
            print "\033[0m"
        print
        if r.json()["playerTurn"]["userName"] == joindata["userName"]:
            print "type from(piece size or x,y):to(x,y) to move"
            print "or nothing to update board:",
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
                        #consolePrint("invalid move")
                        for error in r.json()["errors"]:
                            consolePrint(errorcolor + error["message"])
                    else:
                        consolePrint(errorcolor + "%d from %s: %s" % (r.status_code, ip, r.text))
                        #return 1
                else:
                    consolePrint("moved piece to %s" % (mv[1]))
        else:
            print "waiting for player %s to move" % (r.json()["playerTurn"]["userName"])
            waiting = True
            while waiting:
                time.sleep(0.25)
                r = sess.get('http://%s:4000/api/games/%s' % (ip, gid), headers=headers)
                waiting = r.json()["playerTurn"]["userName"] != joindata["userName"]
        r = sess.get('http://%s:4000/api/games/%s' % (ip, gid), data=joindata, headers=headers)
        if r.status_code != 200:
            consolePrint(errorcolor + "%d from %s: %s" % (r.status_code, ip, r.text))
            return 1
        if r.json()["status"] == "GAME_OVER":
            playing = False
    print "\033c"
    consolePrint("game over")
    consolePrint("winner is %s (player %d)" % (r.json()["winner"]["userName"], r.json()["winner"]["playerNumber"]))
    consolePrint("bye")
    return 0

if __name__ == '__main__':
    sys.exit(main())

