import cv2
import numpy as np
import pytesseract
import re
import json
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

def preProcessForContours(frame):

    imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5,5), 1)
    imgCanny = cv2.Canny(imgBlur, 100, 200)
    kernel = np.ones((5,5),np.uint8)
    imgDilate = cv2.dilate(imgCanny, kernel, iterations=1)
    imgThresh = cv2.erode(imgDilate, kernel, iterations=1)
    return imgThresh

def preprocessForOCR(image_roi):

    cinza = cv2.cvtColor(image_roi, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cinza = clahe.apply(cinza)
    _, binarizada = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    processada = cv2.morphologyEx(binarizada, cv2.MORPH_CLOSE, kernel)
    return processada

def identificar_tipo_placa_texto(placa):
    placa = placa.upper()
    padrao_mercosul = r'^[A-Z]{3}\d[A-Z]\d{2}$'
    padrao_cinza = r'^[A-Z]{3}\d{4}$'

    if re.match(padrao_mercosul, placa):
        return "Mercosul"
    elif re.match(padrao_cinza, placa):
        return "Cinza"
    else:
        return "Invalida"

placa_detectada = False 

while True:
    ret, frame = camera.read()

    if not ret:
        print("Erro: Não foi possível ler o frame.")
        break
    
    if placa_detectada:
        break 

    frame = cv2.resize(frame, (640, 480))
    
    imgContours = preProcessForContours(frame)
    
    contours, hierarchy = cv2.findContours(imgContours, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 2000 and area < 20000: 
            x, y, w, h = cv2.boundingRect(cnt)
            
           
            aspect_ratio = float(w) / h
            if aspect_ratio > 2.0 and aspect_ratio < 4.0: 
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
           
                margin = 5
                roi = frame[max(0, y - margin):min(frame.shape[0], y + h + margin), 
                            max(0, x - margin):min(frame.shape[1], x + w + margin)]
                
                if roi.shape[0] > 0 and roi.shape[1] > 0: 
                
                    processed_roi = preprocessForOCR(roi)
                    
       
                    config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                    
                    text = pytesseract.image_to_string(processed_roi, lang="eng", config=config)
                    text = text.strip().replace("\n", "").replace("\r", "").replace(" ", "")
                    text = ''.join(c for c in text if c.isalnum())
                    text = text.upper()
                    
                
                    if len(text) >= 7 and len(text) <= 8 and all(c.isalnum() for c in text): 
                        print(f"Placa Detectada: {text}")
                        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        placa_detectada = True 
                        break 
    
    cv2.imshow('FEED AO VIVO com OCR', frame)
    cv2.imshow('Pré-processamento de Contorno', imgContours)

    if placa_detectada:
        cv2.waitKey(0) 
        break 

    if cv2.waitKey(1) & 0xFF == 27: 
        break

tipo = identificar_tipo_placa_texto(text)
print(f"Placa Detectada: {text} - Tipo: {tipo}")

camera.release()
cv2.destroyAllWindows()