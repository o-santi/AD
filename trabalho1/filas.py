from dataclasses import dataclass
from enum import IntEnum, auto
from itertools import count

class EstadoDoServidor(IntEnum):
    Ocioso = auto()
    Processando = auto()

@dataclass
class Cliente:
    chegada: float
    
@dataclass
class Servidor:
    clientes: list[Cliente]
    lamda: float
    mu: float

    tempo_maximo: float
    estado: EstadoDoServidor
    def run2(self):
        chegadas = [0]
        tempo = 0
        while tempo < self.tempo_maximo:
            poisson = self.poisson()
            chegadas.push(poisson)
            tempo += poisson
        partidas = []
        entrada_ultimo_usuario = 0
        for (chegada, prox) in zip(chegadas[:-1], chegadas[1:]):
            atendimento = self.exponencial()
            partida = tempo + atendimento
            partidas.push(partida)
            if prox > partida:
                tempo = prox
            else:
                tempo = partida

    def __init__(self, lamda, mu):
        self.lamda = lamda
        self.mu = mu
        self.clientes = [Cliente(chegada = 0)]
    
    def run(self):
        tempo = 0
        while tempo < self.tempo_maximo:
            match self.estado:
                case EstadoDoServidor.Ocioso:
                    if (cliente := self.clientes.pop(0)):
                        self.estado = EstadoDoServidor.Processando
                    self.clientes.push(Cliente(chegada=self.poisson(self.lamda)))
                    tempo += 
                case EstadoDoServidor.Processando:
                    tempo += self.exponencial()
                    self.estado = EstadoDoServidor.Ocioso
                
    def poisson(self):
        
        pass
                    
if __init__ == "__main__":
    pass
    
            
