from dataclasses import dataclass, field
from typing import Optional
from enum import IntEnum, auto
from numpy import random

@dataclass
class Cliente:
    chegada: float
    saida: Optional[float] = None
    
@dataclass
class Servidor:
    lamda: float
    mu: float
    tempo_maximo: float
    
    fila_de_clientes: list[Cliente] = field(default_factory=lambda: [Cliente(chegada=0)])
    processados: list[Cliente] = field(default_factory=list)

    def proximo_cliente(self):
        try:
            return self.fila_de_clientes.pop(0)
        except IndexError:
            return None
    
    def run(self):
        tempo_atual = 0
        ultima_chegada = 0
        while (cliente := self.proximo_cliente()):
            if tempo_atual > self.tempo_maximo:
                return False
            if cliente.chegada > tempo_atual:
                return True
            tempo_atual += self.tempo_de_processamento()
            cliente.saida = tempo_atual
            self.processados.append(cliente)
            while ultima_chegada <= tempo_atual:
                ultima_chegada += self.chegada_aleatoria()
                self.fila_de_clientes.append(Cliente(chegada=ultima_chegada))
        return True
    
    def chegada_aleatoria(self):
        chegada = random.exponential(self.lamda)
        return chegada

    def tempo_de_processamento(self):
        saida = random.exponential(self.mu)
        return saida 
    
    def show_log(self):
        class EventoTipo(IntEnum):
            Entrada = auto()
            Saida = auto()

        @dataclass
        class Evento:
            tipo : EventoTipo
            tempo: float
            
        eventos: list[Evento] = []
        na_fila = 0
        for cliente in self.fila_de_clientes + self.processados:
            eventos.append(Evento(EventoTipo.Entrada, cliente.chegada))
            if cliente.saida:
                eventos.append(Evento(EventoTipo.Saida, cliente.saida))
        for evento in sorted(eventos, key=lambda evento: evento.tempo):
            if evento.tipo == EventoTipo.Entrada:
                na_fila += 1
            else:
                na_fila -= 1
            print(f"{'👨'* na_fila} {evento.tempo:.2f}")
            
if __name__ == "__main__":
    fila1 = Servidor(lamda=1, mu=2, tempo_maximo=10)
    success = fila1.run()
    fila1.show_log()
    print('fila chegou a zero') if success else print('fila nunca acabou... :\'(')
    
            
