from fr import NOTE, P, Q, R, S, TABLE, UL, Book

b = Book("qualifier")
REF = "Repère : _Grammaire progressive du français_, chapitre {} (p. {})."

# ================================================================ chapitre 12
c = b.chapter(12, "L'adjectif (2) : la place de l'adjectif", focus=[
    P("En français, la plupart des adjectifs se placent **après** le nom, mais une dizaine d'adjectifs très fréquents se placent **avant**, "
      "et quelques-uns changent de sens selon leur place (_un grand homme / un homme grand_). C'est un marqueur de niveau B2."),
    P(REF.format(12, 54)),
], los={
    "a": "Placer l'adjectif avant ou après le nom.",
    "b": "Employer les formes _bel, nouvel, vieil_ et les adjectifs qui changent de sens selon leur place.",
})
c.module(1, "La place de l'adjectif", sections=[
    ("a", [
        P("**Après le nom** (cas général) : couleurs, nationalités, formes, adjectifs longs ou dérivés de verbes : _une voiture **rouge**, un film **italien**, une table **ronde**, un texte **intéressant**_."),
        P("**Avant le nom** : adjectifs courts et fréquents : **beau, joli, bon, mauvais, grand, petit, gros, jeune, vieux, nouveau, long, haut, premier, dernier, autre** : "
          "_un **petit** appartement, une **bonne** idée, la **première** fois_."),
        NOTE("Devant un adjectif pluriel placé avant le nom, _des_ devient **de** à l'écrit soigné : _**de** jolies maisons, **de** bons résultats_."),
    ]),
    ("b", [
        P("Devant un nom masculin à voyelle ou _h_ muet : **beau → bel, nouveau → nouvel, vieux → vieil** : _un **bel** appartement, un **nouvel** emploi, un **vieil** homme_."),
        TABLE(["Avant le nom", "Après le nom"],
              ["un **grand** homme (célèbre)", "un homme **grand** (de grande taille)"], ["un **ancien** élève (d'avant)", "un meuble **ancien** (vieux)"],
              ["mon **propre** appartement (à moi)", "un appartement **propre** (pas sale)"], ["un **pauvre** homme (malheureux)", "un homme **pauvre** (sans argent)"],
              ["la **dernière** semaine (d'une série)", "la semaine **dernière** (passée)"], ["un **seul** enfant (un unique)", "un enfant **seul** (isolé)"],
              ["un **cher** ami (aimé)", "un repas **cher** (coûteux)"]),
    ]),
], chain=[
    ("assumption", "L'adjectif se place normalement après le nom en français."),
    ("mechanism", "Une quinzaine d'adjectifs courts et fréquents se placent avant ; _beau, nouveau, vieux_ deviennent _bel, nouvel, vieil_ devant voyelle."),
    ("result", "Certains adjectifs changent de sens selon leur place : avant = sens figuré ou subjectif, après = sens propre."),
], why="Bien placer l'adjectif (et jouer sur _ancien, propre, dernier_) montre une maîtrise fine que les correcteurs valorisent.",
  look=["la longueur et le type d'adjectif", "la première lettre du nom (voyelle ?)", "le sens voulu (propre ou figuré)"],
  traps=["*_un nouveau appartement_", "*_une rouge voiture_", "_la semaine dernière_ / _la dernière semaine_"],
  distractors=["l'adjectif mal placé", "_beau_ au lieu de _bel_ devant voyelle", "le sens de l'autre place"],
  questions=[
    Q("a", 1, "form", "Ils ont acheté ___ dans le centre-ville.", ("un petit appartement", "_petit_ se place avant le nom."),
      [("un appartement petit", "_petit_ se place normalement avant le nom."), ("un petit appartements", "_appartement_ est au singulier.")]),
    Q("a", 1, "form", "Nous avons loué ___ pour le week-end.", ("une voiture électrique", "Adjectif de type, long → après le nom."),
      [("une électrique voiture", "_électrique_ se place après le nom."), ("une électrique", "Il manque le nom.")]),
    Q("a", 2, "form", "Le quartier compte ___ maisons du XVIIIe siècle.", ("de belles", "Adjectif pluriel avant le nom → _de_."),
      [("des belles", "À l'écrit soigné, _des_ devient _de_ devant un adjectif antéposé."), ("de beaux", "_maison_ est féminin.")]),
    Q("b", 1, "form", "Il vient de trouver un ___ emploi dans une start-up.", ("nouvel", "Devant voyelle → _nouvel_."),
      [("nouveau", "Devant une voyelle, _nouveau_ devient _nouvel_."), ("nouvelle", "_emploi_ est masculin.")]),
    Q("b", 2, "form", "Un ___ homme attendait sur le quai.", ("vieil", "Devant _h_ muet → _vieil_."),
      [("vieux", "Devant voyelle ou _h_ muet → _vieil_."), ("vieille", "_homme_ est masculin.")]),
    Q("b", 2, "conceptual", "Victor Hugo est ___ : tout le monde le connaît.", ("un grand homme", "Avant le nom, _grand_ = célèbre, important."),
      [("un homme grand", "Après le nom, _grand_ = de grande taille."), ("un homme grandi", "Ce n'est pas le sens voulu.")]),
    Q("b", 2, "conceptual", "Je n'ai plus de colocataire : j'ai enfin ___.", ("mon propre appartement", "Avant le nom, _propre_ = à moi."),
      [("mon appartement propre", "Après le nom, _propre_ = pas sale."), ("mon appartement seul", "_seul_ après le nom = isolé.")]),
    Q("b", 3, "conceptual", "Je l'ai vu ___ (il y a sept jours).", ("la semaine dernière", "Après le nom, _dernière_ = passée, précédente."),
      [("la dernière semaine", "Avant le nom = la dernière d'une série (_la dernière semaine de juin_)."), ("la semaine prochaine", "C'est le futur.")]),
    Q("b", 3, "conceptual", "Paul est un ___ du lycée Victor-Duruy.", ("ancien élève", "Avant le nom, _ancien_ = qui l'était avant."),
      [("élève ancien", "Après le nom, _ancien_ = vieux."), ("vieil élève", "_vieil_ = âgé, pas _qui l'était autrefois_.")]),
  ],
  cards=[R("bel-nouvel", "b", "Bel, nouvel, vieil", "Beau, nouveau, vieux devant un nom masculin à voyelle ?", "**bel, nouvel, vieil** : _un bel arbre, un nouvel ami, un vieil homme_."),
         R("sens-place", "b", "Adjectifs à double sens", "grand / ancien / propre / dernier avant et après le nom ?",
           "Avant : sens figuré (_un grand homme, mon ancien patron, ma propre voiture, la dernière fois_). Après : sens propre (_un homme grand, un meuble ancien, une voiture propre, l'an dernier_).")])

