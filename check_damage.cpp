#include <iostream>
#include <cmath>
#include <vector>
using namespace std;
/* NOT ACTUALLY USED */
struct Rect
{
    int x;
    int y;
    int width;
    int height;
};
struct Tuple
{
  double x;
  double y;
};
struct Player
{
  Tuple pos;
  int health;
};

vector<Player> check_damage(vector<vector<double> > bullets, vector<Player> players) {
  vector<Player> damaged = players;
  for (auto const& b: bullets) {
    for (int p = 0; p < players.size(); p++) {
      double lx = b[0];
      double ly = b[1];
      double angle = b[2] * 3.1415926535 / 180;
      for (int i = 0; i < 20; i++) {
        double ix = lx + i * cos(angle);
        double iy = ly + i * sin(angle);
        if (hypot(ix+lx, iy+ly) < 20) {
          damaged[p].health -= 10;
          cout << "Damage Taken" << endl;
        }
      }
    }
  }
  return damaged; 
}


int main() {
  vector<vector<double> > shotgun{
    {644, 689, 45},
    {7, 7, 78}
  };
  vector<Player> gamers{
    {10, 10, 100},
    {8, 8, 100},
    {5, 5, 100},
  };
  check_damage(shotgun, gamers);
}
