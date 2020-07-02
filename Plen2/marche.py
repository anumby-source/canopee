# On importe Tkinter
from tkinter import *
import math


class Setup(object):
    def __init__(self):
        self.articulations = []
        self.membres = []

        self.echelle = 500
        self.articulation = 5
        self.sol_position = 0.1

        # On cree une fenetre, racine de notre interface
        self.fenetre = Tk()

        # Dans Fenetre nous allons creer un objet type Canvas qui se nomme zone_dessin
        # Nous donnons des valeurs aux proprietes "width", "height", "bg", "bd"
        self.zone_dessin = Canvas(self.fenetre, width=3*self.echelle, height=self.echelle, bg="white", bd=8)
        self.zone_dessin.pack()

        self.sol = Sol(setup=self)
        self.sol.pack(self.zone_dessin)
        self.sol.dessine()

        self.body = Body(setup=self, canvas=self.zone_dessin, sol=self.sol)

        start = Button(self.fenetre, text="Run", command=self.start)
        start.pack()
        stop = Button(self.fenetre, text="Stop", command=quit)
        stop.pack()

    def start(self):
        animation = Animation(setup=self, body=self.body)
        animation.run()
        self.body.redessine()

    def scale(self, x: float, y: float) -> (float, float):
        """
        on considère des données graphiques décrites entre [0..1]
        où le zéro se situe au niveau d'un sol fixe que l'on a positionné sur l'image
        """
        xx = x * self.echelle
        yy = (1 - (y + self.sol_position)) * self.echelle
        return xx, yy


class Dessin(object):
    def __init__(self):
        self.canvas = None

    def pack(self, canvas):
        if self.canvas is None:
            self.canvas = canvas