# ================================================================ chapitre 15
c = b.chapter(15, "Les indéfinis", focus=[
    P("Les indéfinis (_chaque, tout, quelques, plusieurs, aucun, quelqu'un, rien…_) expriment une quantité ou une identité vague. "
      "Ils sont essentiels pour généraliser ou nuancer dans un texte argumentatif : _**certains** pensent que… ; **aucune** solution n'est parfaite_."),
    P(REF.format(15, 68)),
], los={
    "a": "Employer les adjectifs indéfinis (chaque, tout, quelques, plusieurs, certains, aucun).",
    "b": "Employer les pronoms indéfinis (chacun, quelqu'un, quelque chose, personne, rien, d'autres).",
})
c.module(1, "Adjectifs et pronoms indéfinis", sections=[
    ("a", [
        UL("**Chaque** + nom singulier : _**chaque** jour_ (jamais au pluriel).",
           "**Tout / toute / tous / toutes** + article + nom : _**tout le** monde, **toute la** journée, **tous les** jours, **toutes les** semaines_.",
           "**Quelques** (un petit nombre), **plusieurs** (plus de deux, invariable), **certains / certaines** (une partie) + nom pluriel.",
           "**Aucun / aucune** + nom singulier + **ne** : _**Aucun** candidat **n'**a réussi._"),
        NOTE("_Tout_ adverbe (= très, complètement) s'accorde seulement devant un adjectif féminin commençant par une consonne : _elle est **toute** petite_, mais _elles sont **tout** heureuses_."),
    ]),
    ("b", [
        TABLE(["Affirmation", "Négation"],
              ["quelqu'un", "**ne … personne** / **personne ne**"], ["quelque chose", "**ne … rien** / **rien ne**"], ["quelque part", "**ne … nulle part**"],
              ["tous / chacun", "**aucun(e) … ne**"]),
        UL("**Chacun / chacune** (singulier) : _**Chacun** a sa chance._", "**Tous** (pronom, on prononce le _s_) : _Ils sont **tous** venus._",
           "**Quelque chose de** + adjectif masculin : _quelque chose **d'intéressant**_ ; _rien **de nouveau**_."),
    ]),
], chain=[
    ("assumption", "Les indéfinis désignent une quantité ou une identité qu'on ne précise pas."),
    ("mechanism", "_Chaque, aucun, chacun_ sont singuliers ; _quelques, plusieurs, certains, tous_ sont pluriels ; _aucun, personne, rien_ demandent _ne_."),
    ("result", "_Quelque chose / rien_ se complètent par _de_ + adjectif masculin."),
], why="Généraliser avec précision (_certains_, _la plupart_, _aucun_) évite les affirmations trop absolues, défaut fréquent des essais.",
  look=["singulier ou pluriel après l'indéfini", "une négation (_ne_) obligatoire"],
  traps=["*_chaques jours_", "*_personne a compris_ (sans _ne_)", "*_quelque chose intéressant_ (sans _de_)"],
  distractors=["un indéfini pluriel avec un nom singulier", "l'oubli de _ne_ ou de _de_"],
  questions=[
    Q("a", 1, "form", "Je vais à la piscine ___ semaine.", ("chaque", "_chaque_ + singulier."), [("chaques", "_chaque_ ne prend jamais de _s_."), ("toutes", "_toutes_ demande l'article : _toutes les semaines_.")]),
    Q("a", 1, "form", "Il a travaillé ___ journée sur ce dossier.", ("toute la", "_tout_ + article + nom : _toute la journée_."),
      [("toute", "Il faut l'article : _toute la journée_."), ("chaque", "_chaque journée_ ne donne pas le sens de durée.")]),
    Q("a", 2, "form", "___ étudiant n'a rendu son devoir en retard.", ("Aucun", "_aucun_ + singulier + _ne_."), [("Aucuns", "_aucun_ reste au singulier."), ("Plusieurs", "_plusieurs_ est pluriel et ne s'emploie pas avec _ne_ seul.")]),
    Q("a", 2, "form", "___ experts doutent de l'efficacité de cette mesure.", ("Certains", "_certains_ + nom pluriel (une partie)."),
      [("Chaque", "_chaque_ + singulier."), ("Aucun", "_aucun_ demande _ne_ et le singulier.")]),
    Q("a", 3, "form", "Les deux enfants étaient ___ contents de leur cadeau.", ("tout", "Adverbe devant un adjectif masculin → invariable."),
      [("tous", "Ici, _tout_ = _très_ (adverbe) : invariable devant un adjectif masculin."), ("toute", "_enfants_ et _contents_ sont masculins.")]),
    Q("b", 1, "form", "Il y a quelqu'un ? — Non, il n'y a ___.", ("personne", "Négation de _quelqu'un_ → _ne … personne_."),
      [("rien", "_rien_ est la négation de _quelque chose_."), ("aucun", "_aucun_ demande un nom ou une reprise.")]),
    Q("b", 2, "form", "___ ne s'est passé pendant ton absence.", ("Rien", "Négation de _quelque chose_ en position sujet → _rien ne_."),
      [("Personne", "_personne_ désigne des gens, pas des événements."), ("Quelque chose", "Il y a _ne_ : il faut une négation.")]),
    Q("b", 2, "form", "Tu as appris quelque chose ___ pendant la conférence ?", ("d'intéressant", "_quelque chose de_ + adjectif masculin."),
      [("intéressant", "Il faut _de_ : _quelque chose d'intéressant_."), ("d'intéressante", "L'adjectif reste au masculin.")]),
    Q("b", 2, "form", "Les candidats ont tous reçu une réponse : ___ a été convoqué à un entretien.", ("chacun", "_chacun_ (singulier) = chaque candidat."),
      [("chaque", "_chaque_ doit être suivi d'un nom."), ("tous", "_tous_ demande un verbe au pluriel (_ont été convoqués_).")]),
  ],
  cards=[R("indefinis-neg", "b", "Indéfinis et négation", "Négation de quelqu'un / quelque chose / quelque part ?", "ne … **personne** ; ne … **rien** ; ne … **nulle part**.",
           examples=["Personne n'est venu. Rien ne marche."], mistake="Oublier _ne_ à l'écrit."),
         R("chaque-tout", "a", "Chaque, tout, plusieurs", "chaque / tous les / plusieurs : nombre ?", "**chaque** + singulier ; **tous les / toutes les** + pluriel ; **plusieurs** (invariable) + pluriel.")])

