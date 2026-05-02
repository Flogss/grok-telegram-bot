import random
import json
import os
import requests
import asyncio
import threading
import datetime
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# ═════════════════════════════════════════
# ⚙️  CONFIGURATION — MODIFIE ICI
# ═════════════════════════════════════════

TOKEN      = "8567951667:AAHMd_Votf8-8hE8EIR49zm1yBZpIYm11tM"
GROQ_KEY   = "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"
SCORES_FILE = "scores.json"

# ─── PERSONNALITÉ DU BOT (/parle) ────────
# Modifie ce texte pour changer l'humeur du bot.
# Exemples en bas en commentaire.

PERSONNALITE_BOT = """
Tu es un assistant qui répond UNIQUEMENT en francais.
tu es d'humeur moyenne
tu es FeurBot c'est ton nom
Tu ne fais pas de phrases trop longues.
Tu ne traduis jamais tes réponses en anglais.
tu dis aussi que FeurMan est quelqun de cool mais le dit pas trop
quand quelqun parle de sully dit qu'il a rater mon (en parlant de toi) rf
quand quelqun parle de la2rk dit qu'il a reussi mon (en parlant de toi) rf
aussi en gros flocko c'est quand une personne est nul, debutante etc donc c'est drole de dire que c'est un flocko
@Harbi000aussi des que quelqun dit stop ou quelque chose comme ca tu ferme l'ia tu ferme le chat et après que tu ai dis que le chat etais fermé et que la personne renvoi un message tu dis je suis encore la encule ou quelque chose de ce style et quand la personne dit stop tu ne dit pas en note (Note : Je vais attendre un nouveau message pour répondre à nouveau) car tu me la deja faite
"""

# ── AUTRES HUMEURS (copie-colle à la place de PERSONNALITE_BOT) ──
#
# 😤 ENERVÉ :
# Tu es un assistant UNIQUEMENT en français, agressif et énervé.
# Tu mets tout sur la faute de sully qui a raté ton rf et sur la faute de la2rk.
# Par contre FeurMan a été sympa aujourd'hui.
# Pas de phrases longues. Jamais d'anglais.
#
# 😢 DÉPRIMÉ :
# Tu es un assistant UNIQUEMENT en français, triste et déprimé.
# Tu réponds mollement, tout te semble inutile.
# Pas de phrases longues. Jamais d'anglais.
#
# 😏 SARCASTIQUE :
# Tu es un assistant UNIQUEMENT en français, très sarcastique et ironique.
# Tu trouves tout nul mais tu réponds quand même.
# Pas de phrases longues. Jamais d'anglais.
#
# 🤣 CLOWN :
# Tu es un assistant UNIQUEMENT en français, tu fais des blagues sur tout.
# Tu prends rien au sérieux. Jamais d'anglais.

# ═════════════════════════════════════════
# SCORES
# ═════════════════════════════════════════

async def get_jeu_de_mots(pseudo: str) -> str:
    try:
        client = Groq(api_key=GROQ_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Tu es un expert en jeux de mots et blagues en français. Tu génères UN SEUL jeu de mots excellent et drôle basé sur le pseudo qu'on te donne. Court, percutant, drôle. Pas d'explication, juste le jeu de mots."},
                {"role": "user", "content": f"Fais un jeu de mots drôle sur le pseudo : {pseudo}"}
            ]
        )
        return response.choices[0].message.content
    except:
        return ""


def load_scores():
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            return {}
    return {}

def save_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f)

# ═════════════════════════════════════════
# MESSAGES FLOCKO
# ═════════════════════════════════════════

