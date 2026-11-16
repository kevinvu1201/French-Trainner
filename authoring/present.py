from fr import NOTE, P, Q, R, S, TABLE, UL, Book

b = Book("present")
REF = "Repère : _Grammaire progressive du français_, chapitre {} (p. {})."

# ================================================================ chapitre 16
c = b.chapter(16, "Les verbes en « -er » au présent", focus=[
    P("Les verbes en _-er_ représentent 90 % des verbes français. Leurs terminaisons sont régulières, mais l'orthographe du radical varie "
      "(_j'achète, j'appelle, nous mangeons, nous commençons_)."),
    P(REF.format(16, 74)),
], los={
    "a": "Conjuguer les verbes en _-er_ au présent.",
    "b": "Appliquer les changements orthographiques (-ger, -cer, -yer, -eler, -eter, e/è, é/è).",
})
c.module(1, "Conjugaison, prononciation et orthographe", sections=[
    ("a", [
        TABLE(["parler", "", "aimer", ""], ["je parl**e**", "nous parl**ons**", "j'aim**e**", "nous aim**ons**"],
              ["tu parl**es**", "vous parl**ez**", "tu aim**es**", "vous aim**ez**"], ["il parl**e**", "ils parl**ent**", "il aim**e**", "ils aim**ent**"]),
        P("_-e, -es, -e, -ent_ ne se prononcent pas : _je parle, tu parles, il parle, ils parlent_ se disent de la même façon."),
    ]),
    ("b", [
        UL("**-ger** : _nous mang**e**ons_ (le _e_ garde le son [ʒ]). **-cer** : _nous commen**ç**ons_.",
           "**-yer** : _y → i_ devant un _e_ muet : _je paie, j'envoie, il nettoie_ (mais _nous payons_).",
           "**e → è** (_acheter, lever, peser_) : _j'ach**è**te, nous achetons_. **é → è** (_préférer, espérer, répéter_) : _je préf**è**re, nous préférons_.",
           "**-eler / -eter** : consonne doublée devant _e_ muet : _j'appe**ll**e, je je**tt**e_ (mais _nous appelons, nous jetons_)."),
        NOTE("Les changements ne touchent que les personnes où la terminaison est muette : _je, tu, il, ils_. _Nous_ et _vous_ gardent le radical de l'infinitif."),
    ]),
], chain=[
    ("assumption", "Tous les verbes en _-er_ (sauf _aller_) ont les mêmes terminaisons au présent."),
    ("mechanism", "Le radical change d'orthographe pour garder la prononciation : _ç, ge, è, ll, tt, i_."),
    ("result", "Ces changements touchent _je, tu, il, ils_ ; _nous_ et _vous_ restent réguliers."),
], why="L'orthographe des verbes courants (_j'achète, nous commençons, il appelle_) est vérifiée dans toute production écrite.",
  look=["la terminaison de l'infinitif (-cer, -ger, -yer, -eler…)", "la personne (terminaison muette ou non ?)"],
  traps=["*_nous mangons_", "*_j'achete_", "*_nous appellons_"],
  distractors=["le radical non modifié", "la modification appliquée à _nous / vous_"],
  questions=[
    Q("a", 1, "form", "Mes collègues ___ trois langues.", ("parlent", "_ils parlent_."), [("parles", "_parles_ va avec _tu_."), ("parlons", "_parlons_ va avec _nous_.")]),
    Q("b", 1, "form", "Nous ___ la réunion à 9 heures.", ("commençons", "_-cer_ : _ç_ devant _o_."), [("commencons", "Il faut une cédille devant _o_."), ("commencont", "La terminaison de _nous_ est _-ons_.")]),
    Q("b", 1, "form", "Le soir, nous ___ souvent au restaurant.", ("mangeons", "_-ger_ : _e_ devant _o_."), [("mangons", "Il faut un _e_ pour garder le son [ʒ]."), ("mangions", "C'est l'imparfait ou le subjonctif.")]),
    Q("b", 2, "form", "J'___ mon pain dans cette boulangerie.", ("achète", "_e → è_ devant une syllabe muette."), [("achete", "Il faut un accent grave."), ("achette", "_acheter_ prend un accent, il ne double pas le _t_.")]),
    Q("b", 2, "form", "Comment est-ce que tu t'___ ?", ("appelles", "_-eler_ : _ll_ devant un _e_ muet."), [("appeles", "_appeler_ double le _l_ devant un _e_ muet."), ("appèles", "_appeler_ double la consonne, il ne prend pas d'accent.")]),
    Q("b", 2, "form", "Nous vous ___ demain à 10 heures.", ("appelons", "Avec _nous_, la terminaison est prononcée : pas de doublement."),
      [("appellons", "_nous_ garde le radical de l'infinitif : un seul _l_."), ("appelont", "La terminaison est _-ons_.")]),
    Q("b", 2, "form", "Je ___ le thé au café.", ("préfère", "_é → è_ devant une syllabe muette."), [("préfére", "Il faut un accent grave sur le deuxième _e_."), ("prefère", "Le premier _é_ garde son accent aigu.")]),
    Q("b", 3, "form", "Ils ___ leur loyer le 5 de chaque mois.", ("paient", "_-yer_ : _y → i_ devant un _e_ muet (ou _payent_)."), [("payons", "_payons_ va avec _nous_."), ("paiyent", "Cette forme n'existe pas.")]),
  ],
  cards=[R("er-ortho", "b", "Orthographe des verbes en -er", "nous (manger, commencer) ; j' (acheter, appeler) ?", "nous **mangeons**, nous **commençons** ; j'**achète**, j'**appelle**.",
           mistake="_nous appelons_ : pas de doublement avec _nous_ et _vous_.")])

