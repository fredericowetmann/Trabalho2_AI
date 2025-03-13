import numpy as np
import random
import matplotlib.pyplot as plt

class DifferentialEvolution:
    def __init__(self, pop_size, max_iter, sheet_width, sheet_height, recortes_disponiveis):
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.recortes_disponiveis = recortes_disponiveis
        self.population = self.initialize_population()

    def initialize_population(self):
        population = []
        for _ in range(self.pop_size):
            individual = []
            for recorte in self.recortes_disponiveis:
                new_x = random.uniform(0, self.sheet_width - recorte.get('largura', recorte.get('r', 0) * 2))
                new_y = random.uniform(0, self.sheet_height - recorte.get('altura', recorte.get('r', 0) * 2))
                new_rotation = random.choice([0, 90])
                individual.append({**recorte, "x": new_x, "y": new_y, "rotacao": new_rotation})
            population.append(individual)
        return population
    
    def evaluate(self, candidate):
        penalty = 0
        for i, shape in enumerate(candidate):
            if shape['x'] < 0 or shape['x'] > self.sheet_width or shape['y'] < 0 or shape['y'] > self.sheet_height:
                penalty += 100  # Penaliza formas fora da área
            
            for j, other in enumerate(candidate):
                if i != j and self.overlaps(shape, other):
                    penalty += 50  # Penaliza sobreposição
        
        return penalty
    
    def overlaps(self, shape1, shape2):
        if shape1['tipo'] == 'circular' and shape2['tipo'] == 'circular':
            distance = np.sqrt((shape1['x'] - shape2['x'])**2 + (shape1['y'] - shape2['y'])**2)
            return distance < (shape1['r'] + shape2['r'])
        
        if shape1['tipo'] != 'circular' and shape2['tipo'] != 'circular':
            return not (shape1['x'] + shape1['largura'] <= shape2['x'] or
                        shape2['x'] + shape2['largura'] <= shape1['x'] or
                        shape1['y'] + shape1['altura'] <= shape2['y'] or
                        shape2['y'] + shape2['altura'] <= shape1['y'])
        
        return False
    
    def mutate(self, target_index):
        idxs = [idx for idx in range(self.pop_size) if idx != target_index]
        a, b, c = random.sample(idxs, 3)
        mutant = []
        for i in range(len(self.recortes_disponiveis)):
            new_x = self.population[a][i]['x'] + 0.8 * (self.population[b][i]['x'] - self.population[c][i]['x'])
            new_y = self.population[a][i]['y'] + 0.8 * (self.population[b][i]['y'] - self.population[c][i]['y'])
            mutant.append({**self.recortes_disponiveis[i], "x": new_x, "y": new_y})
        return mutant
    
    def crossover(self, target, mutant):
        trial = []
        for i in range(len(target)):
            if random.random() < 0.9:
                trial.append(mutant[i])
            else:
                trial.append(target[i])
        return trial
    
    def select(self, target, trial):
        if self.evaluate(trial) < self.evaluate(target):
            return trial
        return target
    
    def run(self):
        for _ in range(self.max_iter):
            new_population = []
            for i in range(self.pop_size):
                mutant = self.mutate(i)
                trial = self.crossover(self.population[i], mutant)
                new_population.append(self.select(self.population[i], trial))
            self.population = new_population
        return min(self.population, key=self.evaluate)
    
    def plot_layout(self, layout):
        fig, ax = plt.subplots()
        ax.set_xlim(0, self.sheet_width)
        ax.set_ylim(0, self.sheet_height)
        ax.set_title("Layout Otimizado")
        
        for shape in layout:
            if shape['tipo'] == 'retangular':
                rect = plt.Rectangle((shape['x'], shape['y']), shape['largura'], shape['altura'], edgecolor='b', facecolor='none')
                ax.add_patch(rect)
            elif shape['tipo'] == 'circular':
                circ = plt.Circle((shape['x'], shape['y']), shape['r'], edgecolor='r', facecolor='none')
                ax.add_patch(circ)
            elif shape['tipo'] == 'diamante':
                x, y = shape['x'], shape['y']
                width, height = shape['largura'], shape['altura']
                diamond = plt.Polygon([[x, y + height / 2], [x + width / 2, y], [x, y - height / 2], [x - width / 2, y]], edgecolor='g', facecolor='none')
                ax.add_patch(diamond)
        
        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()
    
    def optimize_and_display(self):
        """
        Executa a otimização, exibe o layout final e retorna o melhor layout encontrado.
        """
        print("Executando otimização com Evolução Diferencial...")
        self.optimized_layout = self.run()
        print("Otimização concluída.")
        self.plot_layout(self.optimized_layout)
        return self.optimized_layout