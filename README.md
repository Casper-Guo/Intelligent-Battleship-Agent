# Intelligent Battleship Agent

An interface for playing the board game Battleship against another player or a random forest classifier.

The agent is trained by playing on randomly generated boards. It exhibits the following characteristics:

1, It correctly recognizes that a grid is more likely to contain a target if a directly (non-diagonal) adjacent grid also contains a target. It thus has the human-like behavior of valuing grids around an already hit grid more highly.

2, By far the most influential feature is the grid's Euclidean distance to the center of the board. This is a consequence of using randomly generated boards rather than human-created boards. This is somewhat detrimental for the bot's performance as humans tend to place ships away from the center.
