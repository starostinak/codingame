#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <queue>
#include <cassert>
#include <set>

using namespace std;

int R; // number of rows.
int C; // number of columns.
int A; // number of rounds between the time the alarm countdown is activated and the time the alarm goes off.

enum Type { UNKNOWN, EMPTY, WALL };
enum Dir { UP, DOWN, LEFT, RIGHT };
struct Node
{
    int row;
    int col;
    Type type;
    
    Node* prev = nullptr;
    int cost_before = 0;
    bool ever_visited = false;
};

typedef std::vector<std::vector<Node>> MapT;

bool is_valid(int row, int col)
{
    return (col > 0 && col < C && row > 0 && row < R);
}

Node* get_neighbour(MapT& lmap, const Node& n, Dir dir) {
    switch (dir) {
        case UP:
            if (!is_valid(n.row - 1, n.col)) return nullptr;
            return &lmap[n.row - 1][n.col];
        case DOWN:
            if (!is_valid(n.row + 1, n.col)) return nullptr;
            return &lmap[n.row + 1][n.col];
        case LEFT:
            if (!is_valid(n.row, n.col - 1)) return nullptr;
            return &lmap[n.row][n.col - 1];
        case RIGHT:
            if (!is_valid(n.row, n.col + 1)) return nullptr;
            return &lmap[n.row][n.col + 1];
    }
    assert(false);
    return nullptr;
}

int get_heurestic(const Node& start, const Node& end)
{
    return abs(start.row - end.row) + abs(start.col - end.col);
}

int num_unknowns_nearby(const MapT& lmap, int row, int col)
{
    int res = 0;
    for (int i = -2; i < 3; ++i) {
        for (int j = -2; j < 3; ++j) {
            if (is_valid(row + i, col + j) && lmap[row + i][col + j].type == UNKNOWN) {
                ++res;
            }
        }
    }
    return res;
}

Node* find_target(MapT& lmap, int row, int col)
{
    std::vector <std::pair<Node*, int>> queue;
    queue.push_back({ &lmap[row][col], 0});
    int curr_dist = 1;
    int most_unknowns = 0;
    Node* best = nullptr;
    std::set <Node*> visited;
    for (int i = 0; i != queue.size(); ++i) {
        Node* curr = queue[i].first;
        int dist = queue[i].second;
        if (dist > curr_dist && best != nullptr) {
            return best;
        }
        visited.insert(curr);
        if (dist != 0) {
            curr_dist = dist;
            int unknowns = num_unknowns_nearby(lmap, curr->row, curr->col);
            if (unknowns > most_unknowns) {
                most_unknowns = unknowns;
                best = curr;
            }
        }
        for (int dir = 0; dir != 4; ++dir) {
            Node* neighbr = get_neighbour(lmap, *curr, (Dir)dir);
            if (neighbr && visited.find(neighbr) == visited.end() && 
                    lmap[neighbr->row][neighbr->col].type == EMPTY)
                queue.push_back(std::make_pair(neighbr, dist + 1));
        }
    }
    assert(false);
    return nullptr;
}

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
int main()
{

    cin >> R >> C >> A; cin.ignore();
    
    MapT lmap(R);
    for (int i = 0; i != R; ++i) {
        lmap[i].resize(C);
        for (int j = 0; j != C; ++j) {
            lmap[i][j].col = j;
            lmap[i][j].row = i;
        }
    }

    // game loop
	Node* target = nullptr;
    Node* goal = nullptr;
    Node* start = nullptr;
    while (1) {
        int KR; // row where Kirk is located.
        int KC; // column where Kirk is located.
        cin >> KR >> KC; cin.ignore();
        lmap[KR][KC].ever_visited = true;

        cerr << KR << " " << KC << std::endl;
        
        for (int i = 0; i < R; i++) {
            string ROW; // C of the characters in '#.TC?' (i.e. one line of the ASCII maze).
            cin >> ROW; cin.ignore();
            cerr << ROW << std::endl;
            for (int j = 0; j != C; ++j) {
                switch (ROW[j]) {
                    case '#':
                        lmap[i][j].type = WALL;
                        break;
                    case '.':
                        lmap[i][j].type = EMPTY;
                        break;
                    case 'T':
                        lmap[i][j].type = EMPTY;
                        lmap[i][j].ever_visited = true;
                        start = &lmap[i][j];
                        break;
                    case 'C':
                        lmap[i][j].type = EMPTY;
                        goal = &lmap[i][j];
                        break;
                }
                lmap[i][j].prev = nullptr;
                lmap[i][j].cost_before = 100500;
            }
        }
        std::cerr << std::endl;

        if (&lmap[KR][KC] == target) {
            target = nullptr;
        }

        if (!goal && !target) {
            target = find_target(lmap, KR, KC);
        }
        if (goal && !goal->ever_visited) {
            target = goal;
        }
        if (goal && goal->ever_visited) {
            target = start;
        }

        std::cerr << "Target: " << target->row << " " << target->col << std::endl;

        std::priority_queue<std::pair<int, Node*>, std::vector<std::pair<int, Node*>>,
            std::greater<std::pair<int, Node*>>> opened;
        opened.push(std::make_pair(get_heurestic(lmap[KR][KC], *target), &lmap[KR][KC]));
        opened.top().second->cost_before = 0;
        while (!opened.empty() && opened.top().second != target) {
            Node* curr = opened.top().second;
            opened.pop();
            for (int dir = 0; dir != 4; ++dir) {
                Node* neighbr = get_neighbour(lmap, *curr, (Dir)dir);
                if (!neighbr || neighbr->type == WALL) continue;
                int cost = curr->cost_before + 1;
                if (cost < neighbr->cost_before) {
                    neighbr->prev = curr;
                    neighbr->cost_before = cost;
                    int heur = get_heurestic(*neighbr, *target);
                    opened.push(std::make_pair(cost + heur, neighbr));
                }
            }
        }
        /*
        for (int i = 0; i != R; ++i) {
            for (int j = 0; j != C; ++j) {
                std::cout << 
            }
        }
        */
        assert(!opened.empty());
        Node* curr = target;
        while (curr->prev != &lmap[KR][KC]) {
            curr = curr->prev;
        }
        std::cerr << "Next: " << curr->row << " " << curr->col << std::endl;
        if (curr->row - KR == -1) {
            std::cout << "UP" << std::endl;
        }
        else if (curr->row - KR == 1) {
            std::cout << "DOWN" << std::endl;
        }
        else if (curr->col - KC == -1) {
            std::cout << "LEFT" << std::endl;
        }
        else if (curr->col - KC == 1) {
            std::cout << "RIGHT" << std::endl;
        }
    }
}