# ================================================================ chapitre 23
c = b.chapter(23, "Le verbe « aller »", focus=[
    P("_Aller_ est irrégulier et très fréquent : déplacement, futur proche (_je vais partir_), santé (_ça va_). "
      "Les prépositions de transport (_en train, à pied_) l'accompagnent souvent."),
    P(REF.format(23, 102)),
], los={
    "a": "Conjuguer _aller_ et l'employer avec un lieu (_aller à, en, chez_).",
    "b": "Choisir _en_ ou _à_ devant un moyen de transport.",
})
c.module(1, "« Aller » et les moyens de transport", sections=[
    ("a", [
        TABLE(["je vais", "tu vas", "il / elle va", "nous allons", "vous allez", "ils / elles vont"]),
        P("_aller **à** la gare, **au** marché, **en** Italie, **chez** le coiffeur_. Pour remplacer le lieu : _J'**y** vais_ (voir chapitre 24)."),
    ]),
    ("b", [
        UL("**en** quand on est **dans** le véhicule : _en train, en voiture, en bus, en avion, en métro, en bateau, en taxi_.",
           "**à** quand on est **sur** le moyen de transport ou à pied : _à pied, à vélo, à moto, à cheval, à trottinette_."),
        NOTE("On entend _en vélo_ à l'oral, mais _à vélo_ reste la forme recommandée à l'écrit."),
    ]),
], chain=[
    ("assumption", "_Aller_ est irrégulier : trois radicaux (_v-, all-, ir-_ au futur)."),
    ("mechanism", "Le lieu suit les règles habituelles (_à, en, au, chez_)."),
    ("result", "Transport : **en** si l'on est dedans, **à** si l'on est dessus."),
], why="Les trajets et les transports sont un thème récurrent (mobilité, environnement) du DELF.",
  look=["la personne du verbe", "dans ou sur le véhicule ?"],
  traps=["*_ils allent_", "*_en pied_", "*_au train_"],
  distractors=["une forme régulière inventée", "_en / à_ inversés"],
  questions=[
    Q("a", 1, "form", "Mes enfants ___ à l'école à 8 heures.", ("vont", "_ils vont_."), [("allent", "Cette forme n'existe pas."), ("vons", "Cette forme n'existe pas.")]),
    Q("a", 1, "form", "Nous ___ chez nos amis ce soir.", ("allons", "_nous allons_."), [("vont", "_vont_ va avec _ils_."), ("vas", "_vas_ va avec _tu_.")]),
    Q("b", 1, "form", "Je vais au travail ___ pied.", ("à", "_à pied_."), [("en", "On dit _à pied_."), ("par", "On dit _à pied_.")]),
    Q("b", 1, "form", "Pour aller à Marseille, nous prenons le TGV : nous y allons ___ train.", ("en", "Dans le véhicule → _en_."), [("à", "On est dans le train : _en train_."), ("au", "_au train_ n'est pas correct.")]),
    Q("b", 2, "form", "Beaucoup de Parisiens vont au bureau ___ vélo.", ("à", "Sur le véhicule → _à vélo_."), [("en", "_en vélo_ est familier ; à l'écrit, _à vélo_."), ("par", "On ne dit pas _par vélo_.")]),
  ],
  cards=[R("transport", "b", "En / à + transport", "en ou à ?", "**en** (dans) : train, voiture, avion, bus ; **à** (sur) : pied, vélo, moto, cheval.")])

