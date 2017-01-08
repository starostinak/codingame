#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <unordered_map>
#include <memory>

using namespace std;

vector<string> alphabet = {".-", "-...", "-.-.", "-..",
        ".", "..-.", "--.", "....",
        "..", ".---", "-.-", ".-..",
        "--", "-.", "---", ".--.",
        "--.-", ".-.", "...", "-",
        "..-", "...-", ".--", "-..-",
        "-.--", "--.."};

struct Node
{
    vector<Node*> next;
    int num_words = 0;
    
    Node(): next(vector<Node*>(2, nullptr)){ }

    Node* add_symbol(bool sym) {
        if (!next[sym]) {
            next[sym] = new Node();
        }
        return next[sym];
    }

    Node* get_node(bool sym) {
        return next[sym];
    }
};

void add_word(Node* root, string word)
{
    Node* curr = root;
    for (auto word_it = word.rbegin(); word_it != word.rend(); ++word_it) {
        string code = alphabet[*word_it - 'A'];
        for (auto code_it = code.rbegin(); code_it != code.rend(); ++code_it) {
            curr = curr->add_symbol(*code_it == '.');
        }
    }
    curr->num_words++;
}

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
int main()
{
    string L;
    cin >> L; cin.ignore();
    int N;
    cin >> N; cin.ignore();
    Node dict_root;
    for (int i = 0; i < N; i++) {
        string W;
        cin >> W; cin.ignore();
        add_word(&dict_root, W);
    }
    
    vector<long> dynamics(L.size(), 0);
    
    for (int i = 0; i != L.size(); ++i) {
        Node* curr = &dict_root;
        for (int j = i; j >= 0; --j) {
            Node* new_curr = curr->get_node(L[j] == '.');
            curr = new_curr;
            if (!curr) break;
            if (j == 0) {
                dynamics[i] += curr->num_words;
            } else {
                dynamics[i] += dynamics[j-1] * curr->num_words;
            }
        } 
    }

    // Write an action using cout. DON'T FORGET THE "<< endl"
    // To debug: cerr << "Debug messages..." << endl;

    cout << dynamics[L.size()-1] << endl;
}
