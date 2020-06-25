# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action
import random
from enum import Enum, unique


class MyAI( AI ):


	@unique
	class Orientation (Enum):
		TOP_LEFT = 0
		TOP_RIGHT = 1
		RIGHT_TOP = 2
		RIGHT_BOT = 3
		BOT_LEFT = 4
		BOT_RIGHT = 5
		LEFT_TOP = 6
		LEFT_BOT = 7
		NONE = 8

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		
		#startx and starty are the safe starting spot
		self.__rowDimension = colDimension
		self.__colDimension = rowDimension
		self.__moveCount = 0
		self.__startX = startX
		self.__startY = startY
		self.working = {}
		self.finished = []
		self.toDo = {}
		self.bombs = []
		self.__lastX = startX
		self.__lastY = startY
		self.__tilesLeft = rowDimension * colDimension - 1
		self.__totalMines = totalMines


	def inBound(self, x, y):
		if x in range(self.__rowDimension) and y in range(self.__colDimension):
			return True
		return False

	def covered(self, x, y):
		coord = (x, y)
		if coord not in list(self.toDo.keys()) and coord not in self.finished and coord not in list(self.working.keys()):
			return True
		return False

	def handle0(self, x, y):
		vals = [-1, 0, 1]
		for i in vals:
			for j in vals:
				if self.inBound(x + i, y + j) and self.covered(x + i, y + j):
					self.toDo[(x + i, y + j)] = AI.Action.UNCOVER


	def getAdj(self, x, y):
		#returns a list of covered tiles adjacent to given tile
		ls = []
		vals = [-1, 0, 1]
		for i in vals:
			for j in vals:
				if self.inBound(x + i, y + j) and self.covered(x + i, y + j):
					ls.append((x+i, y+j))
		return ls

	def getAdjUncover(self, x, y):
		ls = []
		vals = [-1, 0, 1]
		for i in vals:
			for j in vals:
				if self.inBound(x + i, y + j) and not self.covered(x + i, y + j):
					ls.append((x+i, y+j))
		return ls

	def isAdj(self, x, y, a, b):
		if abs(x - a) <= 1 and abs(y - b) <= 1:
			return True
		return False

	def getNearbyUncover(self, x, y):
		ls = []
		vals = [-1, 1]
		for i in vals:
			if self.inBound(x + i, y) and not self.covered(x + i, y):
				ls.append((x + i, y))
			if self.inBound(x, y + i) and not self.covered(x, y + i):
				ls.append((x, y + i))
		return ls

	def checkEdge(self, x, y, t_x, t_y):
		dif_x = x - t_x
		dif_y = y - t_y
		orig_cover = self.getAdj(x, y)
		len_o = len(orig_cover)
		close_cover = self.getAdj(t_x, t_y)
		len_c = len(close_cover)
		orientation = self.Orientation.NONE
		if dif_y == 1: # BOT_LEFT OR BOT_RIGHT
			if len_o == 2 and len_c <= 3:
				if (x - 1, y) in orig_cover and (x - 1, y - 1) in orig_cover and (x - 1, y - 2) in close_cover:
					orientation = self.Orientation.BOT_LEFT
				elif (x + 1, y) in orig_cover and (x + 1, y - 1) in orig_cover and (x + 1, y - 2) in close_cover:
					orientation = self.Orientation.BOT_RIGHT
		elif dif_y == -1: # TOP_LEFT OR TOP_RIGHT
			if len_o == 2 and len_c == 3:
				if (x - 1, y) in orig_cover and (x - 1, y + 1) in orig_cover and (x - 1, y + 2) in close_cover:
					orientation = self.Orientation.TOP_LEFT
				elif (x + 1, y) in orig_cover and (x + 1, y + 1) in orig_cover and (x + 1, y + 2) in close_cover:
					orientation = self.Orientation.TOP_RIGHT
		elif dif_x == 1: #LEFT_TOP OR LEFT_BOT
			if len_o == 2 and len_c == 3:
				if (x, y + 1) in orig_cover and (x - 1, y + 1) in orig_cover and (x - 2, y + 1) in close_cover:
					orientation = self.Orientation.LEFT_TOP
				elif (x, y - 1) in orig_cover and (x - 1, y - 1) in orig_cover and (x - 2, y - 1) in close_cover:
					orientation = self.Orientation.LEFT_BOT
		elif dif_x == -1: #RIGHT_TOP OR RIGHT_BOT
			if len_o == 2 and len_c == 3:
				if (x, y + 1) in orig_cover and (x + 1, y + 1) in orig_cover and (x + 2, y + 1) in close_cover:
					orientation = self.Orientation.RIGHT_TOP
				elif (x, y - 1) in orig_cover and (x + 1, y - 1) in orig_cover and (x + 2, y - 1) in close_cover:
					orientation = self.Orientation.RIGHT_BOT	
			
		return orientation

	def isFinished(self, x, y):
		ls = self.getAdjUncover(x, y)
		if len(ls) == 0:
			return True
		return False

	def infer(self, coord):
		(x, y) = coord
		nearby = self.getNearbyUncover(x, y)
		for tile in nearby:
			(t_x, t_y) = tile
			val = 0
			if tile in list(self.working.keys()):
				val = self.working[tile]
				if val == 1 or val == 2:
					new = (0, 0)
					orientation = self.checkEdge(x, y, t_x, t_y)
					if orientation == self.Orientation.TOP_LEFT:
						new = (x - 1, y + 2)
					elif orientation == self.Orientation.TOP_RIGHT:
						new = (x + 1, y + 2)
					elif orientation == self.Orientation.RIGHT_TOP:
						new = (x + 2, y + 1)
					elif orientation == self.Orientation.RIGHT_BOT:
						new = (x + 2, y - 1)
					elif orientation == self.Orientation.BOT_LEFT:
						new = (x - 1, y - 2)
					elif orientation == self.Orientation.BOT_RIGHT:
						new = (x + 1, y - 2)
					elif orientation == self.Orientation.LEFT_TOP:
						new = (x - 2, y + 1)
					elif orientation == self.Orientation.LEFT_BOT:
						new = (x - 2, y - 1)

					(i_x, i_y) = new
					if orientation != self.Orientation.NONE and self.inBound(i_x, i_y) and self.covered(i_x, i_y):
						if val == 1:
							self.toDo[new] = AI.Action.UNCOVER
							ls = self.getAdjUncover(i_x, i_y)
							for l in ls:
								(sub_x, sub_y) = l
								if self.isFinished(sub_x, sub_y):
									self.working.pop(l)
									self.finished.append(l)
						else:
							self.toDo[new] = AI.Action.FLAG
							#for all tile adjacent to bomb that are uncovered, subtract 1 from value
							self.bombs.append(new)
							self.finished.append(new)
							b_ls = self.getAdjUncover(i_x, i_y)
							for sub_sub_coord in b_ls:
								if sub_sub_coord in list(self.working.keys()):
									self.working[sub_sub_coord] -= 1
	def getAction(self, number: int) -> "Action Object":
		if number >= 0:
				coord = (self.__lastX, self.__lastY)
				for bomb in self.bombs:
					(b_x, b_y) = bomb
					if self.isAdj(b_x, b_y, self.__lastX, self.__lastY):
						number -= 1
				self.working[coord] = number
				
		if self.working:
			for coord in list(self.working.keys()):
				(d_x, d_y) = coord
				num = self.working[coord]
				if num == 0:
					self.handle0(d_x, d_y)
					self.finished.append(coord)
					self.working.pop(coord)	
				else:
					ls = self.getAdj(d_x, d_y)
					length = len(ls)
					#all adj tiles are bombs
					if length == num:
						self.finished.append(coord)
						self.working.pop(coord)
						for sub_coord in ls:
							(b_x, b_y) = sub_coord
							self.toDo[sub_coord] = AI.Action.FLAG
							self.bombs.append(sub_coord)
							#not sure if we append bomb to finished or working or neither??
							self.finished.append(sub_coord)
							b_ls = self.getAdjUncover(b_x, b_y)
							for sub_sub_coord in b_ls:
								if sub_sub_coord in list(self.working.keys()):
									self.working[sub_sub_coord] -= 1
					elif num == 1:
						self.infer(coord)


		if self.toDo:
			k = list(self.toDo.keys())
			coord = k[0]
			(x, y) = coord
			action = self.toDo[coord]
			self.toDo.pop(coord)
			self.__lastX = x
			self.__lastY = y
			if action == AI.Action.UNCOVER:
				self.__tilesLeft -= 1
			return Action(action, x, y)	


		if self.__tilesLeft > self.__totalMines:
			random_chance = (self.__totalMines - len(self.bombs)) / self.__tilesLeft

			min_chance = 1.0
			min_coord = (0, 0)

			for coord in list(self.working.keys()):
				(x, y) = coord
				num_adj = len(self.getAdj(x, y))
				chance = self.working[coord] / num_adj
				if chance < min_chance:
					min_chance = chance
					min_coord = coord

			if min_chance < random_chance:
				(x, y) = min_coord
				#guess = (random.shuffle(self.getAdj(x, y)))[0]
				guess_l = self.getAdj(x, y)
				random.shuffle(guess_l)
				guess = guess_l[0]
				(xx, yy) = guess
				self.__lastX = xx
				self.__lastY = yy
				self.__tilesLeft -= 1
				return Action(AI.Action.UNCOVER, xx, yy)

			#random guess
			xs = list(range(0, self.__rowDimension))
			random.shuffle(xs)
			ys = list(range(0, self.__colDimension))
			random.shuffle(ys)
			for x in xs:
				for y in ys:
					if self.covered(x, y):
						self.__lastX = x
						self.__lastY = y
						self.__tilesLeft -=1	
						return Action(AI.Action.UNCOVER, x, y)
		else:
			return Action(AI.Action.LEAVE)