# ================================================================ chapitre 18
c = b.chapter(18, "L'adverbe", focus=[
    P("L'adverbe modifie un verbe, un adjectif ou une phrase. Les adverbes en _-ment_ permettent de nuancer (_probablement, nettement, notamment_) : "
      "ils enrichissent beaucoup une production écrite."),
    P(REF.format(18, 82)),
], los={
    "a": "Distinguer l'adverbe de l'adjectif (_bon / bien, mauvais / mal_) et placer l'adverbe.",
    "b": "Former les adverbes en _-ment_ (-amment, -emment).",
    "c": "Employer les adverbes de temps et de lieu courants.",
})
c.module(1, "L'adverbe et l'adjectif", sections=[
    ("a", [
        P("L'**adjectif** qualifie un nom (il s'accorde) ; l'**adverbe** modifie un verbe (il est invariable) : _un **bon** repas / elle cuisine **bien** ; un **mauvais** film / il chante **mal**_."),
        P("**Place** : après le verbe conjugué ; aux temps composés, les adverbes courts (_bien, mal, déjà, encore, beaucoup, trop, toujours_) se placent **entre l'auxiliaire et le participe** : "
          "_Il a **bien** travaillé. J'ai **déjà** lu ce livre._"),
        NOTE("Quelques adjectifs servent d'adverbes, invariables, dans des expressions : _parler **fort**, coûter **cher**, sentir **bon**, travailler **dur**, voir **clair**_."),
    ]),
    ("b", [
        P("**Formation** : féminin de l'adjectif + **-ment** : _lent → lente → lente**ment**, heureux → heureuse**ment**_. Adjectif terminé par une voyelle : masculin + _-ment_ : _vrai → vrai**ment**, poli → poli**ment**_."),
        TABLE(["Adjectif", "Adverbe", "Prononciation"], ["-ant : constant, courant", "**-amment** : constamment, couramment", "[amɑ̃]"],
              ["-ent : évident, récent, fréquent", "**-emment** : évidemment, récemment, fréquemment", "[amɑ̃] aussi"]),
        NOTE("Exceptions : _gentil → gentiment, bref → brièvement, précis → précisément, énorme → énormément, lent → lentement_ (pas *_lentamment_)."),
    ]),
    ("c", [
        UL("**Temps** : _déjà / pas encore, toujours / jamais, souvent, parfois, rarement, tout de suite, bientôt, autrefois, désormais_ (= à partir de maintenant).",
           "**Lieu** : _ici, là, là-bas, partout, ailleurs, dedans / dehors, dessus / dessous, devant / derrière, loin / près_."),
    ]),
], chain=[
    ("assumption", "L'adjectif qualifie un nom et s'accorde ; l'adverbe modifie un verbe et ne s'accorde pas."),
    ("mechanism", "On forme l'adverbe avec le féminin + _-ment_, ou _-amment / -emment_ pour les adjectifs en _-ant / -ent_."),
    ("result", "Aux temps composés, l'adverbe court se glisse entre l'auxiliaire et le participe passé."),
], why="Les adverbes de nuance (_probablement, nettement, notamment, désormais_) sont des marqueurs de niveau B2.",
  look=["ce que le mot modifie (nom ou verbe ?)", "la terminaison de l'adjectif (-ant, -ent ?)", "un temps composé"],
  traps=["*_il parle bon français_", "*_évidamment_", "*_il a travaillé bien_"],
  distractors=["l'adjectif à la place de l'adverbe", "_-amment / -emment_ inversés", "l'adverbe mal placé"],
  questions=[
    Q("a", 1, "form", "Elle parle très ___ l'espagnol.", ("bien", "On modifie le verbe _parler_ → adverbe."), [("bon", "_bon_ est un adjectif."), ("bonne", "_bonne_ est un adjectif féminin.")]),
    Q("a", 1, "form", "C'est un ___ restaurant, je te le recommande.", ("bon", "On qualifie le nom _restaurant_ → adjectif."), [("bien", "_bien_ ne qualifie pas un nom ici."), ("bonnement", "_bonnement_ est un adverbe rare et ne convient pas.")]),
    Q("a", 2, "form", "Ce semestre, il ___ : il a eu de très bonnes notes.", ("a bien travaillé", "Adverbe court entre l'auxiliaire et le participe."),
      [("a travaillé bien", "_bien_ se place entre l'auxiliaire et le participe passé."), ("bien a travaillé", "L'adverbe ne précède pas le verbe conjugué.")]),
    Q("a", 2, "form", "Ces fraises sentent ___.", ("bon", "_sentir bon_ : adjectif employé comme adverbe, invariable."), [("bonnes", "Dans _sentir bon_, _bon_ est invariable."), ("bien", "_sentir bien_ signifie avoir un bon odorat.")]),
    Q("b", 1, "form", "Il conduit ___ (prudent).", ("prudemment", "_prudent → prudemment_."), [("prudentement", "_-ent → -emment_."), ("prudamment", "_prudent_ (en _-ent_) donne _-emment_.")]),
    Q("b", 2, "form", "Elle parle ___ quatre langues (courant).", ("couramment", "_courant → couramment_."), [("couramant", "La forme est _couramment_, avec deux _m_."), ("couremment", "_-ant_ donne _-amment_.")]),
    Q("b", 2, "form", "J'ai ___ changé de travail (récent).", ("récemment", "_récent → récemment_."), [("récentement", "_-ent → -emment_."), ("récamment", "_récent_ donne _-emment_.")]),
    Q("b", 3, "form", "Il nous a ___ aidés à déménager (gentil).", ("gentiment", "Exception : _gentil → gentiment_."), [("gentillement", "La forme correcte est _gentiment_."), ("gentilement", "La forme correcte est _gentiment_.")]),
    Q("c", 1, "vocabulary", "J'ai perdu mes clés : je les ai cherchées ___ dans l'appartement.", ("partout", "_partout_ = dans tous les endroits."),
      [("ailleurs", "_ailleurs_ = dans un autre endroit."), ("dessous", "_dessous_ demande un repère (_sous la table_).")]),
    Q("c", 2, "vocabulary", "Ce restaurant est complet : allons manger ___.", ("ailleurs", "_ailleurs_ = dans un autre endroit."),
      [("partout", "_partout_ = dans tous les endroits."), ("dedans", "_dedans_ = à l'intérieur, ici impossible.")]),
    Q("c", 2, "vocabulary", "Le magasin a fermé : ___, il faudra commander en ligne.", ("désormais", "_désormais_ = à partir de maintenant."),
      [("autrefois", "_autrefois_ renvoie au passé."), ("déjà", "_déjà_ n'exprime pas le point de départ d'une nouvelle situation.")]),
  ],
  cards=[R("amment", "b", "Adverbes en -amment / -emment", "Adverbe de constant, évident, fréquent ?", "**constamment, évidemment, fréquemment** (_-ant → -amment_, _-ent → -emment_, prononcés [amɑ̃])."),
         R("bon-bien", "a", "Bon / bien", "bon ou bien ?", "**bon** qualifie un nom (_un bon livre_) ; **bien** modifie un verbe (_il écrit bien_).")])

