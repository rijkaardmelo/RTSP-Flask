# import the necessary packages
from flask import Response, Flask
import threading
import cv2

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs are viewing the stream)
outputFrame = None
lock = threading.Lock()
 
# initialize a flask object
NVR = Flask(__name__)
 
source = "rtsp://camera-01:camera123@10.200.80.0:554"
camera = cv2.VideoCapture(source)

def stream(framecount):
    global outputFrame, lock
    if camera.isOpened():
        while True:
            _,frame = camera.read()
            if frame.shape:
                with lock:
                    outputFrame = frame.copy()
            else:
                continue 
    else:
        print('Não foi possível acessar a câmera!!!')

def generate():
    global outputFrame, lock
 
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # verificando se o frame de saída está disponível, 
            # caso contrário, pule a iteração do loop
            if outputFrame is None:
                continue
 
            # Codificando o frame no formato jpg
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
 
            # Verificando se o frame foi codificado com sucesso
            if not flag:
                continue
 
        # Frame de saída no formato de byte
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')

@NVR.route("/")
def video_feed():
    # Retornando a resposta(video) e com tipo de mídia específica
    return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':
    # Criando a thread
    t = threading.Thread(target=stream, args=(32,))
    # Executar a thread em segundo plano
    t.daemon = True
    # Inicilizando a thread
    t.start()
 
    # Inicializando flask app
    NVR.run(host="10.200.36.243", port="5000", debug=False,
        threaded=True, use_reloader=False)
 
# Liberar o ponteiro do fluxo de video
camera.release()
cv2.destroyAllWindows()