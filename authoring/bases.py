from fr import NOTE, P, Q, R, S, TABLE, UL, Book

b = Book("bases")
REF = "Repère : _Grammaire progressive du français_, chapitre {} (p. {})."

# ================================================================ chapitre 1
c = b.chapter(1, "Le verbe « être »", focus=[
    P("_Être_ est le verbe le plus fréquent du français : il sert à se présenter, à décrire et à former le passé composé de nombreux verbes. "
      "Au niveau B2, les erreurs portent surtout sur les prépositions qui suivent (_à Paris, de Lyon, chez des amis_)."),
    P(REF.format(1, 8)),
], los={
    "a": "Conjuguer _être_ au présent avec les pronoms sujets.",
    "b": "Employer _à_, _de_ et _chez_ après _être_ pour situer quelqu'un.",
})
c.module(1, "Le verbe « être » et les pronoms sujets", sections=[
    ("a", [
        TABLE(["Pronom", "être", "Pronom", "être"],
              ["je", "suis", "nous", "sommes"], ["tu", "es", "vous", "êtes"], ["il / elle / on", "est", "ils / elles", "sont"]),
        P("**Tu** s'emploie avec un proche, **vous** avec une personne qu'on vouvoie ou avec plusieurs personnes. "
          "**On** (= _nous_ à l'oral, ou _les gens_) se conjugue comme _il_ : _On **est** prêts._"),
        NOTE("_Ils_ remplace un groupe masculin ou mixte ; _elles_, un groupe uniquement féminin : _Paul et Marie ? **Ils** sont là._"),
    ]),
    ("b", [
        UL("**à** + ville où l'on est : _Je suis **à** Berlin._",
           "**de** + ville d'origine : _Je suis **de** Rome._ Devant une voyelle : _Vous êtes **d'**où ? Je suis **d'**Athènes._",
           "**chez** + personne : _Je suis **chez** Pierre, **chez** des amis, **chez** moi, **chez** le médecin._"),
        NOTE("On ne dit pas *_à le médecin_ pour parler du cabinet : on est **chez** le médecin (la personne), mais **à** l'hôpital (le lieu)."),
    ]),
], chain=[
    ("assumption", "En français, le verbe est presque toujours précédé de son sujet (nom ou pronom)."),
    ("mechanism", "_Être_ est irrégulier : six formes différentes à mémoriser (_suis, es, est, sommes, êtes, sont_)."),
    ("result", "On situe une personne avec **à** (ville), **de** (origine) et **chez** (personne)."),
], why="Les fautes sur _être_ et sur _à / chez_ restent visibles même chez les apprenants avancés, en particulier à l'oral.",
  look=["le sujet (qui ?)", "un lieu (à), une origine (de) ou une personne (chez)"],
  traps=["_ils_ pour un groupe mixte", "*_à le dentiste_ au lieu de _chez le dentiste_"],
  distractors=["une autre personne du verbe", "la mauvaise préposition"],
  questions=[
    Q("a", 1, "form", "Nous ___ en retard pour la réunion.", ("sommes", "_nous sommes_."),
      [("sont", "_sont_ va avec _ils / elles_."), ("êtes", "_êtes_ va avec _vous_.")]),
    Q("a", 1, "form", "Marc et Julie ? ___ sont au bureau.", ("Ils", "Groupe mixte → _ils_."),
      [("Elles", "_elles_ ne désigne que des femmes."), ("On", "_on_ se conjugue avec _est_, pas _sont_.")]),
    Q("a", 1, "form", "Ce soir, on ___ fatigués après le voyage.", ("est", "_on_ se conjugue comme _il_ : _on est_."),
      [("sommes", "_sommes_ va avec _nous_, même si _on_ a le sens de _nous_."), ("sont", "_sont_ va avec _ils / elles_.")]),
    Q("b", 1, "conceptual", "Je suis ___ Lisbonne, mais j'habite à Paris depuis dix ans.", ("de", "Origine → _de_."),
      [("à", "_à_ indique la ville où l'on est, pas l'origine."), ("chez", "_chez_ s'emploie avec une personne.")]),
    Q("b", 1, "conceptual", "Ce week-end, nous sommes ___ nos cousins à la campagne.", ("chez", "Avec une personne → _chez_."),
      [("à", "_à_ s'emploie avec un lieu, pas une personne."), ("de", "_de_ indique l'origine.")]),
    Q("b", 2, "conceptual", "Désolé, je ne peux pas répondre, je suis ___ le dentiste.", ("chez", "_le dentiste_ est une personne → _chez_."),
      [("au", "*_au dentiste_ est fautif à l'écrit : on va _chez_ quelqu'un."), ("à le", "_à + le_ se contracte toujours, et ici il faut _chez_.")]),
    Q("b", 2, "form", "Vous êtes ___ où, madame ?", ("d'", "_de_ + voyelle → _d'_ : _d'où_."),
      [("de", "Devant une voyelle, _de_ s'élide."), ("à", "_à où_ n'existe pas.")]),
  ],
  cards=[R("etre", "a", "Le verbe être", "Être au présent ?", "je **suis**, tu **es**, il **est**, nous **sommes**, vous **êtes**, ils **sont**.",
           mistake="_on sommes_ : avec _on_, toujours _on est_."),
         R("a-de-chez", "b", "À, de, chez", "Être à / de / chez ?", "**à** + ville (où je suis) ; **de** + ville (origine) ; **chez** + personne.",
           examples=["Je suis à Berlin, de Rome, chez Pierre."])])