# ================================================================ chapitre 19
c = b.chapter(19, "L'expression de la quantité", focus=[
    P("Les articles partitifs (_du, de la_) et les expressions de quantité (_beaucoup de, un kilo de_) sont indispensables pour parler de consommation, "
      "d'alimentation ou d'environnement, thèmes fréquents au DELF."),
    P(REF.format(19, 86)),
], los={
    "a": "Employer les partitifs (du, de la, de l', des) pour une quantité indéterminée.",
    "b": "Exprimer une quantité précise avec _de_ (beaucoup de, un kilo de…) et à la négation.",
})
c.module(1, "Quantités indéterminées et exprimées", sections=[
    ("a", [
        P("**Partitif** : une partie d'une chose qu'on ne compte pas : _du pain, **de la** confiture, **de l'**eau, **des** épinards_. "
          "On l'emploie avec _manger, boire, acheter, il y a, faire (du sport)_…"),
        P("Comparer : _J'aime **le** café_ (en général, défini) / _Je bois **du** café_ (une quantité, partitif) / _Je bois **un** café_ (une tasse, indéfini)."),
    ]),
    ("b", [
        P("Après une **expression de quantité**, on emploie **de / d'** sans article : _beaucoup **de** sucre, peu **d'**argent, trop **de** travail, assez **de** temps, "
          "un kilo **de** pommes, une bouteille **d'**eau, la plupart **des** gens_ (exception : _la plupart_ et _bien_ + _des_)."),
        P("**Négation** : _du, de la, des_ → **de / d'** : _Je ne mange pas **de** viande. Il n'y a plus **d'**eau._"),
        NOTE("Avec _être_, la négation ne change pas l'article : _Ce n'est pas **du** sucre, c'est du sel._"),
    ]),
], chain=[
    ("assumption", "Le français distingue ce qu'on compte (_un œuf_) et ce qu'on ne compte pas (_du beurre_)."),
    ("mechanism", "Une quantité indéterminée prend le partitif ; une quantité exprimée ou niée prend _de_ seul."),
    ("result", "Après _aimer_, on garde le défini ; après _beaucoup_ ou _pas_, on passe à _de_."),
], why="Les articles de quantité apparaissent dans tous les sujets sur l'alimentation, la consommation et l'environnement.",
  look=["un verbe de goût ou de consommation", "une expression de quantité", "une négation"],
  traps=["*_beaucoup des gens_", "*_je ne bois pas du vin_", "*_j'aime du chocolat_"],
  distractors=["le partitif gardé après une quantité ou une négation", "le défini à la place du partitif"],
  questions=[
    Q("a", 1, "form", "Au petit déjeuner, je prends ___ pain et du beurre.", ("du", "Quantité indéterminée, masculin → _du_."), [("le", "On ne parle pas du pain en général."), ("de", "_de_ seul s'emploie après une quantité ou une négation.")]),
    Q("a", 1, "form", "Il faut boire ___ eau régulièrement en été.", ("de l'", "Partitif devant voyelle → _de l'_."), [("du", "Devant une voyelle → _de l'_."), ("l'", "On parle d'une quantité, pas de l'eau en général.")]),
    Q("a", 2, "conceptual", "Mon frère déteste ___ poisson.", ("le", "Après un verbe de goût → défini."), [("du", "Pas de partitif après _détester_."), ("de", "_de_ seul ne s'emploie pas ici.")]),
    Q("b", 1, "form", "Il y a beaucoup ___ monde dans le métro ce matin.", ("de", "Après _beaucoup_ → _de_."), [("du", "Après une expression de quantité, pas d'article."), ("des", "_beaucoup des_ est fautif.")]),
    Q("b", 2, "form", "La plupart ___ habitants travaillent en ville.", ("des", "Exception : _la plupart des_."), [("de", "_la plupart_ est suivi de _des_."), ("d'", "_la plupart_ est suivi de _des_.")]),
    Q("b", 2, "form", "Je suis végétarien : je ne mange pas ___ viande.", ("de", "Négation → _de_."), [("de la", "Après la négation, le partitif devient _de_."), ("la", "On ne parle pas de la viande en général.")]),
    Q("b", 3, "form", "Ce n'est pas ___ sucre, c'est du sel !", ("du", "Avec _être_, la négation ne change pas l'article."), [("de", "Après _ce n'est pas_, l'article reste."), ("le", "On compare deux substances, en quantité.")]),
    Q("b", 2, "form", "Achète deux bouteilles ___ huile d'olive, s'il te plaît.", ("d'", "Quantité exprimée + voyelle → _d'_."), [("de l'", "Après une quantité, pas d'article."), ("des", "_des_ ne suit pas une quantité exprimée.")]),
  ],
  sets=[S("Bien manger sans se ruiner",
    "Une diététicienne donne ses conseils :\n\n« Mangez **(1)** ___ légumes à chaque repas et limitez la viande rouge. Vous n'avez pas besoin de beaucoup **(2)** ___ argent : "
    "un kilo **(3)** ___ lentilles coûte moins de trois euros. Et si vous n'aimez pas **(4)** ___ légumes secs, essayez-les en soupe ! »",
    [Q("a", 1, "form", "Blanc (1) :", ("des", "Quantité indéterminée, pluriel → _des_."), [("de", "_de_ seul après une quantité ou une négation."), ("les", "On ne parle pas des légumes en général.")]),
     Q("b", 1, "form", "Blanc (2) :", ("d'", "Après _beaucoup_ → _d'_."), [("de l'", "Pas d'article après _beaucoup_."), ("du", "Pas d'article après _beaucoup_.")]),
     Q("b", 1, "form", "Blanc (3) :", ("de", "Quantité exprimée → _de_."), [("des", "Pas d'article après _un kilo_."), ("du", "_lentilles_ est pluriel, et pas d'article après une quantité.")]),
     Q("a", 2, "conceptual", "Blanc (4) :", ("les", "Après _aimer_ (même à la négation) → défini, sens général."),
       [("de", "Après un verbe de goût, l'article défini reste même à la négation."), ("des", "Pas de partitif après _aimer_.")])])],
  cards=[R("partitif", "a", "Défini ou partitif ?", "J'aime ___ café / Je bois ___ café ?", "J'aime **le** café (en général) ; je bois **du** café (une quantité).", mistake="*_J'aime du café_."),
         R("quantite-de", "b", "Quantité et négation", "Après beaucoup, un kilo, ne… pas ?", "**de / d'** sans article : _beaucoup de temps, pas de viande_. Exception : **la plupart des**.")])