# ================================================================ chapitre 26
c = b.chapter(26, "Les verbes en « -ir », « -oir » et « -re » au présent", focus=[
    P("Les verbes du « 3e groupe » sont les plus fréquents et les plus irréguliers : _prendre, faire, pouvoir, devoir, savoir, vouloir, venir_. "
      "Leur présent sert aussi de base au subjonctif et à l'imparfait."),
    P(REF.format(26, 108)),
], los={
    "a": "Conjuguer les verbes à un, deux ou trois radicaux (finir, partir, boire, prendre, venir…).",
    "b": "Conjuguer les irréguliers fréquents (faire, mettre, pouvoir, devoir, vouloir, savoir, falloir).",
    "c": "Choisir entre _savoir_ et _connaître_.",
})
c.module(1, "Les verbes à plusieurs radicaux", sections=[
    ("a", [
        TABLE(["Type", "je / il", "nous", "ils"],
              ["finir (2 radicaux)", "je fini**s**, il fini**t**", "nous fin**iss**ons", "ils fin**iss**ent"],
              ["partir, dormir, sortir", "je par**s**, il par**t**", "nous par**t**ons", "ils par**t**ent"],
              ["écrire, lire, dire", "j'écri**s**", "nous écri**v**ons", "ils écri**v**ent"],
              ["prendre (3 radicaux)", "je prend**s**, il prend", "nous pre**n**ons", "ils pre**nn**ent"],
              ["venir, tenir", "je vien**s**", "nous ven**ons**", "ils vie**nn**ent"],
              ["boire", "je boi**s**", "nous bu**v**ons", "ils boi**v**ent"],
              ["recevoir, devoir", "je reçoi**s**, je doi**s**", "nous recev**ons**, nous dev**ons**", "ils reçoi**v**ent, ils doi**v**ent"]),
        NOTE("Les verbes en _-dre_ gardent le _d_ : _il prend, il répond, il attend_ (pas de _t_). Mais _peindre, craindre_ : _il peint, il craint_."),
    ]),
], chain=[
    ("assumption", "Les verbes du 3e groupe ont souvent deux ou trois radicaux selon la personne."),
    ("mechanism", "_je, tu, il_ ont un radical court ; _nous, vous_ celui de l'infinitif ; _ils_ souvent un troisième (_prennent, viennent, boivent_)."),
    ("result", "Connaître la forme de _nous_ et de _ils_ permet de retrouver l'imparfait et le subjonctif."),
], why="Ces verbes sont les plus employés de la langue : une forme fausse se remarque immédiatement.",
  look=["la personne", "le groupe du verbe (-ir type finir ou type partir, -dre…)"],
  traps=["*_ils prendent_", "*_nous finons_", "*_ils venent_"],
  distractors=["le radical d'une autre personne", "une forme régularisée"],
  questions=[
    Q("a", 1, "form", "Les cours ___ à 17 heures.", ("finissent", "_finir_ : _ils finissent_."), [("finent", "_finir_ prend _-iss-_ au pluriel."), ("finisent", "Il faut deux _s_.")]),
    Q("a", 1, "form", "Mes voisins ___ en vacances demain.", ("partent", "_partir_ : _ils partent_."), [("partissent", "_partir_ ne prend pas _-iss-_."), ("parts", "_parts_ n'est pas une forme verbale.")]),
    Q("a", 2, "form", "Les étudiants ___ le bus pour aller à la fac.", ("prennent", "_prendre_ : _ils prennent_."), [("prendent", "Le radical de _ils_ est _prenn-_."), ("prenent", "Il faut deux _n_.")]),
    Q("a", 2, "form", "Mes parents ___ nous voir dimanche.", ("viennent", "_venir_ : _ils viennent_."), [("venent", "Le radical de _ils_ est _vienn-_."), ("venissent", "_venir_ ne prend pas _-iss-_.")]),
    Q("a", 2, "form", "Nous ___ beaucoup de thé en hiver.", ("buvons", "_boire_ : _nous buvons_."), [("boivons", "_boiv-_ ne sert que pour _ils_."), ("boisons", "Le radical de _nous_ est _buv-_.")]),
    Q("a", 3, "form", "Il ___ toujours à mes messages dans l'heure.", ("répond", "Verbe en _-dre_ : _il répond_ (sans _t_)."), [("répont", "Les verbes en _-dre_ gardent le _d_."), ("réponde", "C'est le subjonctif.")]),
  ],
  cards=[R("trois-radicaux", "a", "Prendre, venir, boire", "ils (prendre, venir, boire) ?", "ils **prennent**, ils **viennent**, ils **boivent** ; nous prenons, venons, buvons.")])
