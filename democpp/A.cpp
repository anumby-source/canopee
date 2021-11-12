
#include <iostream>
#include <string>
using namespace std;

/*
Définition de la classe Variable qui transporte
 - le nom d'une variable
 - sa valeur

 Chaque objet Variable devra etre créé avec un nom mais sa valeur par défaut sera fixée au départ à zéro
 Ensuite la fonction "set" permet de changer sa valeur
*/
class Variable
{
    string name;
    int val;

public:
    Variable(String name)
    {
        this.name = name;
        this.val = 0;
    }
    void set(int value)
    {
        this.val = value;
    }
};

int main()
{
    cout << "hello " << endl;

    // on crée 2 objets "Variable"
    v1 = Variable("v1");
    v2 = Variable("v2");

    // Et on les initialise
    v1.set(12);
    v2.set(456);

    // Puis on crée un tableau de pointeurs sur des objets "Variables"
    vars = Variable*[10];

    // seuls les 2 premiers éléments du tableau sont associés à des objets réels
    vars[0] = &v1;
    vars[1] = &v2;

    // on peut accéder les objets "Variable" via leur pointeur
    vars[0]->set(789);

    // on va créer une base de données de Variables dont les noms sera "abc<n>"
    for (int i = 0; i++; i < 10)
    {
        vars[i] = &Variable("abc" + to_string(i));
        v->set(i);
    }

    return 0;
}
