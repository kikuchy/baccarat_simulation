# -*- coding: utf-8 -*-
import random
import functools
import copy

# Score value map.
# Score of A is `VALUE_MAP[1]`, 2 is `VALUE_MAP[2]`.
VALUE_MAP = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0, 0, 0]

# Generate a suffled shoe.
# It makes 8-deck shoe.
def make_shoe():
  shoe = [i + 1 for i in range(13) for j in range(4) for k in range(8)]
  random.shuffle(shoe)
  return shoe

# Compute the score of a hand.
def score(hand):
  h = map(lambda v: VALUE_MAP[v], hand)
  sum = functools.reduce(lambda x, y: x + y, h)
  return sum % 10

# Consume a given shoe and return a card.
def consume(shoe):
  if len(shoe) ==  0:
    return VALUE_MAP[random.randint(1, 13)]
  else:
    return shoe.pop(0)

# Contine a single round of Baccarat game with given shoe.
# A given shoe will be modified.
# It returns `0` if Banker side wins, `1` if Player side wins or `2` if it is Tie.
def play(shoe):
  player_hand = [consume(shoe)]
  banker_hand = [consume(shoe)]
  player_hand.append(consume(shoe))
  banker_hand.append(consume(shoe))

  player_score = score(player_hand)
  banker_score = score(banker_hand)

  # ナチュラル
  if player_score in [8, 9] or banker_score in [8, 9]:
    if player_score == banker_score:
      return 2
    else:
      return 1 if player_score > banker_score else 0
  
  # プレイヤーが5以下の場合
  if player_score in range(0, 5):
    player_hand.append(consume(shoe))
    player_third = score([player_hand[2]])

    # バンカーが追加カードを引く権利を得たケース
    if (banker_score == 6 and player_third in [6, 7]) or \
        (banker_score == 5 and player_third in range(4, 7)) or \
        (banker_score == 4 and player_third in range(2, 7)) or \
        (banker_score == 3 and player_third != 8) or \
        (banker_score in [0, 1, 2]):
      banker_hand.append(consume(shoe))

  elif player_score in [6,7]:
    banker_hand.append(consume(shoe))

  player_score= score(player_hand)
  banker_score = score(banker_hand)
  if player_score == banker_score:
    return 2
  else:
    return 1 if player_score > banker_score else 0


# Payout rate.
# Next to "Banker wins", "Player wins", "Tie"
PAYOUT_RATE = [1.95, 2, 8]

# Payout according to the play result.
def settle(possition, ammount, result):
  if result == possition:
    return ammount * PAYOUT_RATE[result]
  elif result == 2:
    return ammount
  return 0

# Generate games with given epoch.
def generate_games(epoch):
  all_results = []
  for e in range(epoch):
    shoe = make_shoe()
    results = [(None, copy.copy(shoe))]
    while len(shoe)!= 0:
      r = play(shoe)
      results.append((r, copy.copy(shoe)))
    all_results.append(results)
  return all_results

# Simulate the given strategy with given game.
# The strategy has to have three methods.
# * bet(round, p_win, b_win, tie, shoe)
# * feedback(betted_position, won_position)
# * get_stat()
def simulate(games, strategy):
  amount = 0
  amount_history = [amount]
  bet_count = 0
  win_count = 0
  lose_count = 0
  t_payout_count = 0
  stat_history = []
  for epoch, results in enumerate(games):
    p_win = 0
    b_win = 0
    tie = 0
    shoe = results[0][1]
    for round in range(1, len(results) - 1):
      betting = strategy.bet(round - 1, p_win, b_win, tie, shoe)
      if betting != None:
        amount -= betting[1]
        #print(f'{betting[1]}円賭けるよ！！　現時点で残金は {amount} 円だよ！')
        bet_count += 1

      result = results[round]
      r = result[0]
      shoe = result[1]

      if r == None:
        continue
      
      if r == 0:
        b_win += 1
      elif r == 1:
        p_win += 1
      else:
        tie += 1
      
      if betting != None:
        if r == betting[0]:
          win_count += 1
          #print("勝ったよ！")
        elif r == 2:
          t_payout_count += 1
          #print("外したけど払い戻しがあるよ")
        else:
          lose_count += 1
          #print("外したよ！")
        payout = settle(betting[0], betting[1], r)
        amount += payout
        #print(f'払い戻し金は {payout} 円だったよ。払戻後の残金は {amount} 円だよ')
        strategy.feedback(betting[0], r)
        stat_history.append(strategy.get_stat())
      amount_history.append(amount)

  return (amount, amount_history, bet_count, win_count, lose_count, t_payout_count)

def max_drowdown(values):
  current_max = values[0]
  current_drowdown = 0
  for v in values:
    current_max = max(current_max, v)
    current_drowdown = min(current_drowdown, v - current_max)
  return current_drowdown

def max_drowdown_rate(values):
  current_max = values[0]
  current_drowdown = 0
  for v in values:
    current_max = max(current_max, v)
    current_drowdown = min(current_drowdown, v - current_max)
  return abs(current_drowdown / current_max)

def marchin(count, unit):
  return 2 ** (count - 1) * unit

def Fib(n):
  if n == 1:
    return 0
  elif n == 2:
    return 1
  else:
    return Fib(n-1) + Fib(n-2)

def cocomo(count, unit):
  return Fib(count + 1) * unit