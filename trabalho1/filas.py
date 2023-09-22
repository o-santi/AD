from dataclasses import dataclass, field
from typing import Optional
from enum import IntEnum, auto
from numpy import random

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
    
    def show_log(self):
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
        for evento in sorted(eventos, key=lambda evento: evento.tempo):
            match evento.tipo:
                case EventoTipo.Saida:
                    na_fila -= 1
                case EventoTipo.Entrada:
                    na_fila += 1
                    max_na_fila = max(max_na_fila, na_fila)
                    
        arrival_medio = sum(prox.chegada - c.chegada for (c, prox) in zip(self.processados[:-1], self.processados[1:])) / len(self.processados)
        espera_media = sum(cliente.atendido - cliente.chegada for cliente in self.processados) / len(self.processados)
        tempo_de_atendimento = sum(cliente.saida - cliente.atendido for cliente in self.processados) / len(self.processados)
        tempo_ocioso = sum(prox.atendido - c.saida for (c, prox) in zip(self.processados[:-1], self.processados[1:]))
                           
        print(f"Número de pessoas processadas {len(self.processados)}")
        print(f"Máximo de pessoas na fila {max_na_fila}")
        print(f"Média de tempo para chegada {arrival_medio:.2f}s")
        print(f"Média de tempo de espera {espera_media:.2f}s")
        print(f"Média de tempo de atendimento {tempo_de_atendimento:.2f}s")
        print(f"Tempo ocioso total {tempo_ocioso:.1f}s ({100 *tempo_ocioso/self.tempo_maximo:.2f}% do total)")

            
if __name__ == "__main__":
    fila1 = Servidor(lamda=2, mu=2, tempo_maximo=100)
    fila1.run()
    fila1.show_log()
    
    
            