class Point(Dessin):
    """
    Classe classique pour des points graphiques
    """
    def __init__(self, setup: Setup, x: float, y: float, color="orange") -> None:
        Dessin.__init__(self)
        self.setup = setup
        self.x = x
        self.y = y
        self.canvas = None
        self.object = None
        self.color = color

    def dessine(self) -> None:
        x, y = self.setup.scale(self.x, self.y)
        if self.object is None:
            self.object = self.canvas.create_oval(x - self.setup.articulation,
                                                  y - self.setup.articulation,
                                                  x + self.setup.articulation,
                                                  y + self.setup.articulation,
                                                  fill=self.color, width=1)
        else:
            self.canvas.coords(self.object, [x - self.setup.articulation,
                                             y - self.setup.articulation,
                                             x + self.setup.articulation,
                                             y + self.setup.articulation])
        # coords = self.canvas.coords(self.object)
        # print("dessine art", coords)

    def move(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy
        # print("move", dx, dy, self.x, self.y)
        dx, dy = self.setup.scale(dx, dy)
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
    def __init__(self, setup: Setup, x0: float, y0: float, color="orange"):
        Point.__init__(self, setup=setup, x=x0, y=y0, color=color)
        setup.articulations.append(self)


class Membre(Dessin):
    def __init__(self, setup: Setup,
                 longueur: float,
                 art1: Articulation, art2: Articulation,
                 masse: float = 0.0, color="red"):
        Dessin.__init__(self)
        self.longueur = float(longueur)
        self.masse = masse
        self.art1 = art1
        self.art2 = art2
        self.canvas = None
        self.object = None
        self.color = color
        self.setup = setup
        self.setup.membres.append(self)

    def check_longueur(self) -> bool:
        longueur = math.sqrt((self.art1.x - self.art2.x)*(self.art1.x - self.art2.x) +
                             (self.art1.y - self.art2.y)*(self.art1.y - self.art2.y))
        return abs((longueur - self.longueur)/self.longueur) < 0.0001

    def dessine(self) -> None:
        ax, ay = self.setup.scale(self.art1.x, self.art1.y)
        bx, by = self.setup.scale(self.art2.x, self.art2.y)
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


class Sol(Dessin):
    def __init__(self, setup: Setup):
        Dessin.__init__(self)
        self.setup = setup

    def dessine(self) -> None:
        x, y = self.setup.scale(0, 0)
        self.canvas.create_line(0, y,
                                3*self.setup.echelle, y,
                                fill="green", width=3)


class Body(Dessin):
    def __init__(self, setup: Setup, canvas, sol: Sol):
        Dessin.__init__(self)
        self.canvas = canvas
        self.sol = sol
        self.setup = setup

        longueur_tibia = 0.25
        longueur_femur = 0.25
        longueur_tronc = 0.35

        self.tete = Articulation(setup=setup, x0=0.5, y0=longueur_tibia + longueur_femur + longueur_tronc)
        self.hanche = Articulation(setup=setup, x0=0.5, y0=longueur_tibia + longueur_femur)
        self.genou1 = Articulation(setup=setup, x0=0.5, y0=longueur_tibia)
        self.genou2 = Articulation(setup=setup, x0=0.5, y0=longueur_tibia, color="green")
        self.cheville1 = Articulation(setup=setup, x0=0.5, y0=0)
        self.cheville2 = Articulation(setup=setup, x0=0.5, y0=0)

        self.tronc = Membre(setup=setup, longueur=longueur_tronc, art1=self.tete, art2=self.hanche, masse=1)
        self.femur1 = Membre(setup=setup, longueur=longueur_femur, art1=self.hanche, art2=self.genou1, masse=1)
        self.tibia1 = Membre(setup=setup, longueur=longueur_tibia, art1=self.genou1, art2=self.cheville1, masse=1)
        self.femur2 = Membre(setup=setup, longueur=longueur_femur, art1=self.hanche, art2=self.genou2, masse=1,
                             color="blue")
        self.tibia2 = Membre(setup=setup, longueur=longueur_tibia, art1=self.genou2, art2=self.cheville2, masse=1,
                             color="blue")

        # repositionner les articulations pour vérifier les longueurs des membres
        # les chevilles sont toutes les deux au sol
        self.genou1.y = self.tibia1.longueur
        self.hanche.y = self.tibia1.longueur + self.femur1.longueur

        self.genou2.y = self.tibia2.longueur

        self.cdg = Articulation(setup=setup, x0=-0.1, y0=0, color="yellow")
        self.sustentation = Articulation(setup=setup, x0=-0.1, y0=0, color="green")

        """
        l1 = self.tibia1.check_longueur()
        l2 = self.femur1.check_longueur()
        l3 = self.tibia2.check_longueur()
        l4 = self.femur2.check_longueur()

        print("check", l1, l2, l3, l4)
        """

        self.pack(canvas)

    def pack(self, canvas):
        for a in self.setup.articulations:
            a.pack(self.canvas)

        for m in self.setup.membres:
            m.pack(self.canvas)

        self.sol.pack(self.canvas)

    def redessine(self) -> None:
        for _a in self.setup.articulations:
            _a.dessine()

        for _m in self.setup.membres:
            _m.dessine()

        self.sol.dessine()


def degres(angle: float) -> float:
    return angle*180/math.pi


class Animation(object):
    def __init__(self, setup: Setup, body: Body):
        self.setup = setup
        self.body = body
        self.phase = 1
        self.phi = 0
        self.theta = 0
        self.longueur_jambe = body.femur1.longueur + body.tibia1.longueur
        self.max_angle = 18
        self.phases = [self.phase1,
                       self.phase2,
                       self.phase3,
                       self.phase4,
                       self.phase5,
                       self.phase6]
        self.step = -0.02

        self.femur_avant = body.femur1
        self.genou_avant = body.genou1
        self.tibia_avant = body.tibia1
        self.cheville_avant = body.cheville1

        self.femur_arriere = body.femur2
        self.genou_arriere = body.genou2
        self.tibia_arriere = body.tibia2
        self.cheville_arriere = body.cheville2

    def log(self) -> None:
        print("phase{} phi={:.2f} "
              "h={:.4f},{:.4f} "
              "g1={:.4f},{:.4f} "
              "g2={:.4f},{:.4f} "
              "c1={:.4f},{:.4f} "
              "c2={:.4f},{:.4f} ".format(self.phase,
                                         degres(self.phi),
                                         self.body.hanche.x, self.body.hanche.y,
                                         self.body.genou1.x, self.body.genou1.y,
                                         self.body.genou2.x, self.body.genou2.y,
                                         self.body.cheville1.x, self.body.cheville1.y,
                                         self.body.cheville2.x, self.body.cheville2.y))

    def centre_de_gravite(self):
        masse = 0
        moment = 0
        for _m in self.setup.membres:
            if __name__ == '__main__':
                masse += _m.masse
                moment += _m.masse * (_m.art1.x + _m.art2.x) / 2
            position = moment / masse

        sustensation = (self.body.cheville1.x + self.body.cheville2.x) / 2
        print("équilibre ", position - sustensation)
        self.body.cdg.moveto(sustensation + position - sustensation, -0.1 )
        self.body.sustentation.moveto(sustensation, -0.1 )
        self.body.cdg.dessine()
        self.body.sustentation.dessine()

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

        # on lance la jambe_avant vers l'avant, tout en gardans jambe_arriere verticale => chevile_avant décolle du sol
        self.cheville_avant.rotate(self.body.hanche, -self.step)
        self.genou_avant.rotate(self.body.hanche, -self.step)

        return degres(self.phi) < self.max_angle

    """
    - on pivote sur la jambe_arriere dans le but de poser le pied_avant au sol
    - les 2 jambes restent droites
    """
    def phase2(self):
        self.phi += self.step
        # self.log()

        # on pivote tout l'ensemble autour de cheville2
        self.genou_arriere.rotate(self.cheville_arriere, self.step)
        self.body.hanche.rotate(self.cheville_arriere, self.step)
        self.body.tete.moveto(self.body.hanche.x, self.body.hanche.y + self.body.tronc.longueur)
        self.genou_avant.rotate(self.cheville_arriere, self.step)
        self.cheville_avant.rotate(self.cheville_arriere, self.step)

        # jusqu'à ce que self.cheville_avant touche le sol
        return self.cheville_avant.y > 0

    """
    - tout pivote autour du pied #1 qui reste fixe au sol
    - simultanément:
        - on avance le genou #2 vers l'avant 2x plus vite que la rotation de la hanche
        - le genou #2 fléchit vers l'arriere, soulevant le pied #2 du sol
    """
    def phase3(self):
        self.phi += self.step

        # tout tourne autour de chevile1 vers l'avance
        self.body.hanche.rotate(self.cheville_avant, self.step)
        self.body.tete.moveto(self.body.hanche.x, self.body.hanche.y + self.body.tronc.longueur)
        self.genou_avant.rotate(self.cheville_avant, self.step)
        self.genou_arriere.rotate(self.cheville_avant, self.step)
        self.cheville_arriere.rotate(self.cheville_avant, self.step)

        # la jambe2 rattrappe jambe1 => elle tourne 2x plus vite
        self.genou_arriere.rotate(self.body.hanche, -2*self.step)
        self.cheville_arriere.rotate(self.body.hanche, -2*self.step)

        # self.cheville_arriere reste fléchie en arriere pour décoller du sol
        self.cheville_arriere.rotate(self.genou_arriere, 2.5*self.step)

        return degres(self.phi) > -self.max_angle/2

    """
    - tout pivote autour du pied #1 qui reste fixe au sol
    - simultanément:
        - on avance le genou #2 vers l'avant 2x plus vite que la rotation de la hanche
        - le genou #2 fléchit vers l'avant, dans le but de reposer le pied #2 sur le sol
    """
    def phase4(self):
        self.phi += self.step

        # on continue le mouvement de l'ensemble comme phase3
        self.genou_avant.rotate(self.cheville_avant, self.step)
        self.body.hanche.rotate(self.cheville_avant, self.step)
        self.body.tete.moveto(self.body.hanche.x, self.body.hanche.y + self.body.tronc.longueur)
        self.genou_arriere.rotate(self.cheville_avant, self.step)
        self.cheville_arriere.rotate(self.cheville_avant, self.step)

        # la jambe2 rattrappe jambe1 => elle tourne 2x plus vite
        self.genou_arriere.rotate(self.body.hanche, -2*self.step)
        self.cheville_arriere.rotate(self.body.hanche, -2*self.step)

        # la self.cheville_arriere se redressse vers l'avant pour retrouver le contact vers le sol
        self.cheville_arriere.rotate(self.genou_arriere, -5.2*self.step)

        return degres(self.phi) > -self.max_angle

    """
    on va relancer le mouvement mais en échangeant les deux jambes
    """
    def phase5(self):
        if degres(self.phi) < -self.max_angle:
            self.phi = 0

        self.phi += self.step

        # tout tourne autour de chevile1 vers l'avance
        self.body.hanche.rotate(self.cheville_arriere, self.step)
        self.body.tete.moveto(self.body.hanche.x, self.body.hanche.y + self.body.tronc.longueur)
        self.genou_arriere.rotate(self.cheville_arriere, self.step)
        self.genou_avant.rotate(self.cheville_arriere, self.step)
        self.cheville_avant.rotate(self.cheville_arriere, self.step)

        # la jambe1 rattrappe jambe2 => elle tourne 2x plus vite
        self.genou_avant.rotate(self.body.hanche, -2 * self.step)
        self.cheville_avant.rotate(self.body.hanche, -2 * self.step)

        # self.cheville_avant reste fléchie en arriere pour décoller du sol
        self.cheville_avant.rotate(self.genou_avant, 2.5 * self.step)

        return degres(self.phi) > -self.max_angle

    def phase6(self):
        if degres(self.phi) < -self.max_angle:
            self.phi = 0

        self.phi += self.step

        # on continue le mouvement de l'ensemble comme phase5
        self.genou_arriere.rotate(self.cheville_arriere, self.step)
        self.body.hanche.rotate(self.cheville_arriere, self.step)
        self.body.tete.moveto(self.body.hanche.x, self.body.hanche.y + self.body.tronc.longueur)
        self.genou_avant.rotate(self.cheville_arriere, self.step)
        self.cheville_avant.rotate(self.cheville_arriere, self.step)

        # la jambe1 rattrappe jambe2 => elle tourne 2x plus vite
        self.genou_avant.rotate(self.body.hanche, -2 * self.step)
        self.cheville_avant.rotate(self.body.hanche, -2 * self.step)

        # la self.cheville_avant se redressse vers l'avant pour retrouver le contact vers le sol
        self.cheville_avant.rotate(self.genou_avant, -2.2 * self.step)

        return degres(self.phi) > -self.max_angle

    def reset(self):
        self.phi = 0
        g = self.genou_arriere
        c = self.cheville_arriere
        f = self.femur_arriere
        t = self.tibia_arriere

        self.genou_arriere = self.genou_avant
        self.cheville_arriere = self.cheville_avant
        self.femur_arriere = self.femur_avant
        self.tibia_arriere = self.tibia_avant

        self.genou_avant = g
        self.cheville_avant = c
        self.femur_avant = f
        self.tibia_avant = t

        # on réinitialise tout pour resychroniser mais sans changer la référence = chevilleself.g
        self.cheville_avant.moveto(self.cheville_avant.x, 0)
        self.cheville_arriere.moveto(self.cheville_arriere.x, 0)
        _a = (self.cheville_arriere.x - self.cheville_avant.x) / 2
        y = math.sqrt(self.longueur_jambe * self.longueur_jambe - _a * _a)
        self.body.hanche.moveto(self.cheville_avant.x + _a, y)
        self.body.tete.moveto(self.body.hanche.x, self.body.hanche.y + self.body.tronc.longueur)
        self.genou_avant.moveto(self.cheville_avant.x + _a / 2, y / 2)
        self.genou_arriere.moveto(self.cheville_arriere.x - _a / 2, y / 2)

    def run(self):
        phase = self.phases[self.phase - 1]
        if phase():
            self.body.redessine()
            self.setup.fenetre.after(100, self.run)
            # self.log()
            self.centre_de_gravite()
            return
        self.phase += 1
        print("------------------------------------------------------")
        if self.phase <= 6:
            self.setup.fenetre.after(1, self.run)
            return
        else:
            self.reset()
            self.phase = 5
            self.setup.fenetre.after(1, self.run)
            return


def main():
    setup = Setup()

    # On demarre la boucle Tkinter qui s'interompt quand on ferme la fenetre
    setup.fenetre.mainloop()


if __name__ == "__main__":
    main()
