import math

import numpy as np
import cv2
import scipy.signal
from scipy.signal import butter,filtfilt
import matplotlib.pyplot as plt
import statistics


def detekcja_tetno(plane,no_of_frames,t):
    #dzielimy sygnal co 5 s i zapisujemy go do tablicy dwuwymiarowej
    print(" ")
    podzial = t*30
    ile_podzial = no_of_frames/podzial
    ile_podzial= math.floor((ile_podzial))
    ile_podzial=int(ile_podzial)
    ile_podzial= ile_podzial+1

    red_plane_po_podziale = [ [0] * podzial for _ in range(ile_podzial)]
    r=0;
    for i in range (ile_podzial):
        for j in range (podzial):
            if r < no_of_frames-1:
                red_plane_po_podziale[i][j] = plane[r]
                r=r+1
    #obliczamy ilosc pikow dla kazdego 5s fragmentu
    piki = []
    red_plane_5s =np.zeros(podzial)
    k=0
    for i in range (ile_podzial):

        for j in range (podzial):
            red_plane_5s[k] = red_plane_po_podziale[i][j]
            k=k+1
        if k>=(podzial-1):
            k=0

            info, _ = scipy.signal.find_peaks(red_plane_5s)
            info = len(info)
            piki.append(info)




    print(piki)
    #oblicczamy srednia ilosc pikow
    avg = sum(piki)/len(piki)
    #liczymy ilosc pikow na minute
    tentno = (avg/t) * 60
    print(tentno)



#odczyt wideo
cap = cv2.VideoCapture('71.mp4')

#odczyt liczby klatek
no_of_frames = int(cap.get(7))
print (no_of_frames)

#utworzenie pustych tablic w, ktorych beda zapisywane informacje o zmianach w kanalach
red_plane = np.zeros(no_of_frames)
blue_plane = np.zeros(no_of_frames)
green_plane = np.zeros(no_of_frames)

#zapis czasu do wykresow
time_list=[]
t=0

# czas klatki - 1/30 s
difference = 1/30

# do sredniej avg zapisujemy srednie odchylenie standardowe dla kazdego obszaru wideo
avg = []

#Wektor tablic zapisujacy caly film jednej zmiennej
frames=[]

#obliczanie obaszaru
podz_hd1= int(1920/6)
podz_hd2= int(1080/6)

#petla zapisujaca caly film w jednej zmiennej
for i in range(no_of_frames):
    _, frame = cap.read()
    frames.append(frame)



#odczyt filmu dla kazdej ramki, oraz obliczanie odchylenia standarodwego
for k in range(6):
    for j in range(6):

        for i in range(no_of_frames):


            fr=frames[i]
            #obliczanie obszaru ramki
            ramka = fr[(0+(j*podz_hd1)):(podz_hd1+(j*podz_hd1)),(0+(k*podz_hd2)):(podz_hd2+(k*podz_hd2))]
            #obliczanie sredniej wartosci  z kanalu czerwonego w ramce
            red_plane[i] = np.sum(ramka[:,:,2])/(podz_hd1*podz_hd2)

        #obliczanie odchylenia statystycznego dla kazdego obszaru i zapis do zmiennej avg
        odchyl=statistics.stdev(red_plane)

        avg.append(odchyl)




#znajdujemy obszar gdzie zmienia sie najwiecej
maximum= max(avg)
index = avg.index(maximum)
y = int(index/6)
if y==0:
 x = 0
else:
    x=index%y

# analizujemy film po raz ostani i zapisujemy informacje juz tylko dla konkretnego obszaru
for i in range(no_of_frames):
    fr = frames[i]
    ramka = fr[(0 + (x * podz_hd1)):(podz_hd1 + (x * podz_hd1)), (0 + (y * podz_hd2)):(podz_hd2 + (y * podz_hd2))]
    # calculating average red value in the frame
    red_plane[i] = np.sum(ramka[:, :, 2]) / (podz_hd1 * podz_hd2)
    blue_plane[i] = np.sum(ramka[:, :, 0]) / (podz_hd1 * podz_hd2)
    green_plane[i] = np.sum(ramka[:, :, 1]) / (podz_hd1 * podz_hd2)
    time_list.append(t)
    t = t+ difference

#Filtrowanie otrzymanego sygnalu
cutoff=3.62
nyq= 0.5 *58
order =2
data = red_plane
normal_cutoff = cutoff / nyq

b, a = butter(order, normal_cutoff, btype='low', analog=False)

y = filtfilt(b, a, data)

y1 = filtfilt(b, a, blue_plane)

y2 = filtfilt(b,a,green_plane)

#wywolanie funkcji do detekcji pulsu
print(" ")
print("Kanal czerwony")
detekcja_tetno(y,no_of_frames,5)
print(" ")
print("Kanal niebieski")
detekcja_tetno(y1,no_of_frames,5)
print(" ")
print("Kanal zielony")
detekcja_tetno(y2,no_of_frames,5)

#plot

#czerwony
figure, axis = plt.subplots(2, 2)
axis[0, 0].plot(time_list, red_plane)
axis[0, 0].set_title("Czerwony")

# niebieski
axis[0, 1].plot(time_list,blue_plane)
axis[0, 1].set_title("Niebieski")

# zielony
axis[1, 0].plot(time_list, green_plane)
axis[1, 0].set_title("Zielony")
plt.savefig("wykresy.png")







cap.release()