c.module(2, "Les irréguliers fréquents, « savoir » et « connaître »", sections=[
    ("b", [
        TABLE(["Verbe", "je", "nous", "vous", "ils"],
              ["faire", "fais", "faisons", "**faites**", "**font**"], ["mettre", "mets", "mettons", "mettez", "mettent"],
              ["pouvoir", "**peux**", "pouvons", "pouvez", "**peuvent**"], ["vouloir", "**veux**", "voulons", "voulez", "**veulent**"],
              ["devoir", "dois", "devons", "devez", "doivent"], ["savoir", "sais", "savons", "savez", "savent"], ["dire", "dis", "disons", "**dites**", "disent"]),
        P("**Falloir** (seulement _il_) : _il **faut**_ + infinitif ou nom : _Il faut partir. Il faut du courage._"),
        NOTE("_Vous **faites**, vous **dites**, vous **êtes**_ : trois exceptions en _-tes_ (jamais *_vous faisez_, *_vous disez_)."),
    ]),
    ("c", [
        UL("**savoir** + infinitif, _que_, _si_, une question indirecte, ou une information apprise : _Je **sais** nager. Je **sais qu'**il est parti. Tu **sais** la réponse ?_",
           "**connaître** + nom de personne, de lieu, d'œuvre (une familiarité) : _Je **connais** Paul, Lyon, ce livre._"),
    ]),
], chain=[
    ("assumption", "Une dizaine de verbes très fréquents ont des formes à apprendre par cœur."),
    ("mechanism", "_Faire, dire_ font _vous faites, vous dites_ ; _pouvoir, vouloir_ changent de voyelle (_peux / pouvons / peuvent_)."),
    ("result", "_Savoir_ s'emploie avec un infinitif ou une proposition ; _connaître_ avec un nom de personne ou de lieu."),
], why="_Vous faites_, _ils peuvent_, _savoir / connaître_ : erreurs classiques jusqu'au niveau B2.",
  look=["la personne", "ce qui suit le verbe (nom, infinitif, proposition)"],
  traps=["*_vous faisez_", "*_ils pouvent_", "*_je connais nager_"],
  distractors=["une forme régularisée", "_savoir_ / _connaître_ inversés"],
  questions=[
    Q("b", 1, "form", "Qu'est-ce que vous ___ ce week-end ?", ("faites", "_vous faites_ (exception)."), [("faisez", "Cette forme n'existe pas."), ("font", "_font_ va avec _ils_.")]),
    Q("b", 1, "form", "Ils ne ___ pas venir à la réunion.", ("peuvent", "_pouvoir_ : _ils peuvent_."), [("pouvent", "Cette forme n'existe pas."), ("peut", "_peut_ va avec _il_.")]),
    Q("b", 2, "form", "Vous ___ toujours la vérité ?", ("dites", "_vous dites_ (exception)."), [("disez", "Cette forme n'existe pas."), ("disent", "_disent_ va avec _ils_.")]),
    Q("b", 2, "form", "Mes enfants ___ un chien pour Noël.", ("veulent", "_vouloir_ : _ils veulent_."), [("voulent", "Le radical de _ils_ est _veul-_."), ("veuillent", "C'est le subjonctif.")]),
    Q("b", 2, "form", "Pour réussir, il ___ beaucoup travailler.", ("faut", "_falloir_ : _il faut_."), [("fait", "_il fait_ vient de _faire_."), ("falloit", "Cette forme n'existe pas.")]),
    Q("c", 1, "conceptual", "Tu ___ conduire ?", ("sais", "_savoir_ + infinitif (une compétence)."), [("connais", "_connaître_ n'est pas suivi d'un infinitif."), ("peux", "_pouvoir_ exprime une possibilité, pas une compétence apprise.")]),
    Q("c", 1, "conceptual", "Est-ce que vous ___ ce restaurant ?", ("connaissez", "_connaître_ + nom de lieu."), [("savez", "_savoir_ n'est pas suivi d'un nom de lieu."), ("sachez", "C'est le subjonctif ou l'impératif de _savoir_.")]),
    Q("c", 2, "conceptual", "Je ne ___ pas pourquoi il est parti si tôt.", ("sais", "_savoir_ + question indirecte."), [("connais", "_connaître_ n'introduit pas de question indirecte."), ("connaît", "Il faut _savoir_, et la personne est _je_.")]),
  ],
  cards=[R("savoir-connaitre", "c", "Savoir / connaître", "savoir ou connaître ?", "**savoir** + infinitif, _que_, _si_, _pourquoi_… ; **connaître** + nom (personne, lieu, œuvre)."),
         R("faites-dites", "b", "Vous faites, vous dites", "vous (faire, dire, être) ?", "vous **faites**, vous **dites**, vous **êtes**.")])

