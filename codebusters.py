import sys
import math
import random
from collections import defaultdict

# Send your busters out into the fog to trap ghosts and bring them home!

HEIGHT = 9000
WIDTH = 16000
X_SCALE = 1000
Y_SCALE = 1000

busters_per_player = int(input())  # the amount of busters you control
ghost_count = int(input())  # the amount of ghosts on the map
my_team_id = int(input())  # if this is 0, your base is on the top left of the map, if it is one, on the bottom right
team_pos = None
busters = {}
ghosts = {}
iteration = 0
visited_regions = set()
enemy_busters = []

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
        self.target_pos = None
        self.target_ghost_id = -1
        self.can_stun = True
        self.stun_target = -1

class Region:
    def __init__(self):
        self.num_entities = 0
        self.targeted_to_visit = False

def get_distance(entity1, entity2):
    return int(math.sqrt((entity1.x - entity2.x) ** 2 + (entity1.y - entity2.y) ** 2))

def get_region_coord(point):
    return (int(max(0, point.x - 1) / X_SCALE) * X_SCALE, int(max(0, point.y - 1) / Y_SCALE) * Y_SCALE)

def get_point_on_dist(src, dest, dist = 0):
    full_dist = get_distance(src, dest)
    if not full_dist:
        if dest.x == team_pos.x and dest.y == team_pos.y:
            return team_pos
        return get_point_on_dist(src, team_pos, dist)
    relation = dist / float(full_dist)
    res = Point()
    res.x = int(dest.x - (dest.x - src.x) * relation)
    res.y = int(dest.y - (dest.y - src.y) * relation)
    return res

def get_regions_on_path(src, dest):
    res = set()
    distance = get_distance(src, dest)
    num_parts = max(1, int(distance / 500))
    for i in range(num_parts + 1):
        point = get_point_on_dist(src, dest, int(distance / num_parts * i))
        res.add(get_region_coord(point))
    '''
    print("intervals: %i, x_inc=%i(%f), y_inc=%i(%f), from:(%i, %i), to:(%i, %i), %s" % 
            (num_parts, x_inc, (dest.x - src.x) / x_inc, y_inc, (dest.y - src.y) / y_inc,
            src.x, src.y, dest.x, dest.y, res), file=sys.stderr)
    '''
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
        print((entity_id, x, y, entity_type, state, value), file=sys.stderr)
        if entity_type == my_team_id:
            if entity_id in busters:
                buster = busters[entity_id]
                buster.x = x
                buster.y = y
                buster.carry_ghost = bool(state)
                buster.ghost_id = value
                if buster.stun_target >= 0:
                    buster.can_stun = False
                buster.stun_target = -1
            else:
                busters[entity_id] = Buster(x, y, bool(state), value)
        elif entity_type >= 0:
            enemy_busters[entity_id] = Buster(x, y, bool(state), value)
        else:
            if entity_id in ghosts:
                ghost = ghosts[entity_id]
                ghost.x = x
                ghost.y = y
                ghost.num_busters = value
                ghost.last_update = iteration
            else:
                ghosts[entity_id] = Ghost(x, y, value, iteration)

def assign_tasks():
    ghost_priorities = defaultdict(dict) # buster_id->{ghost_id->priority(0 - can bust right not, 1 - can bust after 1 hop, etc}
    for buster_id, buster in busters.items():
        if buster.carry_ghost or buster.stun_target >= 0:
            continue
        for ghost_id, ghost in ghosts.items():
            if ghost.num_busters > 0:
                continue
            dist = get_distance(buster, ghost)
            print("Dist buster %i ghost %i = %i" % (buster_id, ghost_id, dist), file=sys.stderr)
            if dist <= 900:
                ghost_priorities[buster_id][ghost_id] = 1
            elif dist > 900 and dist < 1760:
                ghost_priorities[buster_id][ghost_id] = 0
            else:
                priority = (dist - 1760) / 800 + 1 + (iteration - ghost.last_update)
                ghost_priorities[buster_id][ghost_id] = priority
    stun_priorities = defaultdict(dict)
    for buster_id, buster in busters.items():
        if buster.carry_ghost:
            continue
        for enemy_id, enemy in enemy_busters.items():
            if buster.can_stun and get_distance(buster, enemy) < 1760:
                if enemy.carry_ghost: stun_priorities[buster_id][enemy_id] = 0
                else: stun_priorities[buster_id][enemy_id] = 1
    buster_targets = dict((buster_id, None) for buster_id in busters.keys()) # buster_id -> (entity_id is_ghost)
    print(ghost_priorities, file=sys.stderr)
    print(stun_priorities, file=sys.stderr)
    for buster_id, priorities in ghost_priorities.items():
        buster = busters[buster_id]
        known_target_ghost_id = busters[buster_id].target_ghost_id
        if known_target_ghost_id not in ghosts:
            buster.target_ghost_id = -1
            continue
        if known_target_ghost_id >= 0 and \
                ghost_priorities[buster_id][known_target_ghost_id] == min(ghost_priorities[buster_id].values()):
            buster_targets[buster_id] = (known_target_ghost_id, True)

    print(ghost_priorities, file=sys.stderr)
    for buster_id, buster in busters.items():
        priorities = ghost_priorities[buster_id]
        if buster_targets[buster_id]:
            if buster_id in stun_priorities:
                buster_targets[buster_id] = (min(stun_priorities[buster_id], key=stun_priorities[buster_id].get)[0], False)
            continue
        best_ghost = -1
        best_score = 100500
        for ghost_id, score in ghost_priorities[buster_id].items():
            if ghost_id in buster_targets.values():
                continue
            if score < best_score:
                best_ghost = ghost_id
                best_score = score
        print(stun_priorities[buster_id], file=sys.stderr)
        if best_score > 0 and stun_priorities[buster_id]:
            buster_targets[buster_id] = (min(stun_priorities[buster_id].items(), key=lambda a: a[1])[0], False)
        elif best_ghost >= 0:
            buster_targets[buster_id] = (best_ghost, True)
        else:
            pass
    print(buster_targets, file=sys.stderr)
    return buster_targets

