# On importe Tkinter
from tkinter import *
import math

# On cree une fenetre, racine de notre interface
Fenetre = Tk()

échelle = 500
articulation = 5
sol_position = 0.1

articulations = []
membres = []


def scale(x: float, y: float) -> (float, float):
    """
    on considère des données graphiques décrites entre [0..1]
    où le zéro se situe au niveau d'un sol fixe que l'on a positionné sur l'image
    """
    xx = x * échelle
    yy = (1 - (y + sol_position)) * échelle
    return xx, yy


class Point(object):
    """
    Classe classique pour des points graphiques
    """
    def __init__(self, x: float, y: float, color="orange") -> None:
        self.x = x
        self.y = y
        self.canvas = None
        self.object = None
        self.color = color

    def pack(self, canvas) -> None:
        if self.canvas is None:
            self.canvas = canvas

    def dessine(self) -> None:
        x, y = scale(self.x, self.y)
        if self.object is None:
            self.object = self.canvas.create_oval(x - articulation,
                                                  y - articulation,
                                                  x + articulation,
                                                  y + articulation,
                                                  fill=self.color, width=1)
        else:
            self.canvas.coords(self.object, [x - articulation,
                                             y - articulation,
                                             x + articulation,
                                             y + articulation])
        # coords = self.canvas.coords(self.object)
        # print("dessine art", coords)

    def move(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy
        # print("move", dx, dy, self.x, self.y)
        dx, dy = scale(dx, dy)
        try:
            self.canvas.move(self.object, dx, dy)
        except:
            pass

    def moveto(self, x: float, y: float) -> None:
        dx = x - self.x
        dy = y - self.y
        self.move(dx, dy)

    def rotate(self, ref, angle: float) -> None:
        x = self.x - ref.x
        y = self.y - ref.y
        r = math.sqrt(x * x + y * y)
        try:
            _a = math.acos(x / r)
            if y < 0:
                _a = 2*math.pi - _a
            # print("ref=", ref.x, ref.y, "p=", self.x, self.y, "rel=", x, y, r, "a=", a*180/math.pi)

            _a += angle
            x = r * math.cos(_a) + ref.x
            y = r * math.sin(_a) + ref.y
            # print("a=", a*180/math.pi, "rel=", x, y)
            self.moveto(x, y)
        except:
            pass


class Articulation(Point):
    def __init__(self, x: float, y: float, color="orange"):
        Point.__init__(self, x=x, y=y, color=color)
        articulations.append(self)


class Membre(object):
    def __init__(self, longueur: float, _a: Articulation, _b: Articulation, color="red"):
        self.longueur = float(longueur)
        self.a = _a
        self.b = _b
        self.canvas = None
        self.object = None
        self.color = color
        membres.append(self)

    def check_longueur(self) -> bool:
        longueur = math.sqrt((self.a.x - self.b.x)*(self.a.x - self.b.x) +
                             (self.a.y - self.b.y)*(self.a.y - self.b.y))
        return abs((longueur - self.longueur)/self.longueur) < 0.0001

    def pack(self, canvas) -> None:
        if self.canvas is None:
            self.canvas = canvas

    def dessine(self) -> None:
        ax, ay = scale(self.a.x, self.a.y)
        bx, by = scale(self.b.x, self.b.y)
        if self.object is None:
            self.object = self.canvas.create_line(ax, ay,
                                                  bx, by,
                                                  fill=self.color, width=1)
        else:
            self.canvas.coords(self.object, [ax,
                                             ay,
                                             bx,
                                             by])
        # coords = self.canvas.coords(self.object)
        # print(coords)


class Sol(object):
    def __init__(self):
        pass

    def dessine(self) -> None:
        x, y = scale(0, 0)
        zone_dessin.create_line(0, y,
                                3*échelle, y,
                                fill="green", width=3)


def redessine() -> None:
    for _a in articulations:
        _a.dessine()

    for _m in membres:
        _m.dessine()

    sol.dessine()


def degrés(angle: float) -> float:
    return angle*180/math.pi


class Animation(object):
    def __init__(self):
        self.phase = 1
        self.phi = 0
        self.theta = 0
        self.longueur_jambe = fémur1.longueur + tibia1.longueur
        self.max_angle = 18
        self.phases = [self.phase1,
                       self.phase2,
                       self.phase3,
                       self.phase4,
                       self.phase5,
                       self.phase6]
        self.step = -0.02

        self.fémur_avant = fémur1
        self.genou_avant = genou1
        self.tibia_avant = tibia1
        self.cheville_avant = cheville1

        self.fémur_arrière = fémur2
        self.genou_arrière = genou2
        self.tibia_arrière = tibia2
        self.cheville_arrière = cheville2

    def log(self) -> None:
        print("phase{} phi={:.2f} "
              "h={:.4f},{:.4f} "
              "g1={:.4f},{:.4f} "
              "g2={:.4f},{:.4f} "
              "c1={:.4f},{:.4f} "
              "c2={:.4f},{:.4f} ".format(self.phase,
                                         degrés(self.phi),
                                         hanche.x, hanche.y,
                                         genou1.x, genou1.y,
                                         genou2.x, genou2.y,
                                         cheville1.x, cheville1.y,
                                         cheville2.x, cheville2.y))

    """
    Etat de départ:
    - les deux jambes sont verticales
    
    Première phase:
    - on avance la jambe_avant en avant en conservant la jambe strictement droite 
        jusqu'à atteindre un angle de max_angle
    - la hanche reste exactement à la position
    
    """
    def phase1(self):
        self.phi -= self.step

        self.log()

        # on lance la jambe_avant vers l'avant, tout en gardans jambe_arrière verticale => chevile_avant décolle du sol
        self.cheville_avant.rotate(hanche, -self.step)
        self.genou_avant.rotate(hanche, -self.step)

        return degrés(self.phi) < self.max_angle

    """
    - on pivote sur la jambe_arrière dans le but de poser le pied_avant au sol
    - les 2 jambes restent droites
    """
    def phase2(self):
        self.phi += self.step
        self.log()

        # on pivote tout l'ensemble autour de cheville2
        self.genou_arrière.rotate(self.cheville_arrière, self.step)
        hanche.rotate(self.cheville_arrière, self.step)
        self.genou_avant.rotate(self.cheville_arrière, self.step)
        self.cheville_avant.rotate(self.cheville_arrière, self.step)

        # jusqu'à ce que self.cheville_avant touche le sol
        return self.cheville_avant.y > 0

    """
    - tout pivote autour du pied #1 qui reste fixe au sol
    - simultanément:
        - on avance le genou #2 vers l'avant 2x plus vite que la rotation de la hanche
        - le genou #2 fléchit vers l'arrière, soulevant le pied #2 du sol
    """
    def phase3(self):
        self.phi += self.step

        self.log()

        # tout tourne autour de chevile1 vers l'avance
        hanche.rotate(self.cheville_avant, self.step)
        self.genou_avant.rotate(self.cheville_avant, self.step)
        self.genou_arrière.rotate(self.cheville_avant, self.step)
        self.cheville_arrière.rotate(self.cheville_avant, self.step)

        # la jambe2 rattrappe jambe1 => elle tourne 2x plus vite
        self.genou_arrière.rotate(hanche, -2*self.step)
        self.cheville_arrière.rotate(hanche, -2*self.step)

        # self.cheville_arrière reste fléchie en arrière pour décoller du sol
        self.cheville_arrière.rotate(self.genou_arrière, 2.5*self.step)

        return degrés(self.phi) > -self.max_angle/2

    """
    - tout pivote autour du pied #1 qui reste fixe au sol
    - simultanément:
        - on avance le genou #2 vers l'avant 2x plus vite que la rotation de la hanche
        - le genou #2 fléchit vers l'avant, dans le but de reposer le pied #2 sur le sol
    """
    def phase4(self):
        self.phi += self.step

        self.log()

        # on continue le mouvement de l'ensemble comme phase3
        self.genou_avant.rotate(self.cheville_avant, self.step)
        hanche.rotate(self.cheville_avant, self.step)
        self.genou_arrière.rotate(self.cheville_avant, self.step)
        self.cheville_arrière.rotate(self.cheville_avant, self.step)

        # la jambe2 rattrappe jambe1 => elle tourne 2x plus vite
        self.genou_arrière.rotate(hanche, -2*self.step)
        self.cheville_arrière.rotate(hanche, -2*self.step)

        # la self.cheville_arrière se redressse vers l'avant pour retrouver le contact vers le sol
        self.cheville_arrière.rotate(self.genou_arrière, -5.2*self.step)

        return degrés(self.phi) > -self.max_angle

    """
    on va relancer le mouvement mais en échangeant les deux jambes
    """
    def phase5(self):
        if degrés(self.phi) < -self.max_angle:
            self.phi = 0

        self.phi += self.step

        self.log()

        # tout tourne autour de chevile1 vers l'avance
        hanche.rotate(self.cheville_arrière, self.step)
        self.genou_arrière.rotate(self.cheville_arrière, self.step)
        self.genou_avant.rotate(self.cheville_arrière, self.step)
        self.cheville_avant.rotate(self.cheville_arrière, self.step)

        # la jambe1 rattrappe jambe2 => elle tourne 2x plus vite
        self.genou_avant.rotate(hanche, -2 * self.step)
        self.cheville_avant.rotate(hanche, -2 * self.step)

        # self.cheville_avant reste fléchie en arrière pour décoller du sol
        self.cheville_avant.rotate(self.genou_avant, 2.5 * self.step)

        return degrés(self.phi) > -self.max_angle

    def phase6(self):
        if degrés(self.phi) < -self.max_angle:
            self.phi = 0

        self.phi += self.step

        self.log()

        # on continue le mouvement de l'ensemble comme phase5
        self.genou_arrière.rotate(self.cheville_arrière, self.step)
        hanche.rotate(self.cheville_arrière, self.step)
        self.genou_avant.rotate(self.cheville_arrière, self.step)
        self.cheville_avant.rotate(self.cheville_arrière, self.step)

        # la jambe1 rattrappe jambe2 => elle tourne 2x plus vite
        self.genou_avant.rotate(hanche, -2 * self.step)
        self.cheville_avant.rotate(hanche, -2 * self.step)

        # la self.cheville_avant se redressse vers l'avant pour retrouver le contact vers le sol
        self.cheville_avant.rotate(self.genou_avant, -2.2 * self.step)

        return degrés(self.phi) > -self.max_angle

    def reset(self):
        self.phi = 0
        g = self.genou_arrière
        c = self.cheville_arrière
        f = self.fémur_arrière
        t = self.tibia_arrière

        self.genou_arrière = self.genou_avant
        self.cheville_arrière = self.cheville_avant
        self.fémur_arrière = self.fémur_avant
        self.tibia_arrière = self.tibia_avant

        self.genou_avant = g
        self.cheville_avant = c
        self.fémur_avant = f
        self.tibia_avant = t

        # on réinitialise tout pour resychroniser mais sans changer la référence = chevilleself.g
        self.cheville_avant.moveto(self.cheville_avant.x, 0)
        self.cheville_arrière.moveto(self.cheville_arrière.x, 0)
        _a = (self.cheville_arrière.x - self.cheville_avant.x) / 2
        y = math.sqrt(self.longueur_jambe * self.longueur_jambe - _a * _a)
        hanche.moveto(self.cheville_avant.x + _a, y)
        self.genou_avant.moveto(self.cheville_avant.x + _a / 2, y / 2)
        self.genou_arrière.moveto(self.cheville_arrière.x - _a / 2, y / 2)

    def run(self):
        phase = self.phases[self.phase - 1]
        if phase():
            redessine()
            Fenetre.after(100, self.run)
            return
        self.phase += 1
        print("------------------------------------------------------")
        if self.phase <= 6:
            Fenetre.after(1, self.run)
            return
        else:
            self.reset()
            self.phase = 5
            Fenetre.after(1, self.run)
            return


# Dans Fenetre nous allons creer un objet type Canvas qui se nomme zone_dessin
# Nous donnons des valeurs aux proprietes "width", "height", "bg", "bd"
zone_dessin = Canvas(Fenetre, width=3*échelle, height=échelle, bg="white", bd=8)
zone_dessin.pack()  # Affiche le Canvas

sol = Sol()
sol.dessine()

hanche = Articulation(0.5, 0.60)
genou1 = Articulation(0.5, 0.30)
genou2 = Articulation(0.5, 0.30, color="green")
cheville1 = Articulation(0.5, 0)
cheville2 = Articulation(0.5, 0)

fémur1 = Membre(0.25, hanche, genou1)
tibia1 = Membre(0.25, genou1, cheville1)
fémur2 = Membre(0.25, hanche, genou2, color="blue")
tibia2 = Membre(0.25, genou2, cheville2, color="blue")

for a in articulations:
    a.pack(zone_dessin)

for m in membres:
    m.pack(zone_dessin)

# repositionner les articulations pour vérifier les longueurs des membres
# les chevilles sont toutes les deux au sol
genou1.y = tibia1.longueur
hanche.y = tibia1.longueur + fémur1.longueur

genou2.y = tibia2.longueur

l1 = tibia1.check_longueur()
l2 = fémur1.check_longueur()
l3 = tibia2.check_longueur()
l4 = fémur2.check_longueur()

print("check", l1, l2, l3, l4)


def start():
    animation = Animation()
    animation.run()
    redessine()


def stop():
    quit()


Start = Button(Fenetre, text="Run", command=start)
Start.pack()
Stop = Button(Fenetre, text="Stop", command=stop)
Stop.pack()

# On demarre la boucle Tkinter qui s'interompt quand on ferme la fenetre
Fenetre.mainloop()