# ================================================================ chapitre 2
c = b.chapter(2, "L'adjectif (1) : genre et nombre", focus=[
    P("Un adjectif s'accorde en **genre** et en **nombre** avec le nom qu'il qualifie. À l'écrit du DELF, les fautes d'accord coûtent des points "
      "de « correction grammaticale » : elles sont faciles à éviter avec quelques règles."),
    P(REF.format(2, 12)),
], los={
    "a": "Former le féminin des adjectifs (règle générale et terminaisons particulières).",
    "b": "Former le pluriel des adjectifs et accorder l'adjectif avec le sujet.",
})
c.module(1, "Masculin, féminin, singulier, pluriel", sections=[
    ("a", [
        P("**Règle générale** : masculin + **-e** : _grand → grand**e**_, _français → français**e**_. Un adjectif déjà terminé par _-e_ ne change pas : _jeune, rapide, calme_."),
        TABLE(["Masculin", "Féminin", "Exemples"],
              ["-er", "-ère", "cher → chère, étranger → étrangère"], ["-eux", "-euse", "heureux → heureuse, sérieux → sérieuse"],
              ["-if", "-ive", "sportif → sportive, actif → active"], ["-en / -on", "-enne / -onne", "italien → italienne, bon → bonne"],
              ["-el", "-elle", "naturel → naturelle, cruel → cruelle"], ["-et", "-ète", "complet → complète, inquiet → inquiète"],
              ["-eur", "-euse (souvent)", "travailleur → travailleuse"]),
        P("**Féminins irréguliers** : _beau → belle, nouveau → nouvelle, vieux → vieille, blanc → blanche, frais → fraîche, long → longue, doux → douce, faux → fausse_."),
    ]),
    ("b", [
        P("**Pluriel** : singulier + **-s** (_grand → grands_). Pas de changement après _-s_ ou _-x_ : _français, heureux_."),
        UL("**-eau → -eaux** : _beau → beaux, nouveau → nouveaux_.", "**-al → -aux** : _national → nationaux, social → sociaux_ (mais _banal → banals, final → finals_)."),
        P("**Accord avec le sujet** : _Elles sont **contentes**._ Un groupe mixte prend le **masculin pluriel** : _Paul et Anne sont **fatigués**._"),
        NOTE("_Vous_ de politesse reste au singulier : _Vous êtes **prêt**, monsieur ? Vous êtes **prête**, madame ?_"),
    ]),
], chain=[
    ("assumption", "L'adjectif prend le genre et le nombre du nom ou du pronom qu'il qualifie."),
    ("mechanism", "On ajoute **-e** au féminin et **-s** au pluriel, avec des terminaisons particulières (-eux/-euse, -if/-ive, -al/-aux…)."),
    ("result", "Un groupe mixte s'accorde au masculin pluriel ; le _vous_ de politesse, au singulier."),
], why="Les accords d'adjectifs sont le premier critère de « correction » visible dans une copie de DELF.",
  look=["le nom ou le sujet qualifié", "son genre et son nombre", "la terminaison de l'adjectif au masculin"],
  traps=["*_une femme sérieux_", "*_des problèmes sociales_ (nom masculin)", "_vous_ de politesse mis au pluriel"],
  distractors=["le masculin non accordé", "un pluriel en -als au lieu de -aux", "un féminin mal formé"],
  questions=[
    Q("a", 1, "form", "Ma voisine est très ___ : elle court tous les matins.", ("sportive", "_-if → -ive_."),
      [("sportif", "C'est le masculin."), ("sportife", "_-if_ ne prend pas simplement un _e_.")]),
    Q("a", 1, "form", "C'est une femme ___ et très organisée.", ("sérieuse", "_-eux → -euse_."),
      [("sérieux", "C'est le masculin."), ("sérieuxe", "Ce féminin n'existe pas.")]),
    Q("a", 2, "form", "Cette robe est trop ___ pour moi.", ("chère", "_-er → -ère_, avec un accent grave."),
      [("chere", "Il manque l'accent grave : _chère_."), ("cher", "C'est le masculin.")]),
    Q("a", 2, "form", "Nous avons acheté une ___ voiture.", ("nouvelle", "_nouveau → nouvelle_."),
      [("nouveau", "C'est le masculin."), ("nouvel", "_nouvel_ s'emploie devant un nom masculin à voyelle : _un nouvel ami_.")]),
    Q("a", 2, "form", "La réponse est ___ : relisez la question.", ("fausse", "_faux → fausse_."),
      [("fauxe", "Ce féminin n'existe pas."), ("fause", "Le féminin s'écrit avec deux _s_.")]),
    Q("b", 1, "form", "Les mesures ___ du gouvernement ont été annoncées hier.", ("sociales", "_mesure_ est féminin : _sociale → sociales_."),
      [("sociaux", "_sociaux_ est le masculin pluriel."), ("socials", "Ce pluriel n'existe pas.")]),
    Q("b", 2, "form", "Les problèmes ___ sont nombreux dans cette région.", ("sociaux", "_-al → -aux_ au masculin pluriel."),
      [("socials", "_social_ fait _sociaux_."), ("sociales", "_problème_ est masculin.")]),
    Q("b", 2, "form", "Paul et ses deux sœurs sont très ___.", ("contents", "Groupe mixte → masculin pluriel."),
      [("contentes", "Un seul masculin suffit pour accorder au masculin."), ("content", "Le sujet est pluriel.")]),
    Q("b", 3, "form", "« Vous êtes ___, madame ? Nous pouvons commencer. »", ("prête", "_vous_ de politesse, une seule femme → féminin singulier."),
      [("prêtes", "Le _vous_ de politesse désigne une seule personne."), ("prêts", "Il s'agit d'une femme, seule.")]),
  ],
  cards=[R("feminin", "a", "Féminins particuliers", "Féminin de -eux, -if, -er, -en, -el ?", "-euse, -ive, -ère, -enne, -elle.",
           examples=["heureux → heureuse ; actif → active ; cher → chère ; ancien → ancienne ; naturel → naturelle"]),
         R("pluriel-al", "b", "Pluriel en -al", "Pluriel masculin de national, social, principal ?", "**-aux** : nationaux, sociaux, principaux.",
           mistake="_banal, final, fatal, naval_ font _-als_.")])

