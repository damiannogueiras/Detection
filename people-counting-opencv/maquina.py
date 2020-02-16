from statemachine import StateMachine, State
import time


class Maquina(StateMachine):
    # definimos los estados
    tranquilo = State('Tranquilo', 1, initial=True)
    susto = State('Susto', 2)
    achantado = State('Achantado', 3)
    vuelvo = State('Vuelvo', 4)

    # definimos las transiciones
    persona_cerca = tranquilo.to(susto)
    achanta = susto.to(achantado)
    paso_peligro = achantado.to(vuelvo)
    descanso = vuelvo.to(tranquilo)

    # variables
    t_susto = 0

    def on_enter_tranquilo(self):
        print("Estoy tranquilo")
        # lanzo escena 1: tranquilo
        print("Lanzo escena1")

    def on_persona_cerca(self):
        print('Hay alguien!!!')
        # empiezo a contar el tiempo
        t_susto = time.time_ns() // 1000000

    def on_enter_susto(self):
        # lanzo escena 2: susto
        print("Lanzo escena2")
        # esperamos 3,5sg (correr al otro extremo)
        print("Corro al otro lado (tardo 3,5sg)")

    def on_enter_achantado(self):
        # lanzo escena 3: achantado
        print("Lanzo escena3")
        print('estoy achantado...')
        # comprueba si cerca == False
        time.sleep(3)

    def on_paso_peligro(self):
        # lanzo escena 4: vuelvo
        print("Lanzo escena4")
        print("Vuelvo...")
        # me voy al estado tranquilo

    def on_enter_vuelvo(self):
        # espero a que el video volver acabe
        print("estoy volviendo")
        # CUIDADO! para toda la ejecucion del programa mientras vuelvo
        for i in range(1, 6):
            time.sleep(1)
            print(i)
        # cambio estado tranquilo
        self.descanso()
