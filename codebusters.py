import sys
import math
import random
from collections import defaultdict

# Send your busters out into the fog to trap ghosts and bring them home!

HEIGHT = 9000
WIDTH = 16000
X_SCALE = 1600
Y_SCALE = 1500

busters_per_player = int(input())  # the amount of busters you control
ghost_count = int(input())  # the amount of ghosts on the map
my_team_id = int(input())  # if this is 0, your base is on the top left of the map, if it is one, on the bottom right
team_pos = None
busters = {}
ghosts = {}
iteration = 0
visited_quadrants = set()

class Point:
    def __init__(self, x=-1, y=-1):
        self.x = x
        self.y = y

class Ghost:
    def __init__(self, x, y, num_busters = 0, last_update = 0):
        self.x = x
        self.y = y
        self.num_busters = num_busters
        self.last_update = last_update

class Buster:
    def __init__(self, x, y, carry_ghost = False, ghost_id = -1):
        self.x = x
        self.y = y
        self.carry_ghost = carry_ghost
        self.ghost_id = ghost_id
        self.previous_target_pos = None
        self.target_ghost_id = -1

def get_distance(entity1, entity2):
    return int(math.sqrt((entity1.x - entity2.x) ** 2 + (entity1.y - entity2.y) ** 2))

def get_quadrant_coord(point):
    return (int(max(0, point.x - 1) / X_SCALE) * X_SCALE, int(max(0, point.y - 1) / Y_SCALE) * Y_SCALE)

def get_point_on_dist(src, dest, dist = 0):
    full_dist = get_distance(src, dest)
    if not full_dist:
        return get_point_on_dist(scr, team_pos, dist)
    relation = dist / float(full_dist)
    res = Point()
    res.x = int(dest.x - (dest.x - src.x) * relation)
    res.y = int(dest.y - (dest.y - src.y) * relation)
    return res

def get_quadrants_on_path(src, dest):
    res = set()
    x_inc = int((dest.x - scr.x) / WIDTH * X_SCALE / 2)
    y_inc = int((dest.y - scr.y) / HEIGHT * Y_SCALE / 2)
    num_parts = int((dest.x - src.x) / x_inc)
    for i in range(num_parts):
        res.add(get_quadrant_coord(Point(src.x + x_inc * i, src.y + y_inc * i)))
    return res

def read_input():
    entities = int(input())  # the number of busters and ghosts visible to you
    for i in range(entities):
        # entity_id: buster id or ghost id
        # y: position of this buster / ghost
        # entity_type: the team id if it is a buster, -1 if it is a ghost.
        # state: For busters: 0=idle, 1=carrying a ghost.
        # value: For busters: Ghost id being carried. For ghosts: number of busters attempting to trap this ghost.
        entity_id, x, y, entity_type, state, value = [int(j) for j in input().split()]
        if entity_type == my_team_id:
            if entity_id in busters:
                buster = busters[entity_id]
                buster.x = x
                buster.y = y
                buster.carry_ghost = bool(state)
                buster.ghost_id = value
            else:
                busters[entity_id] = Buster(x, y, bool(state), value)
        if entity_type < 0:
            if entity_id in ghosts:
                ghost = ghosts[entity_id]
                ghost.x = x
                ghost.y = y
                ghost.num_busters = value
                ghost.last_update = iteration
            else:
                ghosts[entity_id] = Ghost(x, y, value, iteration)

def assign_ghosts():
    ghost_priorities = defaultdict(dict) # buster_id->{ghost_id->priority(0 - can bust right not, 1 - can bust after 1 hop, etc}
    for buster_id, buster in busters.items():
        if buster.carry_ghost:
            continue
        for ghost_id, ghost in ghosts.items():
            if ghost.num_busters > 0:
                continue
            dist = get_distance(buster, ghost)
            if dist < 900:
                ghost_priorities[buster_id][ghost_id] = 1
            elif dist >= 900 and dist <= 1760:
                ghost_priorities[buster_id][ghost_id] = 0
            else:
                priority = (dist - 1760) / 800 + 1 + (iteration - ghost.last_update)
                ghost_priorities[buster_id][ghost_id] = priority
    buster_targets = dict((buster_id, -1) for buster_id in busters.keys())
    for buster_id, priorities in ghost_priorities.items():
        known_target_ghost_id = busters[buster_id].target_ghost_id
        if known_target_ghost_id not in ghosts:
            buster.target_ghost_id = -1
            continue
        if known_target_ghost_id >= 0 and \
                ghost_priorities[buster_id][known_target_ghost_id] == min(ghost_priorities[buster_id].values()):
            buster_targets[buster_id] = known_target_ghost_id

    for buster_id, priorities in ghost_priorities.items():
        if buster_targets[buster_id] >= 0:
            continue
        best_ghost = -1
        best_score = 100500
        for ghost_id, score in ghost_priorities[buster_id].items():
            if ghost_id in buster_targets:
                continue
            if score < best_score:
                best_ghost = ghost_id
                best_score = score
        buster_targets[buster_id] = best_ghost
    return buster_targets