# ================================================================ chapitre 4
c = b.chapter(4, "Le nom et l'article", focus=[
    P("Le genre des noms et le choix de l'article (_un / le / du / au_) décident de la justesse de presque chaque phrase. "
      "Quelques terminaisons permettent de deviner le genre ; les contractions _au, aux, du, des_ sont obligatoires."),
    P(REF.format(4, 22)),
], los={
    "a": "Reconnaître le genre d'un nom (personnes et choses) et former son pluriel.",
    "b": "Choisir entre article indéfini et article défini.",
    "c": "Contracter l'article avec _à_ et _de_ (au, aux, du, des).",
})
c.module(1, "Le nom : genre et nombre", sections=[
    ("a", [
        P("**Personnes** : le féminin suit souvent les règles de l'adjectif : _un étudiant → une étudiante, un musicien → une musicienne, un vendeur → une vendeuse, "
          "un acteur → une actrice_. Certains noms ne changent pas : _un / une journaliste, un / une élève_."),
        TABLE(["Souvent masculins", "Souvent féminins"],
              ["-ment (le gouvernement)", "-tion / -sion (la nation, la décision)"], ["-age (le fromage, le voyage)", "-té (la société, la liberté)"],
              ["-isme (le tourisme)", "-ure (la culture), -ance / -ence (la confiance)"], ["-eau (le bureau)", "-ette (la cigarette), -ie (la vie)"]),
        NOTE("Exceptions fréquentes : _la plage, la page, l'image, la cage_ (féminins en -age) ; _l'eau, la peau_ (féminins en -eau) ; _le lycée, le musée_."),
        P("**Pluriel** : + **-s** ; _-eau, -eu → -x_ (_des bureaux, des jeux_) ; _-al → -aux_ (_un journal → des journaux_) ; _-s, -x, -z_ ne changent pas. "
          "Irréguliers : _un œil → des yeux, monsieur → messieurs, madame → mesdames_."),
    ]),
    ("b", [
        UL("**Indéfini** (_un, une, des_) : une chose non identifiée ou mentionnée pour la première fois : _J'ai acheté **un** livre._",
           "**Défini** (_le, la, l', les_) : une chose identifiée, unique ou générale : _**Le** livre que tu m'as prêté. **La** lune. J'aime **le** chocolat._"),
        NOTE("Après un verbe de goût (_aimer, adorer, détester, préférer_), on emploie l'article **défini** : _Je déteste **les** films d'horreur._"),
    ]),
    ("c", [
        TABLE(["", "+ le", "+ la", "+ l'", "+ les"],
              ["à", "**au**", "à la", "à l'", "**aux**"], ["de", "**du**", "de la", "de l'", "**des**"]),
        P("_Je vais **au** cinéma, **aux** États-Unis. Je reviens **du** marché, **des** Alpes. Le livre **du** professeur._"),
        NOTE("Pas de contraction avec _la_ et _l'_ : _à la gare, de l'hôpital_. *_À le_ et *_de le_ n'existent pas."),
    ]),
], chain=[
    ("assumption", "Chaque nom a un genre, signalé par l'article ; certaines terminaisons le laissent deviner."),
    ("mechanism", "L'article **indéfini** présente une chose nouvelle, le **défini** une chose identifiée ou générale."),
    ("result", "_À_ et _de_ fusionnent avec _le_ et _les_ : **au, aux, du, des**."),
], why="Un article faux change le genre ou le sens d'un mot ; les contractions oubliées sont des fautes immédiatement visibles.",
  look=["la terminaison du nom", "si la chose est déjà identifiée", "une préposition _à_ ou _de_ devant _le / les_"],
  traps=["*_le plage_", "*_à le bureau_", "un article indéfini après _aimer_"],
  distractors=["l'article de l'autre genre", "la forme non contractée", "l'indéfini à la place du défini"],
  questions=[
    Q("a", 1, "vocabulary", "___ décision du directeur a surpris tout le monde.", ("La", "Les noms en _-sion_ sont féminins."),
      [("Le", "_décision_ est féminin."), ("L'", "_L'_ s'emploie devant une voyelle ou un _h_ muet.")]),
    Q("a", 2, "vocabulary", "Nous avons passé l'après-midi sur ___ plage.", ("la", "_plage_ est une exception féminine en _-age_."),
      [("le", "Les noms en _-age_ sont souvent masculins, mais _plage_ est féminin."), ("un", "_un_ est masculin.")]),
    Q("a", 2, "vocabulary", "Le tourisme de masse transforme ___ paysage de la côte.", ("le", "_-age_ : _le paysage_ (masculin)."),
      [("la", "_paysage_ est masculin."), ("les", "_paysage_ est ici au singulier.")]),
    Q("a", 2, "form", "Elle lit trois ___ chaque matin.", ("journaux", "_-al → -aux_."),
      [("journals", "_journal_ fait _journaux_."), ("journauxs", "Ce pluriel n'existe pas.")]),
    Q("a", 1, "form", "Mon père est acteur et ma mère est ___.", ("actrice", "_-teur → -trice_."),
      [("acteuse", "Ce féminin n'existe pas."), ("acteure", "Ce féminin n'existe pas.")]),
    Q("b", 1, "conceptual", "J'adore ___ musique classique.", ("la", "Après un verbe de goût → article défini (sens général)."),
      [("une", "L'indéfini ne convient pas au sens général après _adorer_."), ("de la", "Le partitif ne s'emploie pas après _adorer_.")]),
    Q("b", 2, "conceptual", "Ferme ___ porte, s'il te plaît, il fait froid.", ("la", "La porte de la pièce, identifiée par la situation → défini."),
      [("une", "Il s'agit d'une porte précise, connue des deux personnes."), ("de la", "Le partitif ne s'emploie pas avec un objet comptable.")]),
    Q("b", 1, "conceptual", "___ soleil se couche plus tôt en hiver.", ("Le", "Chose unique → article défini."),
      [("Un", "Il n'y a qu'un soleil : il est identifié."), ("Du", "Le partitif ne s'emploie pas avec une chose unique.")]),
    Q("c", 1, "form", "Ce soir, nous allons ___ théâtre.", ("au", "_à + le = au_."),
      [("à le", "_à + le_ se contracte toujours."), ("à la", "_théâtre_ est masculin.")]),
    Q("c", 2, "form", "Elle revient ___ États-Unis la semaine prochaine.", ("des", "_de + les = des_."),
      [("de les", "_de + les_ se contracte toujours."), ("du", "_États-Unis_ est pluriel.")]),
    Q("c", 2, "form", "Le bureau ___ directrice est au troisième étage.", ("de la", "Pas de contraction avec _la_."),
      [("du", "_du_ = _de + le_ ; _directrice_ est féminin."), ("des", "_directrice_ est au singulier.")]),
  ],
  sets=[S("Le message de Léa",
    "Léa écrit à une amie :\n\n« Je suis arrivée hier à Montréal. Ce matin, je suis allée **(1)** ___ musée des Beaux-Arts, puis j'ai mangé dans **(2)** ___ petit restaurant "
    "près du port. J'adore **(3)** ___ cuisine québécoise ! Demain, je pars visiter **(4)** ___ chutes de Montmorency. »",
    [Q("c", 1, "form", "Blanc (1) :", ("au", "_aller à + le musée_ → _au_."), [("à le", "_à + le_ se contracte."), ("à la", "_musée_ est masculin.")]),
     Q("b", 1, "conceptual", "Blanc (2) :", ("un", "Restaurant mentionné pour la première fois → indéfini singulier."),
       [("des", "_restaurant_ est au singulier."), ("de", "_de_ seul ne s'emploie qu'après une négation ou une quantité.")]),
     Q("b", 1, "conceptual", "Blanc (3) :", ("la", "Après _adorer_ → défini."), [("une", "Sens général après un verbe de goût."), ("de la", "Pas de partitif après _adorer_.")]),
     Q("b", 2, "conceptual", "Blanc (4) :", ("les", "Des chutes précises, identifiées par leur nom → défini."),
       [("des", "Le lieu est identifié : il faut le défini."), ("aux", "_visiter_ est transitif direct : pas de _à_.")])])],
  cards=[R("genre-terminaisons", "a", "Genre et terminaisons", "Terminaisons souvent masculines / féminines ?",
           "Masc. : -ment, -age, -isme, -eau. Fém. : -tion, -sion, -té, -ure, -ance, -ence, -ie.", mistake="_la plage, la page, l'image, l'eau_ : exceptions."),
         R("contractions", "c", "Contractions", "à / de + le, les ?", "à + le = **au** ; à + les = **aux** ; de + le = **du** ; de + les = **des**.",
           examples=["Je vais au marché ; je reviens du marché."], mistake="Pas de contraction avec _la_ et _l'_.")])

