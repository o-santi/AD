from dataclasses import dataclass, field
from typing import Optional
from enum import IntEnum, auto
from numpy import random, arange, exp, array
import numpy as np
from matplotlib import pyplot as plt

def align_yaxis(ax1, ax2):
    ax1_ylims = ax1.axes.get_ylim()           # Find y-axis limits set by the plotter
    ax1_yratio = ax1_ylims[0] / ax1_ylims[1]  # Calculate ratio of lowest limit to highest limit

    ax2_ylims = ax2.axes.get_ylim()           # Find y-axis limits set by the plotter
    ax2_yratio = ax2_ylims[0] / ax2_ylims[1]  # Calculate ratio of lowest limit to highest limit
    
    if ax1_yratio < ax2_yratio: 
        ax2.set_ylim(bottom = ax2_ylims[1]*ax1_yratio)
    else:
        ax1.set_ylim(bottom = ax1_ylims[1]*ax2_yratio)
        
@dataclass
class Cliente:
    chegada: float
    atendido: Optional[float] = None
    saida: Optional[float] = None
    
@dataclass
class Servidor:
    lamda: float
    mu: float
    tempo_maximo: float

    processados: list[Cliente] = field(default_factory=list)
    
    def proximo_cliente(self, ultimo_cliente: Cliente) -> Cliente:
        chegada = ultimo_cliente.chegada + self.chegada_aleatoria()
        if chegada > ultimo_cliente.saida:
            atendido = chegada
            return Cliente(chegada=chegada, atendido=atendido,
                           saida=atendido+self.tempo_de_processamento())
        else:
            atendido = ultimo_cliente.saida
            return Cliente(chegada=chegada, atendido=ultimo_cliente.saida,
                           saida=atendido+self.tempo_de_processamento())
        
    def run(self):
        atual_cliente = Cliente(chegada=0, atendido=0,
                                   saida=self.tempo_de_processamento())
        while atual_cliente.saida < self.tempo_maximo:
            self.processados.append(atual_cliente)
            atual_cliente = self.proximo_cliente(atual_cliente)
    
    def chegada_aleatoria(self):
        return random.exponential(1/self.lamda)
         

    def tempo_de_processamento(self):
        return random.exponential(1/self.mu)
    
    def info(self):
        class EventoTipo(IntEnum):
            Entrada = auto()
            Saida = auto()
            Atendido = auto()

        @dataclass
        class Evento:
            tipo : EventoTipo
            tempo: float
            
        eventos: list[Evento] = []
        for cliente in self.processados:
            eventos.append(Evento(EventoTipo.Entrada, cliente.chegada))
            eventos.append(Evento(EventoTipo.Saida, cliente.saida))
            eventos.append(Evento(EventoTipo.Atendido, cliente.atendido))
        na_fila = 0
        max_na_fila = 0
        points = [(0, 1)]
        for evento in sorted(eventos, key=lambda evento: evento.tempo):
            match evento.tipo:
                case EventoTipo.Saida:
                    na_fila -= 1
                    points.append((evento.tempo, na_fila))
                case EventoTipo.Entrada:
                    na_fila += 1
                    points.append((evento.tempo, na_fila))
                    max_na_fila = max(max_na_fila, na_fila)
       
        [x, y] = list(zip(*points))
        fig = plt.figure(figsize=(10, 5))
        (fila, histograma) = fig.subplots(2, 2, width_ratios=[2, 1, 1, 1])
        fig.suptitle(f'Fila M/M/1 ($\lambda$={self.lamda}, $\mu$={self.mu}) ($T_{{max}}={self.tempo_maximo}s)$', fontsize=15)
        fila.set_xlabel('Tempo (s)')
        fila.set_ylabel('Número de clientes')
        fila.bar(x, y, align='edge')
        fila.grid(True, axis='y', linestyle='dashed')

        rho = self.lamda / self.mu
        cdf_x = arange(0, self.tempo_maximo, 0.1)
        cdf_y = []
        xs = (p for p in points)
        proximo_y = 1
        atual_x, atual_y = (0, 1)
        for x in cdf_x:
            while atual_x < x:
                try:
                    atual_y = proximo_y
                    atual_x, proximo_y = next(xs) 
                except:
                    break
            cdf_y.append(atual_y)

        histograma.set_title(f'CDF (media={np.sum(cdf_y) / len(cdf_y):.2f}, teorico={rho / (1 - rho):.2f})')
        histograma.hist(cdf_y, bins=max_na_fila, histtype='step', align='mid', color='blue')
        histograma.tick_params(axis='y', colors='blue')
        poisson = histograma.twinx()
        poisson_x = arange(0, max_na_fila, 0.01)
        poisson.plot(poisson_x, list(map(lambda k: exp(-rho * k) * rho, poisson_x)),
                     label=f'Teorico = Exp($\\lambda$=$\\rho$={rho:.2f})',
                     color='red', alpha=0.8, linestyle='dashed')
        poisson.tick_params(axis='y', colors='red')
        poisson.legend()
        
        # align_yaxis(histograma, poisson) 

        plt.show()

        # print(f"Número de pessoas processadas {len(self.processados)}")
        # print(f"Máximo de pessoas na fila {max_na_fila}")
        # print(f"Média de tempo para chegada {arrival_medio:.2f}s")
        # print(f"Média de tempo de espera {espera_media:.2f}s")
        # print(f"Média de tempo de atendimento {tempo_de_atendimento:.2f}s")
        # print(f"Tempo ocioso total {tempo_ocioso:.1f}s ({100 *tempo_ocioso/self.tempo_maximo:.2f}% do total)")

            
if __name__ == "__main__":

    fila = Servidor(lamda=1, mu=4.1, tempo_maximo=10000)
    fila.run()
    fila.info()