# ================================================================ chapitre 27
c = b.chapter(27, "Les verbes pronominaux", focus=[
    P("Les verbes pronominaux (_se lever, se souvenir, s'intéresser à_) s'emploient avec un pronom de la même personne que le sujet. "
      "Ils sont nombreux dans les textes argumentatifs : _s'engager, se mobiliser, se rendre compte_."),
    P(REF.format(27, 122)),
], los={
    "a": "Conjuguer un verbe pronominal (réfléchi, réciproque) au présent et à l'infinitif.",
    "b": "Employer les verbes toujours pronominaux et le sens passif (_ça se vend bien_).",
})
c.module(1, "Pronoms réfléchis, réciproques et constructions pronominales", sections=[
    ("a", [
        TABLE(["je **me** lève", "tu **te** lèves", "il **se** lève", "nous **nous** levons", "vous **vous** levez", "ils **se** lèvent"]),
        UL("**Réfléchi** : l'action revient sur le sujet : _Je **me** lave._",
           "**Réciproque** (pluriel) : action mutuelle : _Ils **s'**aiment. Nous **nous** écrivons._",
           "À l'**infinitif**, le pronom s'accorde avec le sujet : _Je vais **me** coucher. Nous devons **nous** dépêcher._"),
        P("**Négation** : _Je **ne me** lève **pas** tôt._"),
    ]),
    ("b", [
        UL("**Toujours pronominaux** : _se souvenir de, s'en aller, se méfier de, s'évanouir, se moquer de, s'enfuir_.",
           "**Sens différent** : _rendre / **se rendre compte**, douter / **se douter**, attendre / **s'attendre à**, passer / **se passer**_ (= avoir lieu).",
           "**Sens passif** : _Ce livre **se vend** bien. Le vin blanc **se boit** frais. Ça **ne se fait pas**._"),
    ]),
], chain=[
    ("assumption", "Un verbe pronominal se conjugue avec un pronom qui renvoie au sujet."),
    ("mechanism", "Le pronom change avec la personne, même à l'infinitif (_je vais **me** reposer_)."),
    ("result", "Certains verbes n'existent qu'à la forme pronominale ou changent de sens ; d'autres prennent un sens passif."),
], why="_Se rendre compte, s'attendre à, se mobiliser_ sont des verbes clés de l'argumentation B2.",
  look=["le sujet (pour choisir le pronom)", "un infinitif après un verbe conjugué"],
  traps=["*_nous allons se promener_", "*_je souviens_", "*_je m'en souviens pas_ (oubli de _ne_)"],
  distractors=["_se_ à l'infinitif quel que soit le sujet", "le verbe sans pronom"],
  questions=[
    Q("a", 1, "form", "Le dimanche, nous ___ tard.", ("nous levons", "_nous nous levons_."), [("se levons", "Avec _nous_, le pronom est _nous_."), ("levons", "_se lever_ est pronominal.")]),
    Q("a", 2, "form", "Demain, je vais ___ très tôt.", ("me lever", "Le pronom s'accorde avec le sujet, même à l'infinitif."), [("se lever", "Avec _je_, le pronom est _me_."), ("lever", "Il manque le pronom.")]),
    Q("a", 2, "form", "Nous devons ___ si nous voulons attraper le train.", ("nous dépêcher", "Infinitif pronominal avec _nous_."), [("se dépêcher", "Avec _nous_, le pronom est _nous_."), ("dépêcher", "_se dépêcher_ est pronominal.")]),
    Q("a", 2, "form", "Mes grands-parents ___ depuis soixante ans.", ("s'aiment", "Sens réciproque, 3e personne du pluriel."), [("aiment", "Il manque le pronom réciproque."), ("nous aimons", "Le sujet est _mes grands-parents_.")]),
    Q("b", 1, "form", "Tu ___ de notre premier voyage ?", ("te souviens", "_se souvenir de_ est toujours pronominal."), [("souviens", "_se souvenir_ demande le pronom."), ("rappelles", "_rappeler_ seul ne se construit pas avec _de_.")]),
    Q("b", 2, "vocabulary", "Je ne ___ que c'était si tard !", ("me rendais pas compte", "_se rendre compte_ = comprendre, réaliser."),
      [("rendais pas compte", "_se rendre compte_ est pronominal."), ("me rendais pas", "Il manque _compte_.")]),
    Q("b", 2, "conceptual", "Ce modèle de vélo électrique ___ très bien cette année.", ("se vend", "Sens passif : le vélo est vendu."), [("vend", "Le vélo ne vend rien : il faut le sens passif."), ("est vendant", "Cette forme n'existe pas en français.")]),
    Q("b", 3, "vocabulary", "Les organisateurs ne ___ pas à un tel succès.", ("s'attendaient", "_s'attendre à_ = prévoir."), [("attendaient", "_attendre_ (sans pronom) se construit sans _à_."), ("se doutaient", "_se douter_ se construit avec _de_.")]),
  ],
  cards=[R("infinitif-pronominal", "a", "Pronominal à l'infinitif", "Nous allons ___ promener ?", "**nous** : le pronom s'accorde avec le sujet (_je vais me…, nous allons nous…_)."),
         R("sens-pronominal", "b", "Verbes pronominaux à sens propre", "se rendre compte / s'attendre à / se douter de ?", "réaliser / prévoir / soupçonner.")])

