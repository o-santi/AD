from dataclasses import dataclass, field
from typing import Optional
from enum import IntEnum, auto

@dataclass
class Cliente:
    chegada: float
    saida: Optional[float] = None
    
@dataclass
class Servidor:
    lamda: float
    mu: float
    tempo_maximo: float
    
    fila_de_clientes: list[Cliente] = field(default_factory=list)
    processados: list[Cliente] = field(default_factory=list)

    def proximo_cliente(self):
        try:
            return self.fila_de_clientes.pop(0)
        except IndexError:
            return None
    
    def run(self):
        tempo_atual = 0
        ultima_chegada = 0
        while tempo_atual < self.tempo_maximo:
            print(self.processados)
            while ultima_chegada <= tempo_atual:
                self.fila_de_clientes.append(Cliente(chegada=ultima_chegada))
                ultima_chegada += self.chegada_aleatoria()
            while (cliente := self.proximo_cliente()):
                tempo_atual += self.tempo_de_processamento()
                cliente.saida = tempo_atual
                self.processados.append(cliente)

    def chegada_aleatoria(self):
        return 0.5 # TODO: this

    def tempo_de_processamento(self):
        return 1.0 # TODO: this
    
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
        for cliente in self.processados:
            eventos.append(Evento(EventoTipo.Entrada, cliente.chegada))
            eventos.append(Evento(EventoTipo.Saida, cliente.saida))
        for evento in sorted(eventos, key=lambda evento: evento.tempo):
            if evento.tipo == EventoTipo.Entrada:
                na_fila += 1
            else:
                na_fila -= 1
            print(f"{'👨'* na_fila}")
            
if __name__ == "__main__":
    fila1 = Servidor(lamda=2, mu=4, tempo_maximo=10)
    fila1.run()
    fila1.show_log()
    
            