# ================================================================ chapitre 5
c = b.chapter(5, "« C'est » et « il est »", focus=[
    P("_C'est_ et _il / elle est_ servent tous deux à présenter et à commenter. Le choix dépend de ce qui suit : un **nom déterminé** ou un **adjectif**. "
      "À l'écrit argumentatif, _c'est + adjectif_ (« C'est essentiel ») est très fréquent."),
    P(REF.format(5, 32)),
], los={
    "a": "Choisir entre _c'est_ et _il / elle est_ pour identifier, décrire et commenter.",
    "b": "Présenter une profession avec ou sans article.",
})
c.module(1, "L'identification, le commentaire et la profession", sections=[
    ("a", [
        UL("**C'est + nom déterminé** (article, possessif…) ou **nom propre** : _**C'est** un ami. **C'est** mon frère. **C'est** Paul._",
           "**Il / elle est + adjectif** pour décrire une personne ou une chose précise : _Paul ? **Il est** sympathique. Cette maison ? **Elle est** grande._",
           "**C'est + adjectif masculin** pour commenter une idée, une situation : _Vivre à Paris, **c'est** cher. **C'est** génial !_"),
        P("Au pluriel : _**Ce sont** des amis._ (À l'oral, on entend aussi _c'est des amis_.)"),
    ]),
    ("b", [
        P("Profession, nationalité, religion après _être_ : **pas d'article** : _Il est **médecin**. Elle est **avocate**._"),
        P("Mais avec un adjectif ou une précision, le nom est déterminé → **c'est un(e)** : _**C'est un** médecin **remarquable**. **C'est une** avocate **qui** gagne tous ses procès._"),
        NOTE("*_Il est un médecin_ est une erreur fréquente : soit _il est médecin_, soit _c'est un médecin_."),
    ]),
], chain=[
    ("assumption", "Les deux structures présentent quelqu'un ou quelque chose, mais ne se combinent pas avec les mêmes mots."),
    ("mechanism", "**C'est** + nom déterminé ou commentaire général ; **il / elle est** + adjectif ou profession sans article."),
    ("result", "Un nom de profession qualifié redevient un nom déterminé : _c'est un excellent médecin_."),
], why="La confusion _il est un…_ / _c'est un…_ fait partie des erreurs typiques relevées par les correcteurs de B1–B2.",
  look=["ce qui suit : nom avec article, adjectif seul ou profession", "si l'on commente une personne précise ou une idée"],
  traps=["*_Il est un professeur_", "*_Elle est une bonne idée_ pour commenter une idée", "_c'est_ + adjectif accordé au féminin"],
  distractors=["_il est_ devant un nom avec article", "_c'est_ devant une profession sans article"],
  questions=[
    Q("a", 1, "conceptual", "Tu connais Sophie ? ___ ma collègue.", ("C'est", "Nom déterminé (_ma collègue_) → _c'est_."),
      [("Elle est", "_elle est_ ne se place pas devant un nom avec déterminant."), ("Il est", "_il est_ ne convient ni au genre ni à la structure.")]),
    Q("a", 1, "conceptual", "J'ai rencontré ton frère : ___ très drôle !", ("il est", "Adjectif qui décrit une personne précise → _il est_."),
      [("c'est", "_c'est + adjectif_ commente une situation, pas une personne précise."), ("elle est", "_frère_ est masculin.")]),
    Q("a", 2, "conceptual", "Apprendre une langue en trois mois ? ___ difficile, mais possible.", ("C'est", "Commentaire sur une idée → _c'est + adjectif masculin_."),
      [("Elle est", "On ne commente pas un nom féminin précis, mais une idée."), ("Il est", "_il est difficile_ se construit avec _de_ + infinitif à la suite.")]),
    Q("a", 2, "form", "Regarde ces photos : ___ mes enfants.", ("ce sont", "Pluriel → _ce sont_."),
      [("c'est", "À l'écrit soigné, pluriel → _ce sont_."), ("ils sont", "_ils sont_ ne se place pas devant un nom déterminé.")]),
    Q("b", 1, "conceptual", "Ma sœur ___ infirmière à l'hôpital de Lyon.", ("est", "Profession après _être_ → sans article."),
      [("est une", "Sans adjectif, pas d'article devant une profession."), ("c'est", "_Ma sœur c'est infirmière_ n'est pas correct.")]),
    Q("b", 2, "conceptual", "Mon voisin ? ___ architecte très connu.", ("C'est un", "Profession qualifiée (_très connu_) → _c'est un_."),
      [("Il est un", "*_Il est un_ + nom est fautif."), ("Il est", "Avec l'adjectif, le nom doit être déterminé.")]),
    Q("b", 3, "conceptual", "Mme Duval ? ___ une avocate qui défend les petites entreprises.", ("C'est", "Nom déterminé et précisé par une relative → _c'est une_."),
      [("Elle est", "*_elle est une avocate_ est fautif."), ("Elle", "Il manque le verbe.")]),
  ],
  cards=[R("cest-ilest", "a", "C'est / il est", "C'est ou il est ?",
           "**C'est** + nom déterminé, nom propre, ou commentaire (_c'est génial_). **Il / elle est** + adjectif (personne précise) ou profession sans article.",
           examples=["C'est un médecin. Il est médecin. C'est un excellent médecin."], mistake="*_Il est un médecin_.")])

