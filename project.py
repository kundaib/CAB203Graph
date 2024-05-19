import csv
from collections import defaultdict
from itertools import combinations


def gamesOK(games): 

   opponents = defaultdict(set)
   for u, v in games:
      opponents[u].add(v)
      opponents[v].add(u)

   num_games_set = set(map(len, opponents.values()))

   if len(num_games_set) != 1:
      return False


   players = list(opponents.keys())

   def pair_condition(pair):
      p1, p2 = pair
      if p2 in opponents[p1]:
         return True
      common_opponents = opponents[p1].intersection(opponents[p2])
      return len(common_opponents) >= 2


   pairwise_conditions = map(pair_condition, combinations(players, 2))
   
   return all(pairwise_conditions)


def referees(games, refereecsvfilename):
   
   referee_conflicts = {}
   
   with open(refereecsvfilename, newline='') as csvfile:
      reader = csv.reader(csvfile)
      headers = next(reader) 
      for row in reader:
            referee = row[0].strip()
            conflicts = set(row[1:]) - {''} 
            referee_conflicts[referee] = conflicts
   

   game_to_referees = defaultdict(set)
   referee_to_games = defaultdict(set)
   
   for game in games:
      player1, player2 = game
      for referee, conflicts in referee_conflicts.items():
            if referee not in game and player1 not in conflicts and player2 not in conflicts:
               game_to_referees[game].add(referee)
               referee_to_games[referee].add(game)
   
   def bpm(game, match, visited):
      for referee in game_to_referees[game]:
            if not visited[referee]:
               visited[referee] = True
               if referee not in match or bpm(match[referee], match, visited):
                  match[referee] = game
                  return True
      return False
   

   match = {}
   for game in games:
      visited = {referee: False for referee in referee_conflicts}
      bpm(game, match, visited)
   

   if len(match) != len(games):
      return None
   
   
   game_referee_assignment = {v: k for k, v in match.items()}
   
   return game_referee_assignment

def gameGroups(assignedReferees):

   graph = {}
   for game, referee in assignedReferees.items():
      graph[game] = set()
      for other_game, other_referee in assignedReferees.items():
         if game != other_game and (referee == other_referee or set(game).intersection(other_game)):
               graph[game].add(other_game)

   game_groups = []
   remaining_games = set(graph.keys())

   while remaining_games:
      current_group = set()
      for game in remaining_games:
         if all(game2 not in current_group and not any(referee in assignedReferees[game2] for referee in assignedReferees[game]) for game2 in graph[game]):
               current_group.add(game)
      game_groups.append(current_group)
      remaining_games -= current_group

   return list(map(lambda group: set(group), game_groups))