# ================================================================ chapitre 37
c = b.chapter(37, "Les prépositions et les verbes", focus=[
    P("Beaucoup de verbes se construisent avec **à** ou **de** devant un nom ou un infinitif : _penser à, parler de, commencer à, décider de_. "
      "Ces constructions sont à mémoriser ; elles déterminent aussi les pronoms (_y, en, lui_)."),
    P(REF.format(37, 160)),
], los={
    "a": "Construire les verbes avec _à_ + nom et _de_ + nom.",
    "b": "Construire les verbes avec _à_ + infinitif et _de_ + infinitif.",
})
c.module(1, "Les prépositions « à » et « de »", sections=[
    ("a", [
        TABLE(["Verbe + à + nom", "Verbe + de + nom"],
              ["penser **à**, s'intéresser **à**, participer **à**", "parler **de**, avoir besoin **de**, se souvenir **de**"],
              ["répondre **à**, téléphoner **à**, obéir **à**", "s'occuper **de**, profiter **de**, dépendre **de**"],
              ["ressembler **à**, faire confiance **à**", "se servir **de**, se méfier **de**, manquer **de**"]),
        P("Double construction : _demander / dire / conseiller / promettre **quelque chose à quelqu'un**_ ; _remercier / féliciter **quelqu'un de** quelque chose_."),
    ]),
    ("b", [
        TABLE(["Verbe + à + infinitif", "Verbe + de + infinitif"],
              ["commencer **à**, continuer **à**, apprendre **à**", "décider **de**, essayer **de**, finir **de**, arrêter **de**"],
              ["réussir **à**, arriver **à**, hésiter **à**", "accepter **de**, refuser **de**, oublier **de**, éviter **de**"],
              ["s'habituer **à**, chercher **à**, tenir **à**", "conseiller **à** qqn **de**, demander **à** qqn **de**, permettre **à** qqn **de**"]),
        NOTE("Sans préposition : _aimer, préférer, vouloir, pouvoir, devoir, savoir, espérer, aller, venir_ + infinitif : _J'espère **réussir**._"),
    ]),
], chain=[
    ("assumption", "La préposition après un verbe n'est pas logique : elle appartient au verbe."),
    ("mechanism", "On apprend chaque verbe avec sa construction : _penser à_, _parler de_, _décider de_, _réussir à_…"),
    ("result", "La préposition détermine le pronom de reprise (_j'y pense, j'en parle_) et le relatif (_auquel, dont_)."),
], why="Les constructions verbales correctes (_participer à, éviter de_) sont un critère de « richesse et correction » à l'écrit.",
  look=["le verbe principal", "nom ou infinitif après le verbe"],
  traps=["*_participer dans_", "*_décider à partir_", "*_j'espère de réussir_"],
  distractors=["la préposition de l'autre série", "une préposition calquée sur l'anglais"],
  questions=[
    Q("a", 1, "form", "Elle participe ___ un projet humanitaire.", ("à", "_participer à_."), [("dans", "*_participer dans_ est un calque de l'anglais."), ("de", "_participer de_ a un autre sens (= relever de).")]),
    Q("a", 1, "form", "Nous avons besoin ___ votre aide.", ("de", "_avoir besoin de_."), [("à", "On dit _avoir besoin de_."), ("pour", "On dit _avoir besoin de_.")]),
    Q("a", 2, "form", "Le succès du projet dépend ___ financement.", ("du", "_dépendre de + le_ → _du_."), [("au", "On dit _dépendre de_."), ("sur le", "*_dépendre sur_ est un calque de l'anglais.")]),
    Q("a", 2, "form", "Je ne fais pas confiance ___ ce site internet.", ("à", "_faire confiance à_."), [("en", "On dit _faire confiance à_."), ("de", "On dit _faire confiance à_.")]),
    Q("b", 1, "form", "Il a décidé ___ changer de travail.", ("de", "_décider de_ + infinitif."), [("à", "On dit _décider de_."), ("pour", "On dit _décider de_.")]),
    Q("b", 1, "form", "Ma fille apprend ___ nager.", ("à", "_apprendre à_ + infinitif."), [("de", "On dit _apprendre à_."), ("pour", "On dit _apprendre à_.")]),
    Q("b", 2, "form", "Essayez ___ arriver à l'heure demain.", ("d'", "_essayer de_ + infinitif."), [("à", "On dit _essayer de_."), ("pour", "On dit _essayer de_.")]),
    Q("b", 2, "form", "Les écologistes cherchent ___ sensibiliser le grand public.", ("à", "_chercher à_ + infinitif = essayer de."), [("de", "On dit _chercher à_."), ("pour", "On dit _chercher à_.")]),
    Q("b", 2, "form", "J'espère ___ mon examen en juin.", ("réussir", "_espérer_ + infinitif sans préposition."), [("de réussir", "_espérer_ se construit sans préposition."), ("à réussir", "_espérer_ se construit sans préposition.")]),
    Q("b", 3, "form", "Le médecin lui a conseillé ___ fumer.", ("d'arrêter de", "_conseiller à qqn de_ + _arrêter de_ + infinitif."),
      [("à arrêter de", "On dit _conseiller de_."), ("d'arrêter", "_arrêter_ se construit avec _de_ devant un infinitif.")]),
  ],
  sets=[S("Lettre à la mairie",
    "Un habitant écrit au maire :\n\n« Monsieur le Maire, je m'intéresse **(1)** ___ la vie de notre quartier et je souhaite participer à la réunion du 12 mars. "
    "Beaucoup d'habitants ont décidé **(2)** ___ créer une association : nous cherchons **(3)** ___ améliorer la propreté des rues. "
    "Nous avons besoin **(4)** ___ votre soutien pour réussir. »",
    [Q("a", 1, "form", "Blanc (1) :", ("à", "_s'intéresser à_."), [("de", "On dit _s'intéresser à_."), ("pour", "On dit _s'intéresser à_.")]),
     Q("b", 1, "form", "Blanc (2) :", ("de", "_décider de_ + infinitif."), [("à", "On dit _décider de_."), ("pour", "On dit _décider de_.")]),
     Q("b", 2, "form", "Blanc (3) :", ("à", "_chercher à_ + infinitif."), [("de", "On dit _chercher à_."), ("pour", "On dit _chercher à_.")]),
     Q("a", 1, "form", "Blanc (4) :", ("de", "_avoir besoin de_."), [("à", "On dit _avoir besoin de_."), ("pour", "On dit _avoir besoin de_.")])])],
  cards=[R("verbes-a", "b", "Verbes + à + infinitif", "commencer, apprendre, réussir, chercher, hésiter + ?", "**à** + infinitif."),
         R("verbes-de", "b", "Verbes + de + infinitif", "décider, essayer, accepter, refuser, éviter, oublier + ?", "**de** + infinitif.", mistake="_espérer, vouloir, devoir_ : sans préposition.")])

