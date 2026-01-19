import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from generate_data import *
from simulator import *

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

pattern_matrix = get_pattern_matrix(all_words, all_words)
freqs = get_freqs()
initial_expected_scores = get_initial_expected_scores(freqs)

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} is ready!")

# Command to generate n random starting words
@bot.command()
async def starters(ctx, n=10):
    if not isinstance(n, int) or n <= 0:
        await(ctx.send("Please provide a positive integer for the number of words to generate."))
        return
    elif n > NUM_ALLOWED:
        await(ctx.send(f"Cannot generate more than {NUM_ALLOWED} words."))
        return
    else:
        await(ctx.send(f"Generating {n} random words..."))
        words = generate_random_words(n)
        await(ctx.send(f"Generated words: {', '.join(words)}"))
        return

# Command to make the bot play Wordle with given parameters
@bot.command()
async def play(ctx, target_word=None, starting_word=None):
    target_word = target_word.upper() if target_word is not None else None
    starting_word = starting_word.upper() if starting_word is not None else None
    if target_word is None:
        await(ctx.send("Please provide a target word for the bot to play Wordle."))
        return
    elif starting_word is not None and starting_word not in all_words:
        await(ctx.send(f"The word '{starting_word}' is not in the allowed word list."))
        return 
    score, guesses, patterns = play_game_bot_with_freqs(
        answer=target_word,
        pattern_matrix=pattern_matrix,
        initial_expected_scores=initial_expected_scores,
        freqs=freqs,
        starting_word=starting_word,
        cheating=True,
        discord=True
    )
    guess_msg = ", ".join(guesses)
    guess_msg = f"||{guess_msg}||"
    pattern_msg = "\n".join(patterns)
    await(ctx.send(f"Score: {score}/6\nPatterns:\n{pattern_msg}\nGuesses: {guess_msg}"))
    return

# Command to suggest a guess based on previous attempts and feedback

bot.run(token, log_handler=handler, log_level=logging.DEBUG)