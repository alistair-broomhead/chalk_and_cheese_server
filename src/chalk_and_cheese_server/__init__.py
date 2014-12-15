"""
Chalk and Cheese is an online multiplayer game inspired by Skull

Players are mice who each have a stash of cheese and a piece of chalk. Players
take it in turns to place in their pile either a chalk or a cheese - from the
last player on the second placement round, a mouse can choose to start bidding
for how much cheese they think they can collect in a raid. Players can then
choose to bid more if they think they can collect more.

The winning bidder then chooses one pile at a time to draw from, until they have
made their quota, making the raid successful. If they bite into a chalk, the
raid is unsuccessful, and they must forfeit a token from their stash at random.

The first mouse to make two successful raids is crowned the winner.

------

This is the  back-end for the game, and is a rest service.
"""
from server import run, add_endpoints

if __name__ == "__main__":
    run()