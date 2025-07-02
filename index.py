import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

imagem = cv2.imread("placa1.jpg")

if imagem is None:
    print("Erro ao carregar a imagem.")
else:

    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cinza = clahe.apply(cinza)
 
    _, binarizada = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    processada = cv2.morphologyEx(binarizada, cv2.MORPH_CLOSE, kernel)
    
    cv2.imshow("Pré-processada", processada)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    
    texto = pytesseract.image_to_string(processada, lang="eng", config=config)
    print("Texto detectado:")
    print(texto.strip())