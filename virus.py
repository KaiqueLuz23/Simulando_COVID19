import matplotlib.pyplot as plt
import matplotlib.animation as ani
import numby as np


# Tuplas RGB
GREY = (0.78, 0.78, 0,78) # Não infectados
RED = (0.96, 0.15, 0.15)  # Infectados
GREEN = (0, 0.86, 0.03)   # Recuperados
BLACK = (0, 0, 0)          # Mortos

# Leves: L / Graves: G / Porcentagem: porcen / Fatalidade: F
COVID19_PARAMS ={
    "r0": 2.28,
    "incubacao": 5,
    "porcen_L": 0.8,
    "recuperacao_L": (7, 14),
    "porcen_G": 0.2,
    "recuperacao_G": (21, 42),
    "G_mortes": (14, 56),
    "indice_F": 0.034,
    "intervalo_serial": 7
}

class Virus():
    def __init__(self, params):
        # criando plot
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111, projection="polar")
        self.axes.grid(False)
        self.axes.set_xticklabels([])
        self.axes.set_xticklabels([])
        self.axes.set_ylim(0, 1)

        # criando anotações
        self.day_text = self.axes.annotate(
            "Day 0", xy=[       )