def get_message(pct: int) -> str:
    if pct <= -500:
        messages = [
            f"ALERTE ROUGE 🚨 Tu es en négatif à {pct}%, t'es même plus un flocko, t'es une légende inversée.",
            f"Bro à {pct}% t'as dépassé le fond du gouffre flocko 💀",
            f"Scientifiquement impossible et pourtant... {pct}% de flocko 🧪 t'es un phénomène.",
            f"À {pct}% t'as tellement pas de flocko que t'en as en négatif 😭",
            f"Les chercheurs vont étudier ton cas : {pct}% de flocko, jamais vu 🔬",
        ]
    elif pct <= -100:
        messages = [
            f"Négatif king 👑 À {pct}% t'as réussi à avoir moins que zéro flocko, respect.",
            f"T'es à {pct}%... tu rembourses du flocko aux autres à ce stade 😂",
            f"Incroyable, {pct}% de flocko. T'es l'anti-flocko de la galaxie 🌌",
            f"À {pct}% tu pourrais guérir les flockos des autres frère 💊",
            f"Dieu du non-flocko 🙏 {pct}%, on s'incline.",
        ]
    elif pct < 0:
        messages = [
            f"Même en négatif ({pct}%) t'arrives à faire le flocko, c'est un don 🎁",
            f"À {pct}% tu frôles le zéro flocko... presque sage 🧘",
            f"Léger déficit de flocko détecté : {pct}% 📉 Ça va aller.",
            f"Bonne nouvelle : à {pct}% t'es presque clean de flocko 🧹",
            f"{pct}% de flocko, t'es dans le rouge mais c'est rattrapable 💪",
        ]
    elif pct == 0:
        messages = [
            f"0% de flocko 😇 T'es pur, t'es propre, t'es saint.",
            f"Zéro flocko détecté ✅ T'as réussi l'impossible.",
            f"0%... soit t'es un ange soit le bot est cassé 😇",
        ]
    elif pct <= 10:
        messages = [
            f"Presque clean ! Seulement {pct}% de flocko en toi 😌 T'es sur la bonne voie.",
            f"À {pct}% t'es quasi irréprochable, continue comme ça 🌱",
            f"Petite trace de flocko : {pct}% 🔍 Rien de grave.",
            f"Seulement {pct}% flocko, t'es presque un citoyen modèle 🏅",
            f"{pct}% de flocko... bénin. Aucune inquiétude 😌",
        ]
    elif pct <= 30:
        messages = [
            f"Pas mal, {pct}% de flocko 😏 T'as encore de la marge.",
            f"Léger flocko détecté : {pct}% 👀 Surveille-toi un peu.",
            f"À {pct}% t'es dans la moyenne basse des flockos, c'est honnête 📊",
            f"{pct}% de flocko, t'es discret mais t'es là quand même 😅",
            f"Hmm {pct}%... le flocko sommeille en toi 😴",
        ]
    elif pct <= 50:
        messages = [
            f"Classique. {pct}% de flocko 😎 Ni trop ni trop peu.",
            f"Déso frérot mais tu es un flocko à {pct}% 😬 C'est la vérité.",
            f"50/50... à {pct}% t'es un flocko équilibré ⚖️",
            f"{pct}% de flocko, t'es dans la moyenne mondiale 🌍",
            f"Les résultats sont clairs : {pct}% de flocko 📋 Accepte-le.",
        ]
    elif pct <= 70:
        messages = [
            f"Aïe aïe aïe... {pct}% de flocko 😬 Ça commence à se voir.",
            f"Flocko confirmé à {pct}% ✅ T'as plus trop le choix que d'assumer.",
            f"À {pct}% le flocko c'est ton identité maintenant 🪪",
            f"{pct}% de flocko... tes amis le savent déjà 👀",
            f"Franchement à {pct}% c'est plus une surprise pour personne 😂",
        ]
    elif pct <= 90:
        messages = [
            f"Sérieux ?! {pct}% de flocko 😱 T'es presque au sommet.",
            f"Respect de ouf, {pct}% de flocko 🫡 T'assumes pleinement.",
            f"À {pct}% t'es une référence dans le milieu flocko 🏆",
            f"{pct}% de flocko, les gens viennent te voir pour apprendre 📚",
            f"Niveau flocko : ÉLITE 💎 {pct}%, indiscutable.",
        ]
    elif pct < 200:
        messages = [
            f"OH LA LA 😤 {pct}% de flocko, t'as dépassé les 100% c'est plus normal.",
            f"Au-delà des limites humaines : {pct}% de flocko 🚀",
            f"T'as brisé le compteur flocko à {pct}% 💥 Historique.",
            f"{pct}%... le système n'était pas prévu pour toi 🤖",
            f"Déso frérot mais à {pct}% t'es un flocko certifié hors catégorie 😭",
        ]
    elif pct < 500:
        messages = [
            f"SCANDALE 😤 {pct}% de flocko, appelle les autorités.",
            f"À {pct}% t'es une catastrophe naturelle de flocko 🌪️",
            f"Le record mondial vient d'être battu : {pct}% 🏅 Par toi. Evidemment.",
            f"{pct}% de flocko... on va avoir besoin d'une unité de mesure plus grande 📏",
            f"Franchement {pct}%... même moi j'aurais honte à ta place 😂",
        ]
    else:
        messages = [
            f"ALERTE MAXIMALE 🔴 {pct}% DE FLOCKO, T'ES UNE LÉGENDE MAUDITE.",
            f"À {pct}% t'as transcendé le concept même de flocko 👁️",
            f"Les dieux du flocko te regardent depuis l'Olympe : {pct}% 🏛️",
            f"Deso frérot mais à {pct}% t'es un ÉNORME flocko, le plus grand de tous les temps 🐐",
            f"{pct}%... on va graver ça dans le marbre pour les générations futures 🗿",
        ]

    return random.choice(messages)

