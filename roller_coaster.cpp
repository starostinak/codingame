#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

using namespace std;

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
int main()
{
    int L; // #places
    int C; // #times
    int N; // #groups
    int head = 0;
    cin >> L >> C >> N; cin.ignore();
    std::vector <int> groups(N);
    std::cerr << L << " " << C << " " << N << std::endl;
    for (int i = 0; i < N; i++) {
        cin >> groups[i]; cin.ignore();
        std::cerr << groups[i] << " ";
    }
    std::cerr << std::endl;
    std::vector <std::pair<int, int>>  profits(N); // profit, next_head

    for (int i = 0; i != N; ++i) {
        int profit = 0;
        for (int j = 0; j != N; ++j) {
            int pos = (i + j) % N;
            profit += groups[pos];
            if (profit > L) {
                profits[i] = std::make_pair(profit - groups[pos], pos);
                break;
            }
        }
        if (profits[i].first == 0) {
            profits[i] = std::make_pair(profit, i);
            break;
        }
    }
    unsigned long int profit = 0;
    for (int t = 0; t != C; ++t) {
        profit += profits[head].first;
        head = profits[head].second;
    }

    cout << profit << endl;
    
}

