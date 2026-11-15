from collections import deque
import numpy as np
import cv2

def bfs(binary_mask, seed_root, visited, connectivity):
    
    #Limites da imagem
    y_max, x_max = binary_mask.shape

    seed = set() #Conjunto de pixels que fazem parte da mesma semente
    queue = deque([seed_root])

    visited.add(seed_root)
    seed.add(seed_root)

    while(queue):
        y, x = queue.popleft()

        if(connectivity): #Conectividade 8
            neighbors = [
                (y - 1, x), #Cima
                (y + 1, x), #Baixo
                (y, x - 1), #Esquerda
                (y, x + 1), #Direita
                (y - 1, x + 1), #Diagonal Sup. Direita
                (y - 1, x - 1), #Diagonal Sup. Esquerda
                (y + 1, x - 1), #Diagonal Inf. Esquerda
                (y + 1, x + 1)  #Diagonal Inf. Direita
            ]
        else: #Conectividade 4
            neighbors = [
                (y - 1, x), #Cima
                (y + 1, x), #Baixo
                (y, x - 1), #Esquerda
                (y, x + 1)  #Direita
            ]

        for ny, nx in neighbors:
            #Checa se o pixel está dentro dos limites da imagem
            if(0 <= ny < y_max and 0 <= nx < x_max):
                neighbor = (ny, nx)
                #Checa se é branco e se já não foi visitado
                if binary_mask[ny, nx] > 0 and neighbor not in visited:
                    visited.add(neighbor)
                    seed.add(neighbor) #Adiciona como parte da semente que está sendo checada no momento
                    queue.append(neighbor)

    return seed

def find_seeds(binary_mask, connectivity : bool):
    #Connectivity: 0 para conectividade 4;  1 para conectividade 8
    y_max, x_max = binary_mask.shape

    visited = set()
    seeds = [] #Conjunto de sementes, sendo que cada semente é um conjunto de pixels

    for y in range(y_max):
        for x in range(x_max):
            #Quando acha um pixel branco (semente) que ainda não foi visitado
            if binary_mask[y, x] > 0 and (y, x) not in visited:
                seed = bfs(binary_mask, (y, x), visited, connectivity) #Chama o BFS para explorar aquela semente
                seeds.append(seed) #Aciona o conjunto de pixels daquela semente ao conjunto de sementes

    return seeds

#Usando os menores e maiores valores de x e y dentro de uma semente, desenha um retângulo ao redor dela
def highlight_seeds(image, seeds):
    result = image.copy()

    for seed in seeds:
        min_y = min(y for y, x in seed)
        max_y = max(y for y, x in seed)
        min_x = min(x for y, x in seed)
        max_x = max(x for y, x in seed)
        cv2.rectangle(result, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
    return result

#Retorna a área da semente em pixels
def seed_area(seed):
    return len(seed)

#Retorna o aspect ratio da semente como uma string
def seed_aspect_ratio(seed):
    min_y = min(y for y, x in seed)
    max_y = max(y for y, x in seed)
    min_x = min(x for y, x in seed)
    max_x = max(x for y, x in seed)
    y = max_y - min_y + 1
    x = max_x - min_x + 1

    return str(x) + ":" + str(y)

#Retorna uma tupla altura:largura em pixels
def seed_height_width(seed):
    min_y = min(y for y, x in seed)
    max_y = max(y for y, x in seed)
    min_x = min(x for y, x in seed)
    max_x = max(x for y, x in seed)
    y = max_y - min_y + 1
    x = max_x - min_x + 1

    #Considerando o formato das sementes, assume que ela sempre tem mais altura do que largura
    if(y >= x):
        return (y,x)
    else:
        return (x,y)

#Retorna as estatísticas de uma semente
def seed_measures(seed):
    data = []
    data.append(seed_height_width(seed))
    data.append(seed_area(seed))
    data.append(seed_aspect_ratio(seed))
    return data

#Retorna as estatísticas de todas as sementes em uma imagem
def seeds_statistics(seeds):
    statistics = []
    for seed in seeds:
        statistics.append(seed_measures(seed))
    return statistics