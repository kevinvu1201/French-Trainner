from fr import NOTE, P, Q, R, S, TABLE, UL, Book

b = Book("espace_temps")
REF = "Repère : _Grammaire progressive du français_, chapitre {} (p. {})."

# ================================================================ chapitre 10
c = b.chapter(10, "La situation dans l'espace (1) : villes et pays", focus=[
    P("Les prépositions de lieu (_à Paris, en France, au Japon, aux États-Unis_) dépendent du genre et du nombre du pays. "
      "Les erreurs sont fréquentes et très visibles, même au niveau B2."),
    P(REF.format(10, 44)),
], los={
    "a": "Choisir _à, en, au, aux_ devant une ville, un pays ou un continent.",
    "b": "Employer les expressions de lieu courantes (_dans, sur, sous, à côté de, en face de…_).",
})
c.module(1, "Villes, pays, continents et expressions de lieu", sections=[
    ("a", [
        TABLE(["Destination", "Préposition", "Exemples"],
              ["ville", "**à**", "à Paris, à Londres, à New York"],
              ["pays féminin (souvent en -e) ou à voyelle", "**en**", "en France, en Italie, en Iran, en Israël"],
              ["pays masculin à consonne", "**au**", "au Japon, au Canada, au Mexique, au Portugal"],
              ["pays pluriel", "**aux**", "aux États-Unis, aux Pays-Bas, aux Philippines"],
              ["continent", "**en**", "en Europe, en Asie, en Afrique"]),
        NOTE("Exceptions masculines en _-e_ : _**au** Mexique, **au** Cambodge, **au** Mozambique_. Îles : souvent **à** (_à Cuba, à Madagascar_), parfois **en** (_en Corse, en Sicile_)."),
    ]),
    ("b", [
        UL("**dans** (à l'intérieur) / **sur** (à la surface) / **sous** (en dessous) : _dans le tiroir, sur la table, sous le lit_.",
           "**devant / derrière, à côté de, en face de, près de / loin de, au-dessus de / au-dessous de, entre … et …**",
           "**dans la rue** / **sur la place, sur le boulevard, sur l'avenue** ; **à la campagne, à la montagne, à la mer**."),
        NOTE("Avec _de_ : _à côté **du** métro, près **des** gares_ (contraction obligatoire)."),
    ]),
], chain=[
    ("assumption", "La préposition devant un nom de lieu dépend du type de lieu (ville, pays, continent)."),
    ("mechanism", "Ville → _à_ ; pays féminin ou à voyelle et continent → _en_ ; pays masculin → _au_ ; pays pluriel → _aux_."),
    ("result", "Les locutions de lieu en _de_ (_à côté de, près de_) se contractent avec _le / les_."),
], why="Ces prépositions apparaissent dans toutes les tâches de présentation et de récit de voyage.",
  look=["ville ou pays ?", "le genre et le nombre du pays", "une locution en _de_"],
  traps=["*_en Japon_", "*_au France_", "*_à côté de le métro_"],
  distractors=["_en_ pour un pays masculin", "_à_ pour un pays", "la locution sans contraction"],
  questions=[
    Q("a", 1, "form", "Mes parents habitent ___ Portugal depuis leur retraite.", ("au", "Pays masculin à consonne → _au_."), [("en", "_Portugal_ est masculin."), ("à", "_à_ s'emploie avec une ville.")]),
    Q("a", 1, "form", "Elle fait ses études ___ Allemagne.", ("en", "Pays féminin → _en_."), [("au", "_Allemagne_ est féminin."), ("à l'", "On n'emploie pas _à l'_ devant un pays.")]),
    Q("a", 2, "form", "Nous partons trois semaines ___ États-Unis.", ("aux", "Pays pluriel → _aux_."), [("en", "_États-Unis_ est pluriel."), ("au", "_États-Unis_ est pluriel.")]),
    Q("a", 2, "form", "Il a passé un an ___ Mexique.", ("au", "Exception : _le Mexique_ est masculin → _au_."), [("en", "_Mexique_ est masculin malgré le _e_ final."), ("à", "_à_ s'emploie avec une ville.")]),
    Q("a", 2, "form", "Ils ont déménagé ___ Iran pour le travail.", ("en", "Pays masculin à voyelle → _en_."), [("au", "Devant une voyelle, on emploie _en_."), ("à l'", "On n'emploie pas _à l'_ devant un pays.")]),
    Q("b", 1, "conceptual", "J'ai laissé mes clés ___ la table de la cuisine.", ("sur", "À la surface → _sur_."), [("dans", "_dans_ = à l'intérieur."), ("en", "_en_ ne s'emploie pas avec _la table_.")]),
    Q("b", 2, "form", "L'hôtel se trouve juste à côté ___ musée.", ("du", "_à côté de + le_ → _du_."), [("de le", "_de + le_ se contracte."), ("au", "La locution est _à côté de_.")]),
    Q("b", 2, "conceptual", "Le marché a lieu ___ la place de la Mairie.", ("sur", "On dit _sur la place_."), [("dans", "On dit _dans la rue_, mais _sur la place_."), ("à", "_à la place de_ signifie _au lieu de_.")]),
  ],
  cards=[R("pays", "a", "Prépositions de pays", "à / en / au / aux ?", "ville → **à** ; pays féminin ou à voyelle, continent → **en** ; pays masculin → **au** ; pluriel → **aux**.",
           examples=["à Rome, en Italie, au Japon, aux États-Unis"], mistake="_au Mexique, au Cambodge_ (masculins en -e).")])

