class WebInterface:
    def get_html(self, params):
        html = f"""
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Robot Control Leonel</title>
    <style>
        body {{ text-align: center; padding: 20px; }}
        .btn {{ 
            width: 100px; height: 100px; 
            margin: 10px; font-size: 30px;
            background: #4CAF50; color: white;
            border: none; border-radius: 10px;
        }}
        .dir {{ background: #2196F3; }}
        input {{ 
            width: 80px; padding: 5px;
            margin: 5px; font-size: 16px;
        }}
    </style>
</head>
<body>
    <h2>Control Robot Leonel</h2>
    
    <div>
        <button class="btn" onmousedown="move(1)" onmouseup="move(0)">↑</button><br>
        <button class="btn dir" onmousedown="move(2)" onmouseup="move(0)">←</button>
        <button class="btn dir" onmousedown="move(3)" onmouseup="move(0)">→</button><br>
        <button class="btn" onmousedown="move(4)" onmouseup="move(0)">↓</button>
    </div>

    <div style="margin-top: 20px;">
        <h3>Ajustar PID</h3>
        <form action="/update" method="post">
            <div>Kp: <input type="number" name="kp" value="{params['kp']:.1f}" step="0.1"></div>
            <div>Ki: <input type="number" name="ki" value="{params['ki']:.2f}" step="0.01"></div>
            <div>Kd: <input type="number" name="kd" value="{params['kd']:.1f}" step="0.1"></div>
            <input type="submit" value="Actualizar" style="width: auto; background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin-top: 10px;">
        </form>
    </div>

    <script>
    function move(dir) {{
        fetch('/move', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
            body: 'dir=' + dir
        }});
    }}
    </script>
</body>
</html>
"""
        return html.encode('utf-8')

    def parse_request(self, request):
        try:
            req = request.decode()
            
            if "POST /move" in req:
                dir_str = req.split("dir=")[1].split()[0]
                return ("move", int(dir_str))
                
            if "POST /update" in req:
                data = req.split("\r\n\r\n")[1]
                params = {}
                for item in data.split("&"):
                    k, v = item.split("=")
                    params[k] = float(v)
                print("Actualizando PID:", params)
                return ("update", params)
                
        except Exception as e:
            print("Error en request:", e)
        return None
