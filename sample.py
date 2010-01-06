from purplebot.bot import bot

HOST="Krypt.CA.US.GameSurge.net"
PORT=6667
NICK="PurpleBot"
IDENT="PurpleBot"
REALNAME="PurpleBot"
QUITMSG = "Sayonara"

CHANNELS=["#bottesting"]


sample = bot(2)
sample.run(HOST, PORT, NICK, IDENT, REALNAME)