# ================================================================ chapitre 14
c = b.chapter(14, "Le temps (1) : date, heure, saisons", focus=[
    P("Situer un événement dans le temps (date, jour, heure, saison) est indispensable pour une lettre, un récit ou une invitation."),
    P(REF.format(14, 64)),
], los={
    "a": "Exprimer la date, le jour et la saison (le, en, au).",
    "b": "Dire l'heure et parler de la météo.",
})
c.module(1, "Le jour, la date, l'heure et le temps qu'il fait", sections=[
    ("a", [
        UL("**Date** : _le 14 juillet_, _le **1er** mai_ (premier), _le lundi 3 mars_. Pas de préposition : _Je pars **le** 3 mars_.",
           "**Jour habituel** : _**le** lundi_ = tous les lundis ; _lundi_ = ce lundi-ci.",
           "**Mois et années** : _**en** mars, **au mois de** mars, **en** 2026_.",
           "**Saisons** : _**en** été, **en** automne, **en** hiver_, mais _**au** printemps_."),
    ]),
    ("b", [
        P("**L'heure** : _Il est **huit heures et quart**, **huit heures et demie**, **neuf heures moins le quart**, **midi**, **minuit**_. Langue officielle : _20 h 45_ (vingt heures quarante-cinq)."),
        P("**Météo** : _**Il fait** beau / chaud / froid / 20 degrés. **Il pleut. Il neige. Il y a** du vent, du soleil, du brouillard_."),
        NOTE("_Midi et **demi**_ (_midi_ est masculin) mais _une heure et **demie**_ (_heure_ est féminin)."),
    ]),
], chain=[
    ("assumption", "Chaque unité de temps a sa préposition propre."),
    ("mechanism", "Date et jour → _le_ (sans préposition) ; mois, année et saisons → _en_, sauf _au printemps_."),
    ("result", "L'heure et la météo se disent avec des tournures impersonnelles (_il est, il fait, il pleut_)."),
], why="Dates et horaires sont présents dans presque tous les documents d'écoute et dans les lettres.",
  look=["date, mois, année ou saison ?", "_le lundi_ (habitude) / _lundi_ (ce lundi)"],
  traps=["*_en printemps_", "*_le un mai_", "*_il est beau_ pour la météo"],
  distractors=["_en_ avec _printemps_", "une préposition devant une date"],
  questions=[
    Q("a", 1, "form", "Les cours reprennent ___ septembre.", ("en", "Mois → _en_."), [("au", "_au_ s'emploie avec _au mois de_."), ("le", "_le_ s'emploie avec une date précise.")]),
    Q("a", 1, "form", "Nous allons au Japon ___ printemps.", ("au", "_au printemps_ (exception)."), [("en", "On dit _en été, en automne, en hiver_, mais _au printemps_."), ("dans le", "Ce n'est pas la tournure habituelle.")]),
    Q("a", 2, "conceptual", "Le musée est fermé ___ mardi : tous les mardis.", ("le", "_le mardi_ = tous les mardis."), [("au", "_au mardi_ n'existe pas."), ("en", "_en_ ne s'emploie pas avec les jours.")]),
    Q("a", 2, "form", "La fête du Travail a lieu le ___ mai.", ("1er", "On dit _le premier mai_ (ordinal pour le 1er seulement)."), [("un", "Le premier jour du mois → _premier_."), ("1", "On écrit _1er_ pour le premier jour du mois.")]),
    Q("b", 1, "form", "Rendez-vous à une heure et ___ devant le cinéma.", ("demie", "_heure_ est féminin → _et demie_."), [("demi", "Avec _heure_ (féminin) → _demie_."), ("moitié", "On dit _et demie_.")]),
    Q("b", 1, "form", "Prends un parapluie : il ___ depuis ce matin.", ("pleut", "_il pleut_ (verbe _pleuvoir_)."), [("fait pluie", "On dit _il pleut_."), ("est pluvieux", "On ne dit pas _il est pluvieux_ pour la météo.")]),
    Q("b", 2, "form", "Aujourd'hui, ___ vingt-cinq degrés à Marseille.", ("il fait", "Température → _il fait_."), [("il est", "_il est_ s'emploie pour l'heure."), ("il a", "_il a_ ne s'emploie pas pour la météo.")]),
  ],
  cards=[R("saisons", "a", "Saisons", "Préposition des saisons ?", "**en** été, **en** automne, **en** hiver, mais **au** printemps.")])

