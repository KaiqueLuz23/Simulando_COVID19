import matplotlib.pyplot as plt
import matplotlib.animation as ani
import numpy as np

# Tuplas RGB
import pit as pit

GREY = (0.78, 0.78, 0.78)  # Não infectados
RED = (0.96, 0.15, 0.15)  # Infectados
GREEN = (0, 0.86, 0.03)  # Recuperados
BLACK = (0, 0, 0)  # Mortos

# Leves: L / Graves: G / Porcentagem: porcen / Fatalidade: F / r0: n° esperado de casos/dia
COVID19_PARAMS = {
    "r0": 2.28,
    "incubacao": 5,
    "porcen_L": 0.8,
    "recuperacao_L": (7, 14),
    "porcen_G": 0.2,
    "recuperacao_G": (21, 42),
    "mortes_G": (14, 56),
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
        self.dia_text = self.axes.annotate(
            "Dia 0", xy=[np.pi / 2, 1], ha="center", va="bottom"
        )
        self.infectados_tex = self.axes.annotate(
            "Infectados: 0", xy=[3 * np.pi / 2, 1], ha="center", va="top", color=RED
        )
        self.mortos_text = self.axes.annotate(
            "\nMortos: 0", xy=[3 * np.pi / 2, 1], ha="center", va="top", color=BLACK
        )
        self.recuperados_text = self.axes.annotate(
            "\n\nRecuperados: 0", xy=[3 * np.pi / 2, 1], ha="center", va="top", color=GREEN
        )

        # criando variáveis de membros
        self.dia = 0
        self.total_num_infectados = 0
        self.num_atualmente_infectados = 0
        self.num_recuperados = 0
        self.num_mortos = 0
        self.r0 = params["r0"]
        self.porcen_L = params["porcen_L"]
        self.porcen_G = params["porcen_G"]
        self.indice_F = params["indice_F"]
        self.intervalo_serial = params["intervalo_serial"]

        self.L_fast = params["incubacao"] + params["recuperacao_L"][0]
        self.L_slow = params["incubacao"] + params["recuperacao_L"][1]
        self.G_fast = params["incubacao"] + params["recuperacao_G"][0]
        self.G_slow = params["incubacao"] + params["recuperacao_G"][1]
        self.mortes_fast = params["incubacao"] + params["mortes_G"][0]
        self.mortes_slow = params["incubacao"] + params["mortes_G"][1]

        self.L = {i: {"thetas": [], "rs": []} for i in range(self.L_fast, 365)}
        self.G = {
            "recupercao": {i: {"thetas": [], "rs": []} for i in range(self.G_fast, 365)},
            "mortes": {i: {"thetas": [], "rs": []} for i in range(self.mortes_fast, 365)}
        }

        self.exposto_antes = 0
        self.exposto_depois = 1

        self.populacao_inicial()

    def populacao_inicial(self):
        polulacao = 4500
        self.num_atualmente_infectados = 1
        self.total_num_infectados = 1
        indices = np.arange(0, polulacao) + 0.5
        self.thetas = np.pi * (1 + 5 ** 0.5) * indices
        self.rs = np.sqrt(indices / polulacao)
        self.plot = self.axes.scatter(self.thetas, self.rs, s=5, color=GREY)

        self.axes.scatter(self.thetas[0], self.rs[0], s=5, color=RED)
        self.L[self.L_fast]["thetas"].append(self.thetas[0])
        self.L[self.L_fast]["rs"].append(self.rs[0])


    def propagar_vírus(self, i):
        self.exposto_antes = self.exposto_depois
        if self.dia % self.intervalo_serial == 0 and self.exposto_antes < 4500:
            self.num_novos_infectados = round(self.r0 * self.total_num_infectados)
            self.exposto_depois += round(self.num_novos_infectados * 1.1)
            if self.exposto_depois > 4500:
                self.num_novos_infectados = round((4500 - self.exposto_antes) * 0.9)
                self.exposto_depois = 4500
            self.num_atualmente_infectados += self.num_novos_infectados
            self.total_num_infectados += self.num_novos_infectados
            self.novos_infectados_indices = list(
                np.random.choice(
                    range(self.exposto_antes, self.exposto_depois),
                    self.num_novos_infectados,
                    replace=False
                )
            )
            thetas = [self.thetas[i] for i in self.novos_infectados_indices]
            rs = [self.rs[i] for i in self.novos_infectados_indices]
            self.anim.event_source_stop()
            if len(self.novos_infectados_indices) > 24:
                size_list = round(len(self.novos_infectados_indices) / 24)
                thetas_chunks = list(self.chunks(thetas, size_list))
                r_chunks = list(self.chunks(rs, size_list))
                self.anim2 = ani.FuncAnimation(
                    self.fig,
                    self.one_by_one,
                    interval=50,
                    frames=len(thetas_chunks),
                    fargs=(thetas_chunks,r_chunks,RED)
                )
            else:
                self.anim2 = ani.FuncAnimation(
                    self.fig,
                    self.one_by_one,
                    interval=50,
                    frames=len(thetas),
                    fargs=(thetas, rs, RED)
                )
            self.baixo_sintomas()


        self.dia += 1

        self.atualizar_status()
        self.atualizar_text()

    def one_by_one(self, i, thetas, rs, color):
        self.axes.scatter(thetas[i],rs[i], s=5, color=color)
        if i == (len(thetas) - 1):
            self.anim2.event_source.stop()
            self.anim.event_source_start()

    def chunks(self, a_list, n):
        for i in range(0, len(a_list), n):
            yield a_list[i:i + n]




    def atribuir_sintomas(self):
        num_L = round(self.porcen_L * self.num_novos_infectados)
        num_G = round(self.porcen_G * self.num_novos_infectados)
        # escolha um subconjunto aleatório de recém-infectados para ter sintomas leves
        self.L_indice = np.random.choice(
            self.novos_infectados_indices, num_L, replace=False
        )
        # atribuir ao restante sintomas graves, resultando em recuperação ou morte
        remanescente_indices = [
            i for i in self.novos_infectados_indices if i not in self.L_indice
        ]
        porcen_G_recuperados = 1 - (self.indice_F / self.porcen_G)
        num_G_recuparedos = round(porcen_G_recuperados * num_G)
        self.G_indices = []
        self.Mortes_indices = []
        if remanescente_indices:
            self.G_indices = np.random.choice(
                remanescente_indices, num_G_recuparedos, replace=False
            )
            self.morte_indices = [
                i for i in remanescente_indices if  i not  in self.G_indices
            ]

        # atribuir recuperação / dia da morte

        baixo = self.dia + self.L_fast
        alto = self.dia + self.L_slow
        for L  in self.L_indice:
            recuperados_dia = np.random.randint(baixo, alto)
            L_theta = self.thetas[L]
            L_r = self.rs[L]
            self.L[recuperados_dia]["thetas"].append(L_theta)
            self.L[recuperados_dia]["rs"].append(L_r)

    def atualizar_status(self):
        if self.dia >= self.L_fast:
            L_thetas = self.L[self.dia]["thetas"]
            L_rs = self.L[self.dia]["rs"]
            self.axes.scatter(L_thetas, L_rs, s=5, color=GREEN)
            self.num_atualmente_infectados -= len(L_thetas)
        if self.dia >= self.G_fast:
            rec_thetas = self.G["recuperados"][self.dia]["thetas"]
            rec_rs = self.G["recuperados"][self.dia]["rs"]
            self.axes.scatter(rec_thetas, rec_rs, s=5, color=GREEN)
            self.num_recuperados += len(rec_thetas)
            self.num_atualmente_infectados -= len(rec_thetas)
        if self.dia >= self.mortes_fast:
            mortes_thetas = self.G["mortes"][self.dia]["thetas"]
            mortes_rs = self.G["mortes"][self.dia]["rs"]
            self.axes.scatter(mortes_thetas, mortes_rs, s=5, color=BLACK)
            self.num_mortos += len(mortes_thetas)
            self.num_atualmente_infectados -= len(mortes_thetas)


    def atualizar_text(self):
        self.dia_text.set_text("Dia {}".format(self.dia))
        self.infectados_tex.set_text("Infectados: {}".format(self.num_atualmente_infectados))
        self.mortos_text.set_text("\nMortos: {}".format(self.num_mortos))
        self.recuperados_text.set_text("\n\nRecuperados: {}".format(self.num_recuperados))



    # Animando o vírus se espalhando com "Matplotlib"

    def gen(self):
        while self.num_mortos + self.num_recuperados < self.total_num_infectados:
            yield


    def animate(self):
        self.anim = ani.FuncAnimation(
            self.fig,
            self.propagar_virus,
            frames= self.gen,
            repeat=True
    )


def main():
    coronavirus = Virus(COVID19_PARAMS)
    coronavirus.animate
    plt.show()

if __name__ == "__main__":
    main()


#Virus(COVID19_PARAMS)
#plt.show()
