#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <map>

using namespace std;

enum Dir { ERROR, LEFT, TOP, RIGHT, BOTTOM };

struct CellType
{
    Dir movements_[5] = { ERROR, ERROR, ERROR, ERROR, ERROR }; // if smth comes from ith side it goes to movements_[i] direction
    CellType const* turns_[3] = { this, this, this }; // turns[i] - cell type after (i+1) clockwise turns
};

void fill_cell_types(vector<CellType>& cells)
{
    cells.resize(14);
    cells[1].movements_[LEFT] = cells[1].movements_[RIGHT] = cells[1].movements_[TOP] = BOTTOM;
    cells[2].movements_[LEFT] = RIGHT; cells[2].movements_[RIGHT] = LEFT;
    cells[2].turns_[0] = &cells[3]; cells[2].turns_[2] = &cells[3];
    cells[3].movements_[TOP] = BOTTOM;
    cells[3].turns_[0] = &cells[2]; cells[3].turns_[2] = &cells[2];
    cells[4].movements_[TOP] = LEFT; cells[4].movements_[RIGHT] = BOTTOM;
    cells[4].turns_[0] = &cells[5]; cells[4].turns_[2] = &cells[5];
    cells[5].movements_[TOP] = RIGHT; cells[5].movements_[LEFT] = BOTTOM;
    cells[5].turns_[0] = &cells[4]; cells[5].turns_[2] = &cells[4];
    cells[6].movements_[LEFT] = RIGHT; cells[6].movements_[RIGHT] = LEFT;
    cells[6].turns_[0] = &cells[7]; cells[6].turns_[1] = &cells[8]; cells[6].turns_[2] = &cells[9];
    cells[7].movements_[TOP] = BOTTOM; cells[7].movements_[RIGHT] = BOTTOM;
    cells[7].turns_[0] = &cells[8]; cells[7].turns_[1] = &cells[9]; cells[7].turns_[2] = &cells[6];
    cells[8].movements_[LEFT] = BOTTOM; cells[8].movements_[RIGHT] = BOTTOM;
    cells[8].turns_[0] = &cells[9]; cells[8].turns_[1] = &cells[6]; cells[8].turns_[2] = &cells[7];
    cells[9].movements_[TOP] = BOTTOM; cells[9].movements_[LEFT] = BOTTOM;
    cells[9].turns_[0] = &cells[6]; cells[9].turns_[1] = &cells[7]; cells[9].turns_[2] = &cells[8];
    cells[10].movements_[TOP] = LEFT;
    cells[10].turns_[0] = &cells[11]; cells[10].turns_[1] = &cells[12]; cells[10].turns_[2] = &cells[13];
    cells[11].movements_[TOP] = RIGHT;
    cells[11].turns_[0] = &cells[12]; cells[11].turns_[1] = &cells[13]; cells[11].turns_[2] = &cells[10];
    cells[12].movements_[RIGHT] = BOTTOM;
    cells[12].turns_[0] = &cells[13]; cells[12].turns_[1] = &cells[10]; cells[12].turns_[2] = &cells[11];
    cells[13].movements_[LEFT] = BOTTOM;
    cells[13].turns_[0] = &cells[10]; cells[13].turns_[1] = &cells[11]; cells[13].turns_[2] = &cells[12];
}

struct Map
{
    Map(int width, int height)
    : width_(width), height_(height)
    {
        map_.resize(height, vector<CellType*>(width));
    }

    std::pair<int, int> next(int curr_x, int curr_y, Dir from)
    {
        CellType* type = map_[curr_y][curr_x];
        switch (type->movements_[from]) {
            case ERROR: throw -1;
            case TOP:   throw -1;
            case BOTTOM: return { curr_x, curr_y + 1 };
            case LEFT:  return { curr_x - 1, curr_y };
            case RIGHT: return { curr_x + 1, curr_y };
        }
    }

    static vector <CellType> cell_types;
    int width_;
    int height_;
    vector <vector <CellType*>> map_;
};

vector <CellType> Map::cell_types;

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
int main()
{
    fill_cell_types(Map::cell_types);

    int W; // number of columns.
    int H; // number of rows.
    cin >> W >> H; cin.ignore();

    Map m(W, H);

    for (int i = 0; i != H; i++) {
        for (int j = 0; j != W; ++j) {
            int type;
            cin >> type;
            m.map_[i][j] = &Map::cell_types[type];
        }
    }

    int EX; // the coordinate along the X axis of the exit (not useful for this first mission, but must be read).
    cin >> EX; cin.ignore();

    map <string, Dir> dir_conversions = {{ "TOP", TOP }, { "LEFT", LEFT }, { "RIGHT", RIGHT }};

    // game loop
    while (1) {
        int XI;
        int YI;
        string POS;
        cin >> XI >> YI >> POS; cin.ignore();

        Dir from = dir_conversions[POS];
        auto next = m.next(XI, YI, from);

        // One line containing the X Y coordinates of the room in which you believe Indy will be on the next turn.
        cout << next.first << " " << next.second << endl;
    }
}