# ================================================================ chapitre 17
c = b.chapter(17, "Le temps (2) : la durée", focus=[
    P("_Depuis, pour, pendant, en, il y a_ : ces mots expriment des durées différentes et ne sont pas interchangeables. "
      "Leur confusion est une des fautes les plus fréquentes des apprenants avancés."),
    P(REF.format(17, 80)),
], los={"a": "Choisir entre _depuis, pendant, pour, en_ et _il y a_ pour exprimer une durée."})
c.module(1, "« Depuis », « pour », « pendant », « en »", sections=[
    ("a", [
        UL("**depuis** + durée ou point de départ, avec un verbe au **présent** : action qui continue : _J'habite ici **depuis** trois ans / **depuis** 2020._",
           "**pendant** : durée d'une action **terminée** (ou délimitée) : _J'ai habité à Rome **pendant** trois ans._",
           "**pour** : durée **prévue** (avec _partir, aller, venir_) : _Je pars **pour** une semaine._",
           "**en** : temps **nécessaire** pour accomplir une action : _J'ai lu ce livre **en** deux jours._",
           "**il y a** + durée, avec un verbe au **passé** : moment d'un événement passé : _Je suis arrivé **il y a** deux ans._"),
        NOTE("**Ça fait / il y a … que** + présent = _depuis_ : _**Ça fait** trois ans **que** j'habite ici._"),
    ]),
], chain=[
    ("assumption", "Toutes ces expressions parlent de temps, mais pas du même temps : continuité, durée close, prévision, rapidité, moment passé."),
    ("mechanism", "_Depuis_ + présent (ça continue) ; _pendant_ (durée close) ; _pour_ (prévue) ; _en_ (temps nécessaire) ; _il y a_ + passé (moment)."),
    ("result", "Le temps du verbe confirme le choix : présent avec _depuis_, passé avec _il y a_."),
], why="Les questions sur la durée (_depuis quand ? pendant combien de temps ?_) sont fréquentes en compréhension orale.",
  look=["le temps du verbe", "l'action continue-t-elle ?", "durée prévue ou nécessaire ?"],
  traps=["*_J'habite ici pour trois ans_ (anglais _for_)", "*_depuis_ avec un passé composé ponctuel", "_il y a_ (moment) / _depuis_ (durée)"],
  distractors=["_pour_ au sens de l'anglais _for_", "_pendant_ pour une action qui continue"],
  questions=[
    Q("a", 1, "conceptual", "J'apprends le français ___ deux ans et je continue.", ("depuis", "L'action continue au présent → _depuis_."),
      [("pendant", "_pendant_ s'emploie pour une durée terminée."), ("pour", "_pour_ indique une durée prévue.")]),
    Q("a", 1, "conceptual", "Ils sont partis en Australie ___ six mois : ils rentrent en juin.", ("pour", "Durée prévue avec _partir_ → _pour_."),
      [("depuis", "_depuis_ demande une action qui continue au présent."), ("en", "_en_ indique le temps nécessaire.")]),
    Q("a", 2, "conceptual", "Elle a vécu à Tokyo ___ cinq ans, puis elle est rentrée en France.", ("pendant", "Durée close dans le passé → _pendant_."),
      [("depuis", "L'action est terminée : pas de _depuis_."), ("il y a", "_il y a_ indique un moment, pas une durée.")]),
    Q("a", 2, "conceptual", "Le nouveau pont a été construit ___ dix-huit mois seulement.", ("en", "Temps nécessaire pour réaliser l'action → _en_."),
      [("depuis", "_depuis_ demande une action qui continue au présent."), ("pour", "_pour_ indique une durée prévue.")]),
    Q("a", 2, "conceptual", "J'ai rencontré mon mari ___ dix ans, à Lyon.", ("il y a", "Moment d'un événement passé → _il y a_."),
      [("depuis", "La rencontre est un événement ponctuel et terminé."), ("pendant", "On donne un moment, pas une durée.")]),
    Q("a", 3, "conceptual", "Ça fait trois heures ___ je t'attends !", ("que", "_Ça fait + durée + que_ + présent."), [("depuis", "La structure est _ça fait … que_."), ("pendant", "La structure est _ça fait … que_.")]),
  ],
  cards=[R("duree", "a", "Depuis / pendant / pour / en / il y a", "Quelle préposition de durée ?",
           "**depuis** (ça continue, présent) ; **pendant** (durée close) ; **pour** (durée prévue) ; **en** (temps nécessaire) ; **il y a** (moment passé).",
           examples=["J'habite ici depuis 3 ans. J'ai vécu à Rome pendant 3 ans. Je pars pour 3 jours. J'ai fini en 3 heures. Je suis arrivé il y a 3 ans."])])

