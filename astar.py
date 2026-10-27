from heapq import heappop, heappush

def heuristic(start, end):
	return abs(start[0]-end[0])+abs(start[1]-end[1])

def astar(start, end, grid):
	closedSet = set()
	openSet = []
	cameFrom = {}
	gScore = {}
	fScore = {}

	for i in grid.get_vertices():
		gScore[i] = float("inf")
		fScore[i] = float("inf")

	gScore[start] = 0
	fScore[start] = heuristic(start,end)

	heappush(openSet, (fScore[start], start))

	while openSet:
		_, current = heappop(openSet)
		if current == end:
			return reconstruct_path(cameFrom, current)
		closedSet.add(current)
		for neighbour in grid.neighbours(current):
			if neighbour in closedSet:
				continue

			tentative_gScore = gScore[current] + heuristic(current, neighbour)
			if tentative_gScore >= gScore[neighbour]:
				continue

			cameFrom[neighbour] = current
			gScore[neighbour] = tentative_gScore
			fScore[neighbour] = gScore[neighbour] + heuristic(neighbour, end)
			heappush(openSet, (fScore[neighbour], neighbour))

	return []

def reconstruct_path(cameFrom, current):
	total_path = [current]
	while current in cameFrom.keys():
		current = cameFrom[current]
		total_path.append(current)

	return total_path[::-1]