# ================================================================ chapitre 6
c = b.chapter(6, "Les possessifs", focus=[
    P("Les possessifs indiquent l'appartenance. En français, ils s'accordent avec la **chose possédée**, pas avec le possesseur : "
      "_son frère_ peut être le frère d'un homme ou d'une femme."),
    P(REF.format(6, 36)),
], los={
    "a": "Choisir l'adjectif possessif (mon, ma, mes, son, sa, ses, leur, leurs…).",
    "b": "Employer les pronoms possessifs (le mien, la tienne, les leurs…).",
})
c.module(1, "L'adjectif et le pronom possessifs", sections=[
    ("a", [
        TABLE(["Possesseur", "masc. sing.", "fém. sing.", "pluriel"],
              ["je", "mon", "ma", "mes"], ["tu", "ton", "ta", "tes"], ["il / elle", "son", "sa", "ses"],
              ["nous", "notre", "notre", "nos"], ["vous", "votre", "votre", "vos"], ["ils / elles", "leur", "leur", "leurs"]),
        P("Devant un nom féminin qui commence par une voyelle ou un _h_ muet : **mon, ton, son** : _**mon** amie, **son** école, **ton** histoire_."),
        NOTE("**Leur** (un objet, plusieurs possesseurs) / **leurs** (plusieurs objets) : _les parents et **leur** fils_, _les parents et **leurs** enfants_."),
    ]),
    ("b", [
        TABLE(["", "masc. sing.", "fém. sing.", "masc. plur.", "fém. plur."],
              ["je", "le mien", "la mienne", "les miens", "les miennes"], ["tu", "le tien", "la tienne", "les tiens", "les tiennes"],
              ["il / elle", "le sien", "la sienne", "les siens", "les siennes"], ["nous", "le nôtre", "la nôtre", "les nôtres", "les nôtres"],
              ["vous", "le vôtre", "la vôtre", "les vôtres", "les vôtres"], ["ils / elles", "le leur", "la leur", "les leurs", "les leurs"]),
        P("Le pronom remplace _possessif + nom_ : _Ce n'est pas ma valise, c'est **la tienne**._ Accent circonflexe : **le nôtre, le vôtre** (pronoms), mais **notre, votre** (adjectifs)."),
    ]),
], chain=[
    ("assumption", "Le possessif dépend de deux choses : la personne du possesseur et le genre / nombre de l'objet possédé."),
    ("mechanism", "_son / sa / ses_ s'accordent avec l'objet ; _mon, ton, son_ remplacent _ma, ta, sa_ devant une voyelle."),
    ("result", "Le pronom (_le mien, la leur_) reprend l'ensemble _possessif + nom_ pour éviter une répétition."),
], why="Le possessif est un piège pour les anglophones (_his / her_) : en français, _sa mère_ peut être la mère d'un homme.",
  look=["le genre et le nombre de l'objet possédé", "le nombre de possesseurs", "une voyelle au début du nom"],
  traps=["*_ma amie_", "_sa_ choisi d'après le possesseur (anglais _her_)", "_notre_ / _le nôtre_ (accent)"],
  distractors=["le possessif accordé au possesseur", "_leur_ / _leurs_ inversés", "la forme féminine devant voyelle"],
  questions=[
    Q("a", 1, "form", "Paul a oublié ___ clés au bureau.", ("ses", "Plusieurs clés → _ses_."), [("sa", "_clés_ est pluriel."), ("leurs", "Un seul possesseur.")]),
    Q("a", 2, "form", "Anne m'a présenté ___ mari hier soir.", ("son", "_mari_ est masculin : _son_, même si le possesseur est une femme."),
      [("sa", "Le possessif s'accorde avec l'objet (_mari_), pas avec Anne."), ("ses", "_mari_ est singulier.")]),
    Q("a", 2, "form", "Je te présente ___ amie Clara.", ("mon", "Nom féminin à voyelle → _mon_."), [("ma", "*_ma amie_ est impossible."), ("m'", "_ma_ ne s'élide pas en _m'_.")]),
    Q("a", 2, "form", "Les étudiants doivent rendre ___ mémoires avant le 30 juin.", ("leurs", "Plusieurs possesseurs, plusieurs mémoires → _leurs_."),
      [("leur", "Chaque étudiant rend un mémoire, soit plusieurs mémoires : _leurs_."), ("ses", "Plusieurs possesseurs → _leur(s)_.")]),
    Q("a", 3, "form", "Les deux sœurs vivent encore chez ___ mère.", ("leur", "Une seule mère pour plusieurs possesseurs → _leur_."),
      [("leurs", "Il n'y a qu'une mère."), ("sa", "Plusieurs possesseurs → _leur_.")]),
    Q("b", 1, "form", "Ce n'est pas mon téléphone, c'est ___.", ("le tien", "_téléphone_ est masculin singulier → _le tien_."),
      [("la tienne", "_téléphone_ est masculin."), ("ton", "_ton_ doit être suivi d'un nom.")]),
    Q("b", 2, "form", "Nos enfants vont à l'école publique ; ___ vont dans une école privée.", ("les leurs", "Leurs enfants → _les leurs_."),
      [("leurs", "Sans nom, il faut le pronom _les leurs_."), ("les leur", "Pronom pluriel → _les leurs_ avec _s_.")]),
    Q("b", 2, "form", "Votre proposition est intéressante, mais ___ est moins chère.", ("la nôtre", "Pronom (_notre proposition_) → _la nôtre_, avec accent."),
      [("la notre", "Le pronom prend un accent circonflexe : _nôtre_."), ("notre", "_notre_ doit être suivi d'un nom.")]),
  ],
  cards=[R("son-sa", "a", "Son / sa / ses", "Le possessif s'accorde avec… ?", "avec la **chose possédée** : _son mari_ (de Anne), _sa femme_ (de Paul).",
           mistake="*_ma amie_ → _mon amie_ devant voyelle."),
         R("le-mien", "b", "Pronoms possessifs", "Pronom pour _notre maison_, _leurs enfants_ ?", "**la nôtre** ; **les leurs**.")])

# ================================================================ chapitre 7
c = b.chapter(7, "Les noms de parenté et de groupe", focus=[
    P("La famille et les groupes (_les gens, la plupart, la majorité_) reviennent dans les sujets de société du DELF. "
      "L'accord du verbe après un nom collectif est un point délicat."),
    P(REF.format(7, 38)),
], los={
    "a": "Nommer les liens de parenté.",
    "b": "Accorder le verbe après un nom de groupe ou de quantité.",
})
c.module(1, "La parenté et les noms de groupe", sections=[
    ("a", [
        TABLE(["Masculin", "Féminin", "Ensemble"],
              ["le père", "la mère", "les parents"], ["le grand-père", "la grand-mère", "les grands-parents"], ["le fils", "la fille", "les enfants"],
              ["le frère", "la sœur", "les frères et sœurs"], ["l'oncle", "la tante", ""], ["le neveu", "la nièce", ""], ["le cousin", "la cousine", ""],
              ["le beau-père", "la belle-mère", "les beaux-parents"], ["le mari / l'époux", "la femme / l'épouse", "le couple"]),
        P("_Beau-père_ = le père du conjoint **ou** le nouveau mari de la mère. Les _parents_ sont aussi, plus largement, toute la famille : _J'ai des **parents** en Bretagne_."),
    ]),
    ("b", [
        UL("Nom collectif au singulier → verbe au **singulier** : _**La famille** arrive demain. **Le public** applaudit._",
           "**Les gens** → verbe au pluriel et adjectif au masculin pluriel : _Les gens **sont** pressés._",
           "**La plupart (des…)** → verbe au **pluriel** : _La plupart des étudiants **travaillent** l'été._",
           "**La majorité / une partie / un groupe de + nom pluriel** → singulier ou pluriel (accord au sens) : _La majorité des Français **pense / pensent**…_"),
        NOTE("**Tout le monde** → singulier : _Tout le monde **est** d'accord._"),
    ]),
], chain=[
    ("assumption", "Un nom collectif désigne plusieurs personnes avec un mot singulier (_la famille, le public_)."),
    ("mechanism", "Le verbe s'accorde avec la forme grammaticale du nom (singulier), sauf après _la plupart_, toujours suivi du pluriel."),
    ("result", "_Tout le monde_ est singulier ; _les gens_ et _la plupart_ sont pluriels."),
], why="Les accords après _la plupart_, _tout le monde_ et _les gens_ apparaissent dans presque toutes les productions écrites argumentatives.",
  look=["le nom sujet : collectif singulier ou pluriel ?", "_la plupart_ et _tout le monde_"],
  traps=["*_tout le monde sont_", "*_la plupart des gens pense_", "_beau-père_ (deux sens)"],
  distractors=["l'accord au sens à la place de l'accord grammatical", "le mauvais lien de parenté"],
  questions=[
    Q("a", 1, "vocabulary", "La fille de mon frère est ma ___.", ("nièce", "L'enfant de mon frère ou de ma sœur : neveu / nièce."),
      [("cousine", "La cousine est la fille de mon oncle ou de ma tante."), ("tante", "La tante est la sœur de mon père ou de ma mère.")]),
    Q("a", 2, "vocabulary", "Les parents de ma femme sont mes ___.", ("beaux-parents", "Parents du conjoint → beaux-parents."),
      [("grands-parents", "Les grands-parents sont les parents de mes parents."), ("petits-enfants", "Ce sont les enfants de mes enfants.")]),
    Q("a", 1, "vocabulary", "Le frère de ma mère est mon ___.", ("oncle", "Le frère d'un parent → oncle."),
      [("neveu", "Le neveu est le fils de mon frère ou de ma sœur."), ("cousin", "Le cousin est le fils de mon oncle ou de ma tante.")]),
    Q("b", 1, "form", "Tout le monde ___ content de partir en vacances.", ("est", "_tout le monde_ → singulier."),
      [("sont", "_tout le monde_ est grammaticalement singulier."), ("êtes", "_êtes_ va avec _vous_.")]),
    Q("b", 2, "form", "La plupart des salariés ___ en télétravail le vendredi.", ("sont", "_la plupart des_ → pluriel."),
      [("est", "Après _la plupart_, le verbe est au pluriel."), ("es", "_es_ va avec _tu_.")]),
    Q("b", 2, "form", "Les gens ___ de plus en plus attentifs à leur alimentation.", ("sont", "_les gens_ est pluriel."),
      [("est", "_gens_ est pluriel."), ("sommes", "_sommes_ va avec _nous_.")]),
    Q("b", 2, "form", "Ce soir, le public ___ les musiciens pendant dix minutes.", ("applaudit", "_le public_ est un nom singulier."),
      [("applaudissent", "_public_ est singulier : verbe au singulier."), ("applaudissons", "Le sujet est _le public_, pas _nous_.")]),
  ],
  cards=[R("plupart", "b", "Accord après la plupart / tout le monde", "La plupart des gens … ; tout le monde … ?",
           "_La plupart des gens_ + **pluriel** ; _tout le monde_ + **singulier**.", examples=["La plupart des gens pensent… / Tout le monde pense…"])])