# ================================================================ chapitre 21
c = b.chapter(21, "La situation dans l'espace (2) : régions et origine", focus=[
    P("Les régions, départements et l'origine géographique (_je viens du Japon, d'Italie_) suivent les mêmes règles que les pays, avec _de_ en plus."),
    P(REF.format(21, 94)),
], los={
    "a": "Situer dans une région ou un département (_en Bretagne, dans le Nord_).",
    "b": "Exprimer l'origine avec _de, d', du, des_.",
})
c.module(1, "Régions, départements et origine géographique", sections=[
    ("a", [
        UL("Régions féminines → **en** : _en Normandie, en Provence, en Bourgogne_.",
           "Régions et départements masculins → **dans le** : _dans le Nord, dans le Var, dans le Midi_ (parfois _en_ devant voyelle : _en Anjou_).",
           "États et provinces : _**au** Québec, **en** Californie, **au** Texas, **dans l'**Ontario_."),
    ]),
    ("b", [
        TABLE(["Destination", "Origine"],
              ["à Paris", "**de** Paris"], ["en France, en Iran", "**de** France, **d'**Iran"], ["au Japon", "**du** Japon"], ["aux États-Unis", "**des** États-Unis"]),
        P("_Je viens **de** Lyon. Ce vin vient **d'**Italie. Elle rentre **du** Canada. Il arrive **des** Pays-Bas._"),
    ]),
], chain=[
    ("assumption", "L'origine se marque avec _de_, comme la destination avec _à / en / au_."),
    ("mechanism", "Pays féminin → _de / d'_ sans article ; pays masculin → _du_ ; pays pluriel → _des_."),
    ("result", "Les régions masculines se construisent souvent avec _dans le_."),
], why="Présenter son parcours (_je viens de…, j'ai vécu en…_) ouvre l'épreuve orale du DELF.",
  look=["destination ou origine ?", "le genre et le nombre du lieu"],
  traps=["*_je viens de la France_", "*_je viens de Japon_"],
  distractors=["l'article gardé après _de_ devant un pays féminin", "_de_ sans article devant un pays masculin"],
  questions=[
    Q("a", 1, "form", "Nous passons nos vacances ___ Bretagne.", ("en", "Région féminine → _en_."), [("au", "_Bretagne_ est féminin."), ("dans", "Devant une région féminine, on emploie _en_.")]),
    Q("a", 2, "form", "Ils ont acheté une maison ___ Var.", ("dans le", "Département masculin → _dans le_."), [("en", "Le _Var_ est masculin."), ("au", "On dit plutôt _dans le Var_.")]),
    Q("b", 1, "form", "Cet étudiant vient ___ Japon.", ("du", "Pays masculin → _du_."), [("de", "Devant un pays masculin, on emploie _du_."), ("de le", "_de + le_ se contracte en _du_.")]),
    Q("b", 1, "form", "Ce café vient ___ Colombie.", ("de", "Pays féminin → _de_ sans article."), [("de la", "Après _venir de_, on omet l'article devant un pays féminin."), ("du", "_Colombie_ est féminin.")]),
    Q("b", 2, "form", "Ma collègue rentre ___ États-Unis demain.", ("des", "Pays pluriel → _des_."), [("de", "_États-Unis_ est pluriel : _des_."), ("aux", "_aux_ indique la destination.")]),
    Q("b", 2, "form", "Mon voisin est originaire ___ Équateur.", ("d'", "Pays masculin à voyelle → _d'_."), [("du", "Devant une voyelle, _de l'_ / _d'_ : on dit _d'Équateur_ ou _de l'Équateur_."), ("en", "_en_ indique la destination.")]),
  ],
  cards=[R("origine", "b", "L'origine", "Je viens ___ France / Japon / États-Unis ?", "**de** France, **du** Japon, **des** États-Unis.")])