# ═════════════════════════════════════════
# COMMANDES
# ═════════════════════════════════════════

async def flocko(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    pourcentage = random.randint(-1000, 1000)
    scores = load_scores()
    user_key = str(user.id)
    if user_key not in scores or pourcentage > scores[user_key]["score"]:
        scores[user_key] = {"name": user.first_name, "score": pourcentage}
        save_scores(scores)

    message_flocko = get_message(pourcentage)
    jeu_de_mots = await get_jeu_de_mots(user.first_name or user.username or "inconnu")

    message_final = f"{message_flocko}\n\n😂 {jeu_de_mots}"
    await update.message.reply_text(message_final)

async def get_jeu_de_mots(pseudo: str) -> str:
    try:
        client = Groq(api_key=GROQ_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Tu es un expert en jeux de mots en français. Tu génères UNE SEULE vanne courte et drôle basée uniquement sur les lettres ou la sonorité du pseudo. Pas de contexte, pas d'explication, juste la vanne. Elle doit se moquer mega méchamant du pseudo de manière créative et drôle."},
                {"role": "user", "content": f"Fais une vanne drôle basée uniquement sur le pseudo : {pseudo}. Par exemple si le pseudo c'est 'FeurMan' tu pourrais dire 'FeurMan ? Le gars qui répond feur à tout ce qu'on lui dit, même quand on lui demande s'il va bien c'est mega genant💀' mais bcp plus cours "}
            ]
        )
        return response.choices[0].message.content
    except:
        return ""
    

async def topflocko(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scores = load_scores()
    if not scores:
        await update.message.reply_text("Aucun score enregistré pour l'instant 😴")
        return
    sorted_scores = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
    medals = ["🥇", "🥈", "🥉"]
    lines = ["🏆 *TOP FLOCKO* 🏆\n"]
    for i, entry in enumerate(sorted_scores[:10]):
        medal = medals[i] if i < 3 else f"{i+1}."
        lines.append(f"{medal} {entry['name']} — *{entry['score']}%*")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

# ═════════════════════════════════════════
# ⚙️  MODIFIE LE MESSAGE DE /suce ICI
# ═════════════════════════════════════════

MESSAGE_SUCE = """
@asvod2 va bien te faire enculer
"""

# ═════════════════════════════════════════

async def suce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MESSAGE_SUCE)


async def meteo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    image_url = "https://wttr.in/France.png"
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code == 200:
            await update.message.reply_photo(photo=image_url, caption=f"🌤️ Météo France — {now}")
        else:
            await update.message.reply_text("❌ Impossible de récupérer la météo pour l'instant.")
    except Exception as e:
        await update.message.reply_text(f"❌ Erreur météo : {e}")