# ================================================================ chapitre 8
c = b.chapter(8, "Les démonstratifs", focus=[
    P("Les démonstratifs montrent ou reprennent un élément déjà cité. Dans un texte, le pronom démonstratif (_celui, celle_) évite les répétitions : "
      "c'est un outil de cohésion apprécié à l'écrit."),
    P(REF.format(8, 40)),
], los={
    "a": "Choisir l'adjectif démonstratif (ce, cet, cette, ces) et les suffixes -ci / -là.",
    "b": "Employer les pronoms démonstratifs (celui, celle, ceux, celles) + de / qui / -ci / -là.",
})
c.module(1, "L'adjectif et le pronom démonstratifs", sections=[
    ("a", [
        TABLE(["", "masculin", "féminin"], ["singulier", "ce livre / **cet** ami, **cet** hôtel", "cette maison"], ["pluriel", "ces livres", "ces maisons"]),
        P("**Cet** devant un nom masculin commençant par une voyelle ou un _h_ muet. Pour distinguer deux éléments : _ce livre-**ci**_ (proche) / _ce livre-**là**_ (éloigné)."),
        NOTE("_Ce matin, cette semaine, cette année_ = le moment présent ; _ce jour-là, cette année-là_ = un moment passé ou futur précis."),
    ]),
    ("b", [
        TABLE(["", "masculin", "féminin"], ["singulier", "celui", "celle"], ["pluriel", "ceux", "celles"]),
        P("Le pronom démonstratif n'est jamais seul. Il est suivi de **-ci / -là**, de **de** + nom, ou d'un **relatif** :"),
        UL("_Quelle robe préfères-tu ? **Celle-ci** ou **celle-là** ?_", "_Ce n'est pas mon vélo, c'est **celui de** mon frère._",
           "_Les étudiants **qui** ont réussi et **ceux qui** ont échoué…_"),
    ]),
], chain=[
    ("assumption", "Le démonstratif désigne un élément précis, montré ou déjà mentionné."),
    ("mechanism", "L'adjectif (_ce, cet, cette, ces_) accompagne un nom ; le pronom (_celui, celle…_) le remplace."),
    ("result", "Le pronom se complète toujours par _-ci / -là_, _de_ ou une relative."),
], why="_Celui qui_, _ceux de_ sont des reprises élégantes qui évitent les répétitions dans un essai.",
  look=["le genre du nom et sa première lettre", "ce qui suit le pronom (-ci, de, qui)"],
  traps=["*_ce ami_", "*_celui_ employé seul", "_cette année_ / _cette année-là_"],
  distractors=["_ce_ devant voyelle", "la forme d'un autre genre ou nombre"],
  questions=[
    Q("a", 1, "form", "___ hôtel est complet tout l'été.", ("Cet", "Masculin + _h_ muet → _cet_."), [("Ce", "Devant une voyelle ou un _h_ muet → _cet_."), ("Cette", "_hôtel_ est masculin.")]),
    Q("a", 1, "form", "J'ai lu ___ articles avec beaucoup d'intérêt.", ("ces", "Pluriel → _ces_."), [("ses", "_ses_ est un possessif."), ("cettes", "Cette forme n'existe pas.")]),
    Q("a", 2, "conceptual", "Je me souviens bien de mon arrivée : ___, il neigeait.", ("ce jour-là", "Moment passé précis → _-là_."),
      [("ce jour-ci", "_-ci_ ne s'emploie pas pour un moment passé."), ("aujourd'hui", "Le récit porte sur un jour passé.")]),
    Q("b", 1, "form", "Quelle veste veux-tu ? ___ ou celle-là ?", ("Celle-ci", "_veste_ est féminin."), [("Celui-ci", "_veste_ est féminin."), ("Cette-ci", "Il faut le pronom _celle_.")]),
    Q("b", 2, "form", "Ma voiture est en panne, j'ai pris ___ de ma sœur.", ("celle", "_voiture_, féminin singulier, + _de_."),
      [("cette", "_cette_ doit être suivi d'un nom."), ("celui", "_voiture_ est féminin.")]),
    Q("b", 2, "form", "Les candidats qui ont un diplôme et ___ qui ont de l'expérience peuvent postuler.", ("ceux", "Masculin pluriel + _qui_."),
      [("celles", "_candidats_ est masculin."), ("ces", "_ces_ doit être suivi d'un nom.")]),
  ],
  cards=[R("celui", "b", "Pronoms démonstratifs", "Celui / celle / ceux / celles + ?", "toujours suivis de **-ci / -là**, de **de** + nom ou d'un **relatif** (_celui qui_).",
           mistake="*_Je prends celui._")])

