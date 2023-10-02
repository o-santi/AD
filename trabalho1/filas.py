from dataclasses import dataclass, field
from typing import Optional
from enum import IntEnum, auto
from numpy import random, arange, exp, array
import numpy as np
from matplotlib import pyplot as plt

class EventoTipo(IntEnum):
    Entrada = auto()
    Saida = auto()
    Atendido = auto()
    
@dataclass
class Evento:
    tipo : EventoTipo
    tempo: float
        
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
        atendido = max(chegada, ultimo_cliente.saida)
        return Cliente(chegada=chegada, atendido=atendido,
                       saida=atendido+self.tempo_de_processamento())
        
    def run(self):
        atual_cliente = Cliente(chegada=0, atendido=0,
                                   saida=self.tempo_de_processamento())
        while atual_cliente.saida < self.tempo_maximo:
            self.processados.append(atual_cliente)
            atual_cliente = self.proximo_cliente(atual_cliente)

    def run_until_empty(self):
        atual_cliente = Cliente(chegada=0, atendido=0,
                                   saida=self.tempo_de_processamento())
        while atual_cliente.saida < self.tempo_maximo:
            self.processados.append(atual_cliente)
            if not (atual_cliente := self.proximo_cliente_ou_vazio(atual_cliente)):
                return True
        return False

    def proximo_cliente_ou_vazio(self, ultimo_cliente):
        chegada = ultimo_cliente.chegada + self.chegada_aleatoria()
        if chegada < ultimo_cliente.saida:
            atendido = ultimo_cliente.saida
            return Cliente(chegada=chegada, atendido=ultimo_cliente.saida,
                           saida=atendido+self.tempo_de_processamento())
    
    def chegada_aleatoria(self):
        return random.exponential(1/self.lamda)

    def tempo_de_processamento(self):
        return random.exponential(1/self.mu)

    def eventos(self):            
        eventos = []
        
        for cliente in self.processados:
            eventos.append(Evento(EventoTipo.Entrada, cliente.chegada))
            eventos.append(Evento(EventoTipo.Saida, cliente.saida))
            eventos.append(Evento(EventoTipo.Atendido, cliente.atendido))
        return sorted(eventos, key=lambda evento: evento.tempo)
    
    def info(self):
        na_fila = 0
        curr_time = 0
        waiting_time = 0
        pessoas_area = 0
        cdf_pessoas = []
        for evento in self.eventos():
            pessoas_area += na_fila * (evento.tempo - curr_time)
            cdf_pessoas.append((pessoas_area, evento.tempo))
            curr_time = evento.tempo
            match evento.tipo:
                case EventoTipo.Saida:
                    na_fila -= 1
                case EventoTipo.Entrada:
                    na_fila += 1
        waiting_time = sum(cliente.atendido - cliente.chegada for cliente in self.processados)
        mean_waiting_time = waiting_time / len(self.processados)
        mean_pessoas_area = pessoas_area / self.tempo_maximo
        return mean_pessoas_area, mean_waiting_time, cdf_pessoas
        
    # def plot(self):
    #     [x, y] = list(zip(*points))
    #     fig = plt.figure(figsize=(10, 5))
    #     fila = fig.subplots(1, 1)
    #     fig.suptitle(f'''Fila M/M/1 ($\lambda$={self.lamda}, $\mu$={self.mu})  ($T_{{max}}={self.tempo_maximo}s) (Mean = {mean_persons/self.tempo_maximo:.2f}$)''', fontsize=15)

    #     fila.set_xlabel('Tempo (s)')
    #     fila.set_ylabel('Número de clientes')
    #     fila.bar(x, y, align='edge')
    #     fila.grid(True, axis='y', linestyle='dashed')

    #     plt.show()

def gera_cdfs(lamda, mu, tempo_maximo=100):
    serv = Servidor(lamda=lamda, mu=mu, tempo_maximo=tempo_maximo)
    serv.run()
    _, _, cdf = serv.info()
    [tempo, pessoas] = list(zip(*cdf))
    fig = plt.figure(figsize=(10, 5))
    
    fig.suptitle(f"M/M/1 ($\\lambda$ = {lamda}, $\\mu$ = {mu})")
    [clientes, espera] = fig.subplots(2, 1)
    clientes.set_title("Cdf do número de clientes")
    clientes.plot(tempo, pessoas)

    x = range(len(serv.processados))
    y = []
    soma = 0
    for cliente in serv.processados:
        soma += cliente.saida - cliente.chegada
        y.append(soma)
    espera.set_title("Cdf do tempo de espera")
    espera.plot(x, y)

    fig.tight_layout()
    plt.savefig(f"m_m_1_queue_lambda_{lamda}_mu_{mu}.png")
    
    
def simula_servidores(lamda, mu, tempo_maximo=100):
    medias = []
    rho = lamda/mu
    for n in range(100):
        serv = Servidor(lamda=lamda, mu=mu, tempo_maximo=tempo_maximo)
        serv.run()
        numero_medio_clientes, tempo_medio_espera, _ = serv.info()
        medias.append((numero_medio_clientes, tempo_medio_espera))
    def media_desvio_padrao(l):
        media = np.mean(l)
        desvio = np.std(l)
        confianca = 1.984 * (desvio / np.sqrt(len(l)))
        return media, desvio, confianca 
    [[c_media, c_desvio_padrao, c_confianca], [e_media, e_desvio_padrao, e_confianca]] = list(map(media_desvio_padrao, zip(*medias)))
    
    print(f"Média de clientes {c_media:.2f} (±{c_confianca:.2f} @ 95%) (teorico: {rho/(1-rho):.2f}), desvio padrão {c_desvio_padrao:.2f}")
    print(f"Tempo médio de espera: {e_media:.2f} (±{e_confianca:.2f} @ 95%) (teorico: {rho / (mu - lamda):.2f}) desvio padrão {e_desvio_padrao:.2f}")

def estima_terminacoes(lamda, mu, tempo_maximo=100):
    terminations = 0
    tries = 10000
    for n in range(tries):
        serv = Servidor(lamda=lamda, mu=mu, tempo_maximo=tempo_maximo)
        terminated = serv.run_until_empty()
        if terminated:
            terminations += 1
    print(f"O sistema (lambda={lamda}, mu={mu}) termina {100 * terminations / tries}% das vezes")
            
if __name__ == "__main__":
    simula_servidores(lamda=1, mu=2, tempo_maximo=1000)
    simula_servidores(lamda=2, mu=4, tempo_maximo=1000)
    gera_cdfs(lamda=1, mu=2)
    gera_cdfs(lamda=2, mu=4)
    estima_terminacoes(lamda=2,    mu=4)
    estima_terminacoes(lamda=1,    mu=2)
    estima_terminacoes(lamda=1.05, mu=1)
    estima_terminacoes(lamda=1.10, mu=1)