# ================================================================ chapitre 25
c = b.chapter(25, "La situation dans l'espace et le temps (3) : à, de, jusqu'à", focus=[
    P("_De … à_, _jusqu'à_, _à partir de_ délimitent un trajet ou une période : horaires, itinéraires, périodes d'ouverture."),
    P(REF.format(25, 106)),
], los={"a": "Exprimer le point de départ, la limite et l'intervalle (de … à, jusqu'à, à partir de, dès)."})
c.module(1, "« À », « de », « jusqu'à », « à partir de »", sections=[
    ("a", [
        UL("**de … à** : intervalle : _**de** 9 h **à** 18 h, **de** Paris **à** Lyon, **du** lundi **au** vendredi_.",
           "**jusqu'à** : limite : _Le magasin est ouvert **jusqu'à** 20 h. Allez **jusqu'au** carrefour._",
           "**à partir de** : point de départ (futur ou habituel) : _**À partir de** demain, le métro sera gratuit._",
           "**dès** : point de départ immédiat, souvent plus tôt que prévu : _**Dès** son arrivée, il s'est mis au travail._"),
        NOTE("Contractions : _**du** 1er **au** 15 mai, **jusqu'aux** vacances, **à partir du** mois prochain_."),
    ]),
], chain=[
    ("assumption", "Un intervalle a un début et une fin, dans l'espace comme dans le temps."),
    ("mechanism", "_De_ marque le début, _à_ et _jusqu'à_ la fin ; _à partir de_ et _dès_ insistent sur le point de départ."),
    ("result", "Les contractions (_du, au, jusqu'au_) s'appliquent comme ailleurs."),
], why="Horaires et périodes (_du … au …_, _à partir de_) sont au cœur des documents informatifs écoutés au DELF.",
  look=["début, fin ou intervalle ?", "un article à contracter"],
  traps=["*_de lundi à vendredi_ avec article manquant à l'écrit", "*_jusqu'à le_"],
  distractors=["la forme non contractée", "_depuis_ à la place de _à partir de_ pour le futur"],
  questions=[
    Q("a", 1, "form", "La bibliothèque est ouverte ___ lundi au samedi.", ("du", "_de + le lundi_ → _du_."), [("de le", "_de + le_ se contracte."), ("le", "Il faut _de … à_ pour un intervalle.")]),
    Q("a", 1, "form", "Continuez tout droit ___ feu rouge.", ("jusqu'au", "_jusqu'à + le_ → _jusqu'au_."), [("jusqu'à le", "_à + le_ se contracte."), ("depuis le", "On indique une limite, pas un point de départ.")]),
    Q("a", 2, "conceptual", "___ 1er janvier, les sacs plastiques seront interdits.", ("À partir du", "Point de départ dans le futur → _à partir de_."),
      [("Depuis le", "_depuis_ s'emploie pour une situation qui a déjà commencé."), ("Jusqu'au", "On annonce un début, pas une limite.")]),
    Q("a", 2, "conceptual", "___ les premiers symptômes, consultez un médecin.", ("Dès", "Point de départ immédiat → _dès_."), [("Jusqu'à", "On veut agir immédiatement, pas attendre une limite."), ("Pendant", "_pendant_ indique une durée.")]),
  ],
  cards=[R("intervalle", "a", "Intervalles", "Du … au, jusqu'à, à partir de, dès ?", "**du** lundi **au** vendredi ; **jusqu'à** 20 h ; **à partir de** demain ; **dès** l'arrivée (immédiatement).")])