def assign_exploration_points(free_busters_ids):
    entities_in_range = dict(((x, y), 0) for x in range(0, WIDTH, X_SCALE)
            for y in range(0, HEIGHT, Y_SCALE)) # (x, y) -> num entities
    move_destinations = {}
    for buster in busters.values():
        entities_in_range[(int(buster.x / X_SCALE) * X_SCALE, int(max(0, buster.y - 1) / Y_SCALE) * Y_SCALE)] += 1
    for ghost in ghosts.values():
        entities_in_range[(int(ghost.x / X_SCALE) * X_SCALE, int(max(0, ghost.y - 1) / Y_SCALE) * Y_SCALE)] += 1.0 / max(1, iteration - ghost.last_update)
    for buster_id in free_busters_ids:
        buster = busters[buster_id]
        if buster.previous_target_pos and get_distance(buster, buster.previous_target_pos) > 800:
            move_destinations[buster_id] = buster.previous_target_pos
            continue
        best_score = -100500
        best_dest = None
        for (x, y), entities in entities_in_range.items():
            region_center = Point(x + int(X_SCALE/2), y + int(Y_SCALE/2))
            dist = get_distance(busters[buster_id], region_center)
            if dist < 2200:
                continue
            score = int(dist / 800) - entities
            if (x, y) in visited_quadrants:
                score -= 10
            if score > best_score:
                best_score = score
                best_dest = region_center
        move_destinations[buster_id] = best_dest
    return move_destinations
        
    
if my_team_id == 0:
    team_pos = Point(0, 0)
else:
    team_pos = Point(WIDTH, HEIGHT)

# game loop
while True:
    read_input()
    ghosts_to_remove = set()
    for ghost_id, ghost in ghosts.items():
        for buster in busters.values():
            dist = get_distance(ghost, buster)
            if dist < 2200 and ghost.last_update != iteration:
                ghosts_to_remove.add(ghost_id)
    for buster in busters.values():
        if buster.carry_ghost and buster.ghost_id in ghosts: ghosts_to_remove.add(buster.ghost_id)
        '''
        if len(visited_quadrants) == 50:
            del visited_quadrants[0]
        '''
        visited_quadrants.add(get_quadrant_coord(buster))
    for ghost_id in ghosts_to_remove:
        del ghosts[ghost_id]
    target_ghosts = assign_ghosts()
    moves = dict((i, "") for i in busters.keys())
    for buster_id, buster in sorted(busters.items()):
        # MOVE x y | BUST id | RELEASE | STUN buster_id
        if buster.carry_ghost:
            buster.target_ghost_id = -1
            if get_distance(team_pos, buster) < 1600:
                moves[buster_id] = "RELEASE"
            else:
                moves[buster_id] = "MOVE " + str(team_pos.x) + " " + str(team_pos.y)
        elif target_ghosts[buster_id] >= 0:
            buster.previous_target_pos = None
            target_ghost_id = target_ghosts[buster_id]
            dist_to_ghost = get_distance(buster, ghosts[target_ghost_id])
            if dist_to_ghost >= 900 and dist_to_ghost <= 1760:
                moves[buster_id] = 'BUST ' + str(target_ghost_id)
            else:
                dest = get_point_on_dist(buster, ghosts[target_ghost_id], 900)
                buster.target_ghost_id = target_ghost_id
                moves[buster_id] = 'MOVE ' + str(dest.x) + ' ' + str(dest.y)
        else:
            pass
    target_destinations = assign_exploration_points([i for i, move in moves.items() if not move])
    for buster_id, dest in target_destinations.items():
        moves[buster_id] = "MOVE %i %i" % (dest.x, dest.y)
        busters[buster_id].previous_target_pos = dest
    for _, move in sorted(moves.items()):
        print(move)