# ================================================================ chapitre 9
c = b.chapter(9, "« Il y a » et « c'est »", focus=[
    P("_Il y a_ signale l'**existence** de quelque chose ; _c'est_ l'**identifie**. On les enchaîne souvent : _Il y a un musée. C'est le musée Rodin._"),
    P(REF.format(9, 42)),
], los={"a": "Distinguer _il y a_ (existence) et _c'est_ (identification), et leurs formes négatives."})
c.module(1, "L'existence et l'identification", sections=[
    ("a", [
        UL("**Il y a + un / une / des** : existence : _**Il y a** une pharmacie dans la rue._",
           "**C'est + le / la / un nom propre** : identification : _**C'est** la pharmacie de M. Morel._"),
        P("**Négation** : _il n'y a **pas de**_ (l'article devient _de_) mais _ce n'est **pas un / le**_ (l'article reste) :"),
        UL("_Il n'y a **pas de** pharmacie ici._", "_Ce n'est **pas une** pharmacie, c'est une parfumerie._"),
        NOTE("_Il y a_ est invariable : _**Il y a** des problèmes_ (jamais *_il y ont_)."),
    ]),
], chain=[
    ("assumption", "On signale d'abord qu'une chose existe, puis on dit ce qu'elle est."),
    ("mechanism", "_Il y a_ + indéfini pour l'existence ; _c'est_ + défini, nom propre ou indéfini pour l'identification."),
    ("result", "À la négation, _il n'y a pas **de**_, mais _ce n'est pas **un**_."),
], why="La négation _il n'y a pas de_ est très fréquente dans les descriptions et les lettres de réclamation.",
  look=["existence ou identification ?", "une négation"],
  traps=["*_il n'y a pas une_ (sens général)", "*_ce n'est pas de_"],
  distractors=["l'article indéfini gardé après _il n'y a pas_", "_c'est_ pour signaler l'existence"],
  questions=[
    Q("a", 1, "conceptual", "___ un bon restaurant au coin de la rue.", ("Il y a", "Existence → _il y a_."), [("C'est", "On signale l'existence, on n'identifie pas."), ("Il est", "_il est_ + nom indéfini n'est pas correct.")]),
    Q("a", 1, "conceptual", "Tu vois ce bâtiment ? ___ la nouvelle médiathèque.", ("C'est", "Identification → _c'est_."), [("Il y a", "On identifie le bâtiment."), ("Il est", "_il est_ ne se place pas devant un nom déterminé.")]),
    Q("a", 2, "form", "Dans ce village, il n'y a pas ___ école.", ("d'", "_il n'y a pas_ → _de / d'_."), [("une", "Après _il n'y a pas_, l'article indéfini devient _de_."), ("l'", "On nie l'existence : _de_.")]),
    Q("a", 2, "form", "Ce n'est pas ___ problème technique, c'est une erreur humaine.", ("un", "_ce n'est pas_ garde l'article."), [("de", "Après _ce n'est pas_, l'article ne change pas."), ("du", "_du_ est un partitif.")]),
    Q("a", 2, "form", "Il ___ beaucoup de touristes en été.", ("y a", "_il y a_ est invariable."), [("y ont", "_il y a_ ne se met jamais au pluriel."), ("est", "_il est beaucoup de_ n'est pas courant.")]),
  ],
  cards=[R("il-y-a", "a", "Il y a / c'est à la négation", "Négation de _il y a un_ / _c'est un_ ?", "_il n'y a pas **de**_ ; _ce n'est pas **un**_.")])

# ================================================================ chapitre 11
c = b.chapter(11, "Le verbe « avoir »", focus=[
    P("_Avoir_ exprime la possession, l'âge, les sensations (_avoir faim_) et de nombreuses expressions idiomatiques utiles (_avoir besoin, avoir l'habitude, avoir lieu_)."),
    P(REF.format(11, 48)),
], los={
    "a": "Conjuguer _avoir_ et l'employer pour l'âge et la description physique.",
    "b": "Employer les expressions avec _avoir_ et la négation _pas de_.",
})
c.module(1, "« Avoir » et ses expressions", sections=[
    ("a", [
        TABLE(["j'ai", "tu as", "il / elle / on a", "nous avons", "vous avez", "ils / elles ont"]),
        P("**Âge** : _J'**ai** trente ans_ (jamais *_je suis trente ans_). **Description** : _Elle **a** les yeux bleus, les cheveux longs._"),
    ]),
    ("b", [
        UL("Sensations : **avoir faim, soif, chaud, froid, sommeil, peur, mal (à la tête)**.",
           "Expressions : **avoir besoin de, avoir envie de, avoir l'habitude de, avoir raison / tort, avoir le temps de, avoir lieu** (= se dérouler)."),
        P("**Négation** : _J'ai **une** voiture → Je n'ai **pas de** voiture._ L'article indéfini et le partitif deviennent **de / d'**."),
        NOTE("Dans les expressions sans article (_avoir faim_), on garde la structure : _Je n'ai pas faim._ _Avoir besoin **de**_ + nom sans article : _J'ai besoin **d'**aide._"),
    ]),
], chain=[
    ("assumption", "_Avoir_ sert à beaucoup plus qu'à la possession : âge, sensations, habitudes."),
    ("mechanism", "Ces expressions n'ont pas d'article (_avoir faim, avoir lieu_) et se construisent souvent avec _de_."),
    ("result", "À la négation, _un / une / des / du_ deviennent _de_."),
], why="_Avoir lieu_, _avoir besoin de_, _avoir tendance à_ sont des expressions courantes des textes du DELF.",
  look=["âge, sensation ou expression figée ?", "une négation"],
  traps=["*_je suis 25 ans_", "*_je n'ai pas une voiture_", "*_le concert a place_"],
  distractors=["_être_ à la place d'_avoir_", "l'article gardé à la négation"],
  questions=[
    Q("a", 1, "form", "Ma grand-mère ___ quatre-vingt-dix ans.", ("a", "L'âge s'exprime avec _avoir_."), [("est", "*_elle est 90 ans_ est un calque d'autres langues."), ("fait", "_faire 90 ans_ n'est pas l'expression de l'âge.")]),
    Q("a", 1, "form", "Mes cousins ___ les cheveux roux.", ("ont", "_ils ont_."), [("sont", "On décrit avec _avoir les cheveux…_"), ("avons", "_avons_ va avec _nous_.")]),
    Q("a", 1, "form", "Elle ___ les yeux verts et les cheveux courts.", ("a", "Description physique → _avoir_."),
      [("est", "On décrit avec _avoir les yeux…_"), ("fait", "_faire_ ne s'emploie pas pour décrire.")]),
    Q("b", 1, "vocabulary", "Le festival ___ lieu chaque année en juillet.", ("a", "_avoir lieu_ = se dérouler."), [("prend", "_prendre lieu_ n'existe pas (calque de l'anglais)."), ("est", "_être lieu_ n'existe pas.")]),
    Q("b", 1, "vocabulary", "J'ai très ___ : il reste de l'eau ?", ("soif", "_avoir soif_ : besoin de boire."),
      [("sommeil", "_avoir sommeil_ : besoin de dormir, sans lien avec l'eau."), ("froid", "_avoir froid_ ne se soulage pas avec de l'eau.")]),
    Q("b", 2, "form", "Nous n'avons pas ___ enfants.", ("d'", "Négation : _des_ → _d'_."), [("des", "Après la négation, _des_ devient _de / d'_."), ("les", "On ne parle pas d'enfants précis.")]),
    Q("b", 2, "vocabulary", "Tu ___ raison : il vaut mieux partir tôt.", ("as", "_avoir raison_."), [("es", "*_être raison_ n'existe pas."), ("fais", "*_faire raison_ n'existe pas.")]),
  ],
  cards=[R("expr-avoir", "b", "Expressions avec avoir", "avoir … lieu / besoin / l'habitude / raison ?",
           "**avoir lieu** = se dérouler ; **avoir besoin de** ; **avoir l'habitude de** ; **avoir raison / tort**.", mistake="*_prendre place_ pour _avoir lieu_.")])