# ================================================================ chapitre 38
c = b.chapter(38, "Les verbes de déplacement", focus=[
    P("_Aller, venir, partir, sortir, rentrer, retourner, revenir_ : ces verbes ne sont pas synonymes. Les distinguer précisément évite des contresens."),
    P(REF.format(38, 164)),
], los={
    "a": "Distinguer _aller / venir, partir / sortir, rentrer / revenir / retourner_.",
    "b": "Employer _visiter_ (un lieu) et _aller voir / rendre visite à_ (une personne).",
})
c.module(1, "« Aller », « venir », « partir » et les autres", sections=[
    ("a", [
        UL("**aller** : vers un lieu où l'on n'est pas ; **venir** : vers le lieu où se trouve la personne qui parle ou à qui l'on parle : _Tu **viens** chez moi ce soir ?_",
           "**partir** (de) : quitter un lieu, souvent pour longtemps ; **sortir** (de) : aller à l'extérieur d'un lieu fermé, ou se divertir le soir.",
           "**rentrer** : retourner chez soi ; **revenir** : venir de nouveau là où l'on est ; **retourner** : aller de nouveau là où l'on était."),
    ]),
    ("b", [
        UL("**visiter** + un lieu : _visiter un musée, une ville_.", "**aller voir** / **rendre visite à** + une personne : _Je **rends visite à** ma grand-mère._ (jamais *_visiter ma grand-mère_)."),
    ]),
], chain=[
    ("assumption", "Les verbes de mouvement se choisissent selon le point de vue de celui qui parle."),
    ("mechanism", "_Venir / revenir_ : vers ici ; _aller / retourner_ : vers là-bas ; _rentrer_ : chez soi."),
    ("result", "_Visiter_ s'emploie pour un lieu ; pour une personne, _rendre visite à_."),
], why="Ces nuances apparaissent dans les documents oraux (annonces, messages) et dans les récits.",
  look=["le point de vue (ici ou là-bas)", "un lieu ou une personne"],
  traps=["*_visiter mes parents_", "_aller_ au lieu de _venir_ pour rejoindre l'interlocuteur"],
  distractors=["le verbe de direction opposée", "_visiter_ avec une personne"],
  questions=[
    Q("a", 1, "conceptual", "Tu ___ à ma fête samedi ? J'organise ça chez moi.", ("viens", "Vers le lieu de celui qui parle → _venir_."), [("vas", "On se dirige vers la personne qui parle."), ("pars", "_partir_ = quitter un lieu.")]),
    Q("a", 2, "conceptual", "Il est tard, je ___ chez moi.", ("rentre", "Retourner chez soi → _rentrer_."), [("reviens", "_revenir_ = venir de nouveau ici."), ("sors", "_sortir_ = aller dehors.")]),
    Q("a", 2, "conceptual", "J'ai adoré Lisbonne : j'espère y ___ l'an prochain.", ("retourner", "Aller de nouveau là-bas → _retourner_."), [("revenir", "_revenir_ = venir de nouveau ici (on n'est pas à Lisbonne)."), ("rentrer", "_rentrer_ = retourner chez soi.")]),
    Q("a", 2, "conceptual", "Ce soir, on ___ au cinéma avec des amis.", ("sort", "Se divertir à l'extérieur → _sortir_."), [("revient", "_revenir_ = venir de nouveau ici."), ("rentre", "_rentrer_ = retourner chez soi.")]),
    Q("b", 1, "vocabulary", "Pendant les vacances, je vais ___ ma grand-mère en Bretagne.", ("rendre visite à", "Une personne → _rendre visite à_."), [("visiter", "_visiter_ s'emploie avec un lieu."), ("visiter à", "*_visiter à_ n'existe pas.")]),
    Q("b", 1, "vocabulary", "Nous avons ___ le château de Versailles.", ("visité", "Un lieu → _visiter_."), [("rendu visite au", "_rendre visite à_ s'emploie avec une personne."), ("vu à", "Cette construction n'existe pas.")]),
  ],
  cards=[R("deplacement", "a", "Rentrer, revenir, retourner", "rentrer / revenir / retourner ?", "**rentrer** : chez soi ; **revenir** : de nouveau ici ; **retourner** : de nouveau là-bas."),
         R("visiter", "b", "Visiter / rendre visite", "visiter ou rendre visite à ?", "**visiter** un lieu ; **rendre visite à** une personne.")])

b.write()
