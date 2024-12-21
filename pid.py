class FuzzyPID:
    class FuzzyPID:
        def __init__(self):
            # Valores PID iniciales
            self.Kp = 30.0
            self.Ki = 0.0  # Comenzamos sin integral
            self.Kd = 50.0
            
            # Variables de control
            self.error_sum = 0
            self.last_error = 0
            
            print(f"\nPID iniciado con:")
            print(f"Kp = {self.Kp:.1f}")
            print(f"Ki = {self.Ki:.2f}")
            print(f"Kd = {self.Kd:.1f}")
        
        def set_values(self, kp=None, ki=None, kd=None):
            """Actualiza los valores PID"""
            if kp is not None: self.Kp = float(kp)
            if ki is not None: self.Ki = float(ki)
            if kd is not None: self.Kd = float(kd)
            
            # Reset integral
            self.error_sum = 0
            
            print(f"\nNuevos valores PID:")
            print(f"Kp = {self.Kp:.1f}")
            print(f"Ki = {self.Ki:.2f}")
            print(f"Kd = {self.Kd:.1f}")
        
        def update(self, error, delta_error):
            try:
                # Límites de error
                error = max(min(error, 20), -20)
                delta_error = max(min(delta_error, 15), -15)
                
                # Actualizar integral con límites
                if abs(error) < 1:  # Reset cerca del objetivo
                    self.error_sum = 0
                else:
                    self.error_sum = max(min(self.error_sum + error, 50), -50)
                
                # Calcular términos PID
                p_term = self.Kp * error
                i_term = self.Ki * self.error_sum
                d_term = self.Kd * delta_error
                
                # Calcular salida con límites
                output = p_term + i_term + d_term
                output = max(min(output, 200), -200)
                
                return output
                
            except Exception as e:
                print(f"Error PID: {e}")
                return 0