# ================================================================ chapitre 13
c = b.chapter(13, "Les nombres", focus=[
    P("Les nombres sont partout dans les documents du DELF (statistiques, dates, prix). Il faut savoir les lire, les écrire et les ordonner."),
    P(REF.format(13, 58)),
], los={
    "a": "Lire et écrire les nombres cardinaux (accords de _vingt, cent, mille_).",
    "b": "Former les nombres ordinaux et les fractions courantes.",
})
c.module(1, "Cardinaux et ordinaux", sections=[
    ("a", [
        P("70 = **soixante-dix**, 80 = **quatre-vingts**, 90 = **quatre-vingt-dix** (en Belgique et en Suisse : _septante, (huitante), nonante_)."),
        UL("**Vingt** et **cent** prennent un **s** quand ils sont multipliés et **en fin de nombre** : _quatre-vingt**s**, deux cent**s**_ ; mais _quatre-vingt-trois, deux cent dix_.",
           "**Mille** est invariable : _trois **mille**_. **Million, milliard** sont des noms : _deux million**s** **d'**habitants_.",
           "Trait d'union entre tous les éléments (orthographe de 1990) ou seulement sous cent : _vingt-et-un_ / _vingt et un_."),
    ]),
    ("b", [
        P("**Ordinaux** : nombre + **-ième** : _deux → deuxième, cinq → cinq**u**ième, neuf → neu**v**ième_. Exceptions : **premier / première**, _second(e)_."),
        P("**Fractions** : _un **demi**, un **tiers**, un **quart**_, puis _un cinquième, deux tiers, trois quarts_. **La moitié** (50 %)."),
        NOTE("Pour les dates et les rois, on utilise le cardinal, sauf pour _premier_ : _le **1er** mai, le **2** mai ; François **Ier**, Louis **XIV** (quatorze)_."),
    ]),
], chain=[
    ("assumption", "Le système français mélange base 10 et base 20 (_quatre-vingts_)."),
    ("mechanism", "_Vingt_ et _cent_ ne prennent un _s_ qu'en fin de nombre et multipliés ; _mille_ ne varie jamais ; _million_ est un nom."),
    ("result", "Les ordinaux se forment avec _-ième_ ; les fractions courantes ont des noms propres (_tiers, quart, moitié_)."),
], why="Les questions sur des données chiffrées reformulées (_un tiers, la moitié_) sont fréquentes en compréhension écrite et orale.",
  look=["la position de _vingt / cent_ dans le nombre", "_mille_ et _million_"],
  traps=["*_trois milles_", "*_deux cent trente_ avec _cents_", "_un tiers_ ≠ _30 %_ exactement"],
  distractors=["un accord en _s_ fautif", "une fraction mal reformulée"],
  questions=[
    Q("a", 1, "form", "Ce vélo coûte ___ euros (80 €).", ("quatre-vingts", "_vingt_ multiplié et en fin de nombre → _s_."),
      [("quatre-vingt", "En fin de nombre, _quatre-vingts_ prend un _s_."), ("huitante", "_huitante_ ne s'emploie qu'en Suisse.")]),
    Q("a", 2, "form", "La ville compte ___ habitants (3 000).", ("trois mille", "_mille_ est invariable."), [("trois milles", "_mille_ ne prend jamais de _s_."), ("trois millier", "_un millier_ est un nom approximatif.")]),
    Q("a", 2, "form", "Le pays compte deux ___ habitants.", ("millions d'", "_million_ est un nom : _s_ au pluriel + _de_."),
      [("million", "_million_ est un nom : il prend un _s_ et se construit avec _de_."), ("millions", "Il manque _d'_ devant le nom.")]),
    Q("a", 3, "form", "Le livre fait ___ pages (280).", ("deux cent quatre-vingts", "_cent_ suivi d'un autre nombre → pas de _s_ ; _quatre-vingts_ final → _s_."),
      [("deux cents quatre-vingts", "_cent_ ne prend pas de _s_ s'il est suivi d'un nombre."), ("deux cent quatre-vingt", "_quatre-vingts_ en fin de nombre prend un _s_.")]),
    Q("b", 1, "form", "Elle est arrivée ___ au marathon de Paris (9e).", ("neuvième", "_neuf → neuvième_."), [("neufième", "Le _f_ devient _v_."), ("neuvième fois", "On demande un rang, pas une fréquence.")]),
    Q("b", 2, "vocabulary", "« 25 % des Français » signifie…", ("un quart des Français.", "25 % = un quart."), [("un tiers des Français.", "Un tiers ≈ 33 %."), ("la moitié des Français.", "La moitié = 50 %.")]),
    Q("b", 2, "vocabulary", "« Près des deux tiers des sondés » correspond à…", ("environ 66 %.", "2/3 ≈ 66 %."), [("environ 23 %.", "Confusion entre _deux tiers_ et le nombre 2."), ("environ 75 %.", "75 % = trois quarts.")]),
  ],
  cards=[R("vingt-cent", "a", "Accord de vingt, cent, mille", "Quand vingt et cent prennent-ils un s ?", "Multipliés **et** en fin de nombre : _quatre-vingts, trois cents_ ; _mille_ est invariable.",
           examples=["quatre-vingt-deux ; trois cent dix ; deux mille"]),
         R("fractions", "b", "Fractions", "1/2, 1/3, 1/4, 2/3, 3/4 ?", "un demi (la moitié), un tiers, un quart, deux tiers, trois quarts.")])

b.write()