# ================================================================ chapitre 41
c = b.chapter(41, "Le temps (3) : origine, chronologie, succession", focus=[
    P("Raconter, c'est ordonner : _d'abord, ensuite, avant de, après avoir, la veille, le lendemain_. "
      "Ces indicateurs donnent de la cohérence au récit et à l'argumentation."),
    P(REF.format(41, 198)),
], los={
    "a": "Exprimer l'origine et la durée au passé (_depuis, il y a, ça faisait … que_).",
    "b": "Ordonner des actions (_d'abord, ensuite, avant de + infinitif, après + infinitif passé_).",
    "c": "Situer par rapport à un moment de référence (_la veille, le lendemain, ce jour-là_).",
})
c.module(1, "L'origine, la chronologie et la succession", sections=[
    ("a", [
        P("Au passé, la durée d'une action en cours se dit avec **depuis** + **imparfait** : _Il **attendait depuis** une heure quand le train est arrivé._ "
          "Ou : _**Ça faisait / il y avait** une heure **qu'**il attendait._"),
        P("_**Depuis que** + indicatif_ : point de départ exprimé par une proposition : _**Depuis qu'**il travaille à Paris, il ne prend plus sa voiture._"),
    ]),
    ("b", [
        UL("Ordonner : **d'abord / tout d'abord, puis, ensuite, après, enfin, finalement**.",
           "**avant de + infinitif** (même sujet) : _Lisez la consigne **avant de** répondre._",
           "**après + infinitif passé** (même sujet) : _**Après avoir lu** la consigne, répondez._ / _**Après être arrivé**, il a appelé._",
           "Sujets différents : **avant que + subjonctif**, **après que + indicatif** : _Partez avant qu'il (ne) pleuve. Après qu'il est parti, nous avons rangé._"),
    ]),
    ("c", [
        TABLE(["Par rapport à aujourd'hui", "Par rapport à un autre moment"],
              ["hier", "**la veille**"], ["demain", "**le lendemain**"], ["avant-hier / après-demain", "**l'avant-veille / le surlendemain**"],
              ["aujourd'hui / maintenant", "**ce jour-là / à ce moment-là**"], ["la semaine dernière / prochaine", "**la semaine précédente / suivante**"]),
        NOTE("Ces équivalences sont indispensables au **discours rapporté au passé** (chapitre 45) : _« Je pars demain » → Il a dit qu'il partait **le lendemain**._"),
    ]),
], chain=[
    ("assumption", "Un récit suppose un ordre des actions et un moment de référence."),
    ("mechanism", "Les connecteurs (_d'abord, ensuite_) et les infinitives (_avant de, après avoir_) ordonnent ; _la veille, le lendemain_ situent par rapport à un moment passé."),
    ("result", "_Après_ + infinitif **passé** ; _avant de_ + infinitif présent ; _avant que_ + subjonctif mais _après que_ + indicatif."),
], why="La cohérence chronologique est un critère explicite de la grille de production écrite du DELF.",
  look=["même sujet ou sujets différents ?", "un moment de référence passé"],
  traps=["*_après manger_", "*_après qu'il soit parti_ (subjonctif)", "_demain_ dans un récit passé"],
  distractors=["l'infinitif présent après _après_", "_hier / demain_ au lieu de _la veille / le lendemain_"],
  questions=[
    Q("a", 2, "form", "Quand je suis arrivé, elle m'attendait ___ une demi-heure.", ("depuis", "Action en cours au passé → _depuis_ + imparfait."),
      [("pendant", "_pendant_ indique une durée terminée."), ("il y a", "_il y a_ indique un moment, pas une durée en cours.")]),
    Q("a", 3, "form", "___ elle fait du yoga, elle dort beaucoup mieux.", ("Depuis qu'", "_depuis que_ + proposition au présent."),
      [("Depuis", "Devant une proposition (sujet + verbe), il faut _depuis que_."), ("Il y a qu'", "Cette structure n'existe pas.")]),
    Q("b", 1, "form", "Relisez votre texte avant ___ le rendre.", ("de", "_avant de_ + infinitif."), [("que", "_avant que_ demande un sujet et un verbe conjugué."), ("à", "La locution est _avant de_.")]),
    Q("b", 2, "form", "Après ___ ses études, il est parti travailler au Canada.", ("avoir terminé", "_après_ + infinitif passé."), [("terminer", "Après _après_, l'infinitif doit être au passé."), ("avoir terminer", "Le participe passé est _terminé_.")]),
    Q("b", 2, "form", "Après ___ à l'hôtel, nous sommes allés dîner.", ("être arrivés", "Infinitif passé avec _être_ (_arriver_), accordé avec _nous_."),
      [("avoir arrivé", "_arriver_ se conjugue avec _être_."), ("arriver", "Il faut l'infinitif passé.")]),
    Q("b", 3, "form", "Après que tout le monde ___, la réunion a commencé.", ("est arrivé", "_après que_ + indicatif."), [("soit arrivé", "_après que_ est suivi de l'indicatif (fait accompli)."), ("arrive", "La concordance demande un temps accompli.")]),
    Q("c", 2, "vocabulary", "Il est arrivé le 3 mai et il est reparti ___, le 4.", ("le lendemain", "Le jour suivant un moment passé → _le lendemain_."),
      [("demain", "_demain_ se réfère à aujourd'hui, pas à un moment passé."), ("la veille", "_la veille_ = le jour précédent.")]),
    Q("c", 2, "vocabulary", "Elle s'est mariée le 10 juin ; ___, elle avait fait une grande fête avec ses amies.", ("la veille", "Le jour précédent un moment passé → _la veille_."),
      [("hier", "_hier_ se réfère à aujourd'hui."), ("le lendemain", "La fête précède le mariage (_avait fait_).")]),
  ],
  sets=[S("Un premier jour de stage",
    "Inès raconte :\n\n« **(1)** ___ arriver au bureau, j'avais relu toutes mes notes. **(2)** ___ avoir rencontré l'équipe, j'ai reçu mon ordinateur. "
    "J'étais très stressée : **(3)** ___, j'avais à peine dormi. Mais tout s'est bien passé, et **(4)** ___, ma tutrice m'a confié mon premier dossier. »",
    [Q("b", 1, "form", "Blanc (1) :", ("Avant d'", "_avant de_ + infinitif présent (même sujet)."), [("Après", "La relecture précède l'arrivée (_j'avais relu_)."), ("Avant que d'", "_avant que_ demande un verbe conjugué.")]),
     Q("b", 2, "form", "Blanc (2) :", ("Après", "_après_ + infinitif passé (_avoir rencontré_)."), [("Avant de", "_avant de_ est suivi de l'infinitif présent."), ("Depuis", "_depuis_ ne se construit pas avec l'infinitif.")]),
     Q("c", 2, "vocabulary", "Blanc (3) :", ("la veille", "La nuit précédant ce jour-là."), [("hier", "Le récit est au passé : _hier_ ne convient pas."), ("le lendemain", "L'insomnie précède le premier jour.")]),
     Q("c", 2, "vocabulary", "Blanc (4) :", ("le lendemain", "Le jour suivant, dans un récit passé."), [("demain", "_demain_ se réfère au présent."), ("la veille", "Le dossier arrive après le premier jour.")])])],
  cards=[R("veille", "c", "La veille / le lendemain", "Hier / demain dans un récit passé ?", "**la veille** / **le lendemain** ; _aujourd'hui → ce jour-là_."),
         R("apres-avoir", "b", "Avant de / après avoir", "Avant de … / après … + ?", "**avant de** + infinitif présent ; **après** + infinitif **passé** (_après avoir mangé, après être parti_).", mistake="*_après manger_.")])

b.write()