def assign_exploration_points(free_busters_ids):
    regions_info = dict(((x, y), Region()) for x in range(0, WIDTH, X_SCALE)
            for y in range(0, HEIGHT, Y_SCALE)) # (x, y) -> num entities
    move_destinations = {}
    for buster in busters.values():
        region_x, region_y = get_region_coord(buster)
        region = regions_info[(region_x, region_y)]
        region.num_entities += 1
        if buster.target_pos:
            regions_to_visit = get_regions_on_path(buster, buster.target_pos)
            for x, y in regions_to_visit:
                regions_info[(x, y)].targeted_to_visit = True
    for ghost in ghosts.values():
        region_x, region_y = get_region_coord(ghost)
        regions_info[(region_x, region_y)].num_entities += 1.0 / max(1, iteration - ghost.last_update)

    for buster_id in free_busters_ids:
        buster = busters[buster_id]
        print("buster %i (%i, %i) target_pos %s" %
                (buster_id, buster.x, buster.y,
                str((buster.target_pos.x, buster.target_pos.y)) if buster.target_pos else "(-1,-1)"),
                file=sys.stderr)
        if buster.target_pos and get_distance(buster, buster.target_pos) > 100:
            move_destinations[buster_id] = buster.target_pos
            continue
        best_score = -100500
        best_dest = None
        for (x, y), entities in regions_info.items():
            region_center = Point(x + int(X_SCALE/2), y + int(Y_SCALE/2))
            dist = get_distance(busters[buster_id], region_center)
            if dist < 100:
                continue
            '''
            if dist < 2200:
                continue
            score = int(dist / 800) - entities
            '''
            score = 0
            regions_on_path = get_regions_on_path(buster, region_center)
            for x, y in regions_on_path:
                if (x, y) in visited_regions:
                    score -= 1
                elif regions_info[(x, y)].targeted_to_visit:
                    score -= 0.5
                else:
                    score += 2
            '''
            if (x, y) in visited_regions:
                score -= 10
            '''
            if score > best_score:
                best_score = score
                best_dest = region_center
        move_destinations[buster_id] = best_dest
        for x, y in get_regions_on_path(buster, best_dest):
            regions_info[(x, y)].targeted_to_visit = True
    return move_destinations
        
    
if my_team_id == 0:
    team_pos = Point(0, 0)
else:
    team_pos = Point(WIDTH, HEIGHT)

# game loop
while True:
    enemy_busters = {}
    read_input()
    ghosts_to_remove = set()
    for ghost_id, ghost in ghosts.items():
        for buster in busters.values():
            dist = get_distance(ghost, buster)
            # print("Dist buster %i ghost %i %i last upd %i iteration %i")
            if dist < 2200 and ghost.last_update != iteration:
                ghosts_to_remove.add(ghost_id)
    for buster_id, buster in busters.items():
        if buster.carry_ghost and buster.ghost_id in ghosts: ghosts_to_remove.add(buster.ghost_id)
        visited_regions.add(get_region_coord(buster))
        print("Buster %i (%i, %i)" % (buster_id, buster.x, buster.y), file=sys.stderr)
    for ghost_id in ghosts_to_remove:
        del ghosts[ghost_id]
    moves = dict((i, "") for i in busters.keys())
    for buster in busters.values():
        if buster.carry_ghost:
            continue
        for enemy_id, enemy in enemy_busters.items():
            if buster.can_stun and get_distance(buster, enemy) < 1760:
                buster.stun_target = enemy_id
                moves[buster_id] = 'STUN ' + str(enemy_id)
    target_ghosts = assign_tasks()
    for buster_id, buster in sorted(busters.items()):
        # MOVE x y | BUST id | RELEASE | STUN buster_id
        if buster.carry_ghost:
            buster.target_ghost_id = -1
            if get_distance(team_pos, buster) < 1600:
                buster.target_pos = None
                moves[buster_id] = "RELEASE"
            else:
                buster.target_pos = team_pos
                moves[buster_id] = "MOVE " + str(team_pos.x) + " " + str(team_pos.y)
        elif target_ghosts[buster_id] and target_ghosts[buster_id][1]:
            target_ghost_id = target_ghosts[buster_id][0]
            dist_to_ghost = get_distance(buster, ghosts[target_ghost_id])
            if dist_to_ghost > 900 and dist_to_ghost < 1760:
                buster.target_pos = None
                moves[buster_id] = 'BUST ' + str(target_ghost_id)
            else:
                dest = get_point_on_dist(buster, ghosts[target_ghost_id], 900)
                buster.target_ghost_id = target_ghost_id
                buster.target_pos = dest
                moves[buster_id] = 'MOVE ' + str(dest.x) + ' ' + str(dest.y)
        elif target_ghosts[buster_id] and not target_ghosts[buster_id][1]:
            moves[buster_id] = 'STUN ' + str(target_ghosts[buster_id][0])
        else:
            pass
    target_destinations = assign_exploration_points([i for i, move in moves.items() if not move])
    for buster_id, dest in target_destinations.items():
        moves[buster_id] = "MOVE %i %i" % (dest.x, dest.y)
        busters[buster_id].target_pos = dest
    for _, move in sorted(moves.items()):
        print(move)
    iteration += 1