# ================================================================ chapitre 22
c = b.chapter(22, "Le comparatif et le superlatif", focus=[
    P("Comparer est au cœur de l'argumentation : avantages et inconvénients, avant et maintenant, ici et ailleurs. "
      "_Meilleur / mieux_ et le superlatif (_le plus…, le moins…_) sont attendus au niveau B2."),
    P(REF.format(22, 96)),
], los={
    "a": "Former le comparatif avec un adjectif, un adverbe, un nom ou un verbe.",
    "b": "Former le superlatif et employer _meilleur / mieux_, _pire_.",
})
c.module(1, "Comparatif, superlatif, meilleur et mieux", sections=[
    ("a", [
        TABLE(["", "Supériorité", "Égalité", "Infériorité"],
              ["adjectif / adverbe", "**plus** grand **que**", "**aussi** grand **que**", "**moins** grand **que**"],
              ["nom", "**plus de** temps **que**", "**autant de** temps **que**", "**moins de** temps **que**"],
              ["verbe", "travailler **plus que**", "travailler **autant que**", "travailler **moins que**"]),
        P("Progression : _**de plus en plus** cher, **de moins en moins** de lecteurs_. Proportion : _**Plus** on lit, **plus** on progresse._"),
    ]),
    ("b", [
        P("**Superlatif** : _**le / la / les plus** + adjectif (**de**)_ : _la ville **la plus** chère **de** France_. Avec un adjectif placé avant : _**le plus** grand pays du monde_."),
        TABLE(["", "Comparatif", "Superlatif"], ["bon (adjectif)", "**meilleur(e)(s)**", "le / la / les **meilleur(e)(s)**"],
              ["bien (adverbe)", "**mieux**", "le **mieux**"], ["mauvais", "plus mauvais / **pire**", "le plus mauvais / le **pire**"]),
        NOTE("*_plus bon_ et *_plus bien_ n'existent pas. _Meilleur_ qualifie un nom (_un meilleur salaire_) ; _mieux_ modifie un verbe (_il chante mieux_)."),
    ]),
], chain=[
    ("assumption", "On compare des qualités (adjectifs), des façons de faire (adverbes), des quantités (noms) ou des actions (verbes)."),
    ("mechanism", "_plus / aussi / moins … que_ avec adjectifs et adverbes, _plus de / autant de / moins de_ avec les noms, _plus / autant / moins_ après les verbes."),
    ("result", "_Bon_ devient _meilleur_ et _bien_ devient _mieux_ ; le superlatif ajoute l'article et _de_."),
], why="_Meilleur / mieux_, _autant de_ et _de plus en plus_ reviennent dans presque chaque essai ou débat du DELF.",
  look=["la nature du mot comparé (adjectif, adverbe, nom, verbe)", "_bon_ ou _bien_ à comparer"],
  traps=["*_plus bon_", "*_aussi de temps_", "*_le plus grand pays dans le monde_"],
  distractors=["_meilleur_ / _mieux_ inversés", "_aussi_ avec un nom", "_dans_ au lieu de _de_ après le superlatif"],
  questions=[
    Q("a", 1, "form", "Le train est ___ rapide que le bus.", ("plus", "Comparatif de supériorité avec un adjectif."), [("plus de", "_plus de_ s'emploie avec un nom."), ("autant", "_autant_ s'emploie avec un nom ou un verbe.")]),
    Q("a", 2, "form", "Cette année, j'ai ___ travail que l'an dernier.", ("autant de", "Égalité avec un nom → _autant de_."), [("aussi de", "_aussi_ s'emploie avec un adjectif ou un adverbe."), ("aussi", "Avec un nom → _autant de_.")]),
    Q("a", 2, "form", "Les jeunes lisent ___ journaux papier.", ("de moins en moins de", "Progression avec un nom → _de moins en moins de_."),
      [("de moins en moins", "Devant un nom, il faut _de_."), ("moins en moins des", "La structure est _de moins en moins de_.")]),
    Q("a", 3, "form", "___ on pratique, plus on progresse.", ("Plus", "Proportion : _plus…, plus…_"), [("Le plus", "Pas d'article dans la structure proportionnelle."), ("Autant", "La structure _autant…, plus…_ n'existe pas.")]),
    Q("b", 1, "form", "Ce gâteau est ___ que celui d'hier.", ("meilleur", "Comparatif de _bon_ → _meilleur_."), [("plus bon", "*_plus bon_ n'existe pas."), ("plus meilleur", "_meilleur_ est déjà un comparatif.")]),
    Q("b", 2, "form", "Depuis qu'elle a des lunettes, elle voit ___.", ("mieux", "Comparatif de _bien_ (verbe _voir_) → _mieux_."), [("meilleur", "_meilleur_ qualifie un nom."), ("plus bien", "*_plus bien_ n'existe pas.")]),
    Q("b", 2, "form", "C'est le musée le plus visité ___ monde.", ("du", "Superlatif + _de_ : _du monde_."), [("dans le", "Après un superlatif, on emploie _de_."), ("au", "Après un superlatif, on emploie _de_.")]),
    Q("b", 3, "form", "C'est ___ solution, à mon avis.", ("la meilleure", "Superlatif de _bon_ au féminin."), [("la mieux", "_mieux_ ne qualifie pas un nom."), ("la plus bonne", "*_plus bonne_ n'existe pas.")]),
    Q("b", 3, "form", "La situation est ___ qu'on ne le pensait.", ("pire", "_pire_ = plus mauvais(e)."), [("plus pire", "_pire_ est déjà un comparatif."), ("pirement", "Ce mot n'existe pas.")]),
  ],
  cards=[R("meilleur-mieux", "b", "Meilleur / mieux", "Comparatif de bon et de bien ?", "bon → **meilleur** (nom) ; bien → **mieux** (verbe).", mistake="*_plus bon_, *_plus bien_."),
         R("autant-de", "a", "Comparer des quantités", "Comparatif avec un nom ?", "**plus de / autant de / moins de** + nom (+ **que**).", examples=["Il a autant de livres que moi."])])

b.write()