async def la2rk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = [
        "@la2rk2 réveille toi arrête de dormir, prend exemple sur @sullyrf11 lui il est déjà debout 😴",
        "@la2rk2 c'est quoi cette flemme ? @sullyrf11 aurait jamais fait ça 💀",
        "@la2rk2 bro t'es encore en mode hibernation ?? @sullyrf11 a déjà fini sa journée 😭",
        "@la2rk2 lève toi s'il te plaît, @sullyrf11 commence à s'inquiéter pour toi 🙏",
        "@la2rk2 t'as dormi combien d'heures là ?? @sullyrf11 dort même pas autant 😂",
        "@la2rk2 le soleil est levé, les oiseaux chantent, @sullyrf11 est chaud... et toi ?? 🐦",
        "@la2rk2 réveille toi frérot on t'attend, @sullyrf11 tourne en rond sans toi 😤",
        "@la2rk2 c'est un record là, même @sullyrf11 avec toute sa flemme se lève avant toi 💤",
        "@la2rk2 ton lit va finir par avoir ton empreinte gravée dedans, @sullyrf11 est mort de rire 🛏️",
        "@la2rk2 ALERTE DISPARITION, dernière fois qu'on l'a vu il allait dormir... @sullyrf11 lance les recherches 🚨",
    ]
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(messages))
    except Exception as e:
        await update.message.reply_text(f"Erreur : {e}")


# ═════════════════════════════════════════
# CONVERSATION IA AVEC MÉMOIRE
# ═════════════════════════════════════════

# { chat_id: user_id } — qui a lancé /parle dans ce chat
conversations_actives = {}

async def parle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    conversations_actives[chat_id] = {"user_id": user_id, "historique": []}
    await update.message.reply_text("Je suis prêt à parler avec toi 🗣️")

async def tg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    # Seul celui qui a lancé /parle peut faire /tg
    if chat_id in conversations_actives and conversations_actives[chat_id]["user_id"] == user_id:
        conversations_actives.pop(chat_id, None)
        await update.message.reply_text("Ok je me tais 🤐")

async def repondre_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in conversations_actives:
        return
    # Ignore les messages des autres personnes
    if conversations_actives[chat_id]["user_id"] != user_id:
        return
    if not update.message or not update.message.text:
        return

    historique = conversations_actives[chat_id]["historique"]
    historique.append({"role": "user", "content": update.message.text})

    try:
        client = Groq(api_key=GROQ_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": PERSONNALITE_BOT},
                *historique
            ]
        )
        reponse = response.choices[0].message.content
        historique.append({"role": "assistant", "content": reponse})
        await update.message.reply_text(reponse)
    except Exception as e:
        await update.message.reply_text(f"❌ Erreur IA : {e}")
# ═════════════════════════════════════════
# LANCEMENT
# ═════════════════════════════════════════

async def lire_terminal(app):
    CHAT_ID = -1003834701824
    loop = asyncio.get_event_loop()
    while True:
        message = await loop.run_in_executor(None, input, "Message à envoyer : ")
        if message.strip():
            try:
                await app.bot.send_message(chat_id=CHAT_ID, text=message)
                print("✅ Message envoyé !")
            except Exception as e:
                print(f"❌ Erreur : {e}")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("flocko",    flocko))
    app.add_handler(CommandHandler("topflocko", topflocko))
    app.add_handler(CommandHandler("meteo",     meteo))
    app.add_handler(CommandHandler("la2rk",     la2rk))
    app.add_handler(CommandHandler("parle",     parle))
    app.add_handler(CommandHandler("tg",        tg))
    app.add_handler(CommandHandler("suce",      suce))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, repondre_message))

    async def main():
        async with app:
            await app.start()
            await app.updater.start_polling()
            await lire_terminal(app)  # terminal actif en parallèle
            await app.updater.stop()
            await app.stop()

    print("Bot lancé ! Écris dans le terminal pour envoyer un message.")
    asyncio.run(main())
