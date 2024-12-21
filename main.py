from machine import Pin, I2C, PWM
import math
import socket
from time import sleep, ticks_ms
from pid import FuzzyPID
from web import WebInterface

# Constantes
MPU_ADDR = 0x68
ACCEL_XOUT_H = 0x3B
PWR_MGMT_1 = 0x6B

class Robot:
    def __init__(self):
        # Debug
        self.debug = True
        self.last_print = ticks_ms()
        self.cycle_count = 0
        
        try:
            # Hardware setup
            self.setup_mpu()
            self.setup_motors()
            self.setup_server()
            
            # Control
            self.pid = FuzzyPID()
            self.web = WebInterface()
            
            # Variables de control
            self.angle_offset = -2
            self.last_error = 0
            self.target_speed = 0
            self.target_turn = 0
            self.last_angle = 0
            
            print("Robot iniciado correctamente")
        except Exception as e:
            print(f"Error en init: {e}")
            raise

    def setup_mpu(self):
        try:
            self.i2c = I2C(0, scl=Pin(22), sda=Pin(21))
            self.i2c.writeto_mem(MPU_ADDR, PWR_MGMT_1, bytes([0]))
            sleep(0.1)
            print("MPU6050 OK")
        except Exception as e:
            print(f"Error MPU6050: {e}")
            raise

    def setup_motors(self):
        try:
            # Configurar PWM a 1000Hz
            self.pwm_freq = 1000
            self.max_duty = 1023
            
            # Motor izquierdo
            self.motor_a1 = PWM(Pin(25), freq=self.pwm_freq)
            self.motor_a2 = PWM(Pin(26), freq=self.pwm_freq)
            
            # Motor derecho
            self.motor_b1 = PWM(Pin(32), freq=self.pwm_freq)
            self.motor_b2 = PWM(Pin(33), freq=self.pwm_freq)
            
            # Inicializar a 0
            self.motor_a1.duty(0)
            self.motor_a2.duty(0)
            self.motor_b1.duty(0)
            self.motor_b2.duty(0)
            
            print("Motores OK")
        except Exception as e:
            print(f"Error motores: {e}")
            raise

    def setup_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(('0.0.0.0', 80))
            self.socket.listen(1)
            self.socket.setblocking(False)
            print("Servidor web iniciado")
        except Exception as e:
            print(f"Error servidor web: {e}")

    def read_angle(self):
        try:
            data = self.i2c.readfrom_mem(MPU_ADDR, ACCEL_XOUT_H, 6)
            ax = (data[0] << 8 | data[1])
            ay = (data[2] << 8 | data[3])
            
            if ax & 0x8000: ax = -((65535 - ax) + 1)
            if ay & 0x8000: ay = -((65535 - ay) + 1)
            
            angle = math.atan2(ay, ax) * 180/math.pi
            
            # Filtro simple para ruido
            angle = 0.8 * self.last_angle + 0.2 * angle
            self.last_angle = angle
            
            return angle
        except Exception as e:
            self.log_debug(f"Error leyendo ángulo: {e}")
            return self.last_angle

    def control_motors(self, output):
        try:
            # Si hay un movimiento manual activo, no interferir
            if self.target_speed != 0 or self.target_turn != 0:
                return
                
            # Control normal de balance
            left_speed = output
            right_speed = output
            
            # Limitar velocidad
            max_speed = 80
            left_speed = max(min(left_speed, max_speed), -max_speed)
            right_speed = max(min(right_speed, max_speed), -max_speed)
            
            # Convertir a duty cycle
            left_duty = abs(int(left_speed * self.max_duty / 255))
            right_duty = abs(int(right_speed * self.max_duty / 255))
            
            # Control motor izquierdo
            if left_speed > 0:
                self.motor_a1.duty(left_duty)
                self.motor_a2.duty(0)
            else:
                self.motor_a1.duty(0)
                self.motor_a2.duty(left_duty)
            
            # Control motor derecho
            if right_speed > 0:
                self.motor_b1.duty(right_duty)
                self.motor_b2.duty(0)
            else:
                self.motor_b1.duty(0)
                self.motor_b2.duty(right_duty)
            
        except Exception as e:
            self.log_debug(f"Error en motores: {e}")
            # Intentar detener motores en caso de error
            try:
                self.motor_a1.duty(0)
                self.motor_a2.duty(0)
                self.motor_b1.duty(0)
                self.motor_b2.duty(0)
            except:
                pass

    def handle_move(self, direction):
        print(f"Movimiento: {direction}")  # Debug
        
        if direction == 1:      # Adelante
            self.target_speed = 50  # Aumentado para más velocidad
            self.target_turn = 0
            print("Moviendo adelante")
            
        elif direction == 2:    # Izquierda
            self.target_speed = 0
            self.target_turn = -50  # Aumentado para giro más pronunciado
            print("Moviendo izquierda")
            
        elif direction == 3:    # Derecha
            self.target_speed = 0
            self.target_turn = 50   # Aumentado para giro más pronunciado
            print("Moviendo derecha")
            
        elif direction == 4:    # Atrás
            self.target_speed = -50  # Aumentado para más velocidad
            self.target_turn = 0
            print("Moviendo atrás")
            
        else:                   # Parar (cuando se suelta el botón)
            self.target_speed = 0
            self.target_turn = 0
            print("Detenido")
        
        # Control directo de motores para movimiento inmediato
        try:
            output = 0  # Reset output para movimiento directo
            
            # Calcular velocidades
            left_speed = self.target_speed + self.target_turn
            right_speed = self.target_speed - self.target_turn
            
            # Convertir a duty cycle
            left_duty = abs(int(left_speed * self.max_duty / 255))
            right_duty = abs(int(right_speed * self.max_duty / 255))
            
            # Control motor izquierdo
            if left_speed > 0:
                self.motor_a1.duty(left_duty)
                self.motor_a2.duty(0)
            else:
                self.motor_a1.duty(0)
                self.motor_a2.duty(left_duty)
            
            # Control motor derecho
            if right_speed > 0:
                self.motor_b1.duty(right_duty)
                self.motor_b2.duty(0)
            else:
                self.motor_b1.duty(0)
                self.motor_b2.duty(right_duty)
                
        except Exception as e:
            print(f"Error en control de motores: {e}")

    def handle_pid_update(self, params):
        try:
            # Usar el método set_values del PID
            self.pid.set_values(
                kp=params.get('kp'),
                ki=params.get('ki'),
                kd=params.get('kd')
            )
        except Exception as e:
            print(f"Error actualizando PID: {e}")

    def handle_web_request(self):
        try:
            conn, addr = self.socket.accept()
            request = conn.recv(1024)
            
            result = self.web.parse_request(request)
            if result:
                action, data = result
                if action == 'move':
                    self.handle_move(data)
                elif action == 'update':
                    self.handle_pid_update(data)
            
            # Generar HTML con los valores actuales
            response = self.web.get_html({
                'kp': self.pid.Kp,
                'ki': self.pid.Ki,
                'kd': self.pid.Kd
            })
            
            # La respuesta ya viene codificada desde get_html
            conn.send(response)
            conn.close()
            
        except OSError as e:
            if e.args[0] != 11:  # Ignorar EAGAIN
                print("Error web:", e)
        except Exception as e:
            print("Error web:", e)

    def balance_loop(self):
        print("Iniciando loop de balance")
        
        while True:
            try:
                # Lectura y control
                angle = self.read_angle()
                error = angle - self.angle_offset
                delta_error = error - self.last_error
                
                # PID
                output = self.pid.update(error, delta_error)
                
                # Control motores
                self.control_motors(output)
                
                self.last_error = error
                
                # Debug cada 100ms
                now = ticks_ms()
                if now - self.last_print >= 100:
                    print(f"Angle: {angle:6.1f}° Err: {error:6.1f}° Out: {output:6.1f}")
                    self.last_print = now
                
                # Manejar peticiones web
                self.handle_web_request()
                
                sleep(0.01)  # 10ms loop
                
            except Exception as e:
                print(f"Error en loop: {e}")
                sleep(0.1)

def main():
    try:
        robot = Robot()
        robot.balance_loop()
    except KeyboardInterrupt:
        print("\nDetenido por usuario")
    except Exception as e:
        print(f"Error principal: {e}")
    finally:
        # Limpieza
        try:
            robot.motor_a1.deinit()
            robot.motor_a2.deinit()
            robot.motor_b1.deinit()
            robot.motor_b2.deinit()
        except:
            pass

if __name__ == '__main__':
    main()
