from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PicklePersistence
from telegram import ChatAction
from functools import wraps
from urllib.parse import urlencode
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import pickle
import os.path
from .utils import *

logger = setup_logger(__name__)


def start_command(update, context):
    """Start a new dialogue when user seds the command "/start"."""

    logger.debug(f"{update.effective_message.chat_id} - User: /start")
    context.chat_data['turns'] = []
    update.message.reply_text("Heeyyyy, I'm gonna be your startup mentor.😎 \n"
                              "I will: \n"
                              "🎯 Help You Set Goals and Work on Them  \"/goals\". \n" 
                              "✅ Check Your Progress on a Regular Basis \"/progress\". \n"
                              "🧠 Share Knowledge, Skills & Expertise \"/expertise\". \n"
                              "🔥 Provide with Tasks, Challenges & Resources \"/tasks\". \n"
                              "🤗 Give Advice & Support. \n"
                              "💬 Text & Discuss Anything With You. \n"
                              "💪 Motivate You \"/motivate\".  \n"
                              "🚀 Help You Develop Contacts & Explore Careers \"/careers\".  \n"
                              "\n \n"
                              "To have some fun - append \"@gif\" for me to generate a GIF. \n"
                              "If I'm getting annoying, type \"/reset\" or \"/start\" \n"
                              "Make sure to send no more than one message per turn. \n")



def goals_command(update, context):
    #help the user set goals when the user presses "/goals".

    logger.debug(f"{update.effective_message.chat_id} - User: /goals")
    
    turns = context.chat_data['turns']
    update.message.reply_text("Now let's set some awesome, measurable goals! 🎯 \n"
                              "Do you have anything you would wanna accomplish " 
                              "with startups this year? Something ambitious would be great!🔥")

def progress_command(update, context):
    #help the user set goals when the user presses "/goals".

    logger.debug(f"{update.effective_message.chat_id} - User: /progress")
    
    turns = context.chat_data['turns']
    update.message.reply_text("🎯 Progress Check: \n"
                              "Hey, what's the progress with your goals? \n"
                              "Precisely describe what you did, what you do "
                              "now and what you're planning to do in the nearest future. \n"
                              "You can also ask me for advice")

def expertise_command(update, context):

    logger.debug(f"{update.effective_message.chat_id} - User: /expertise")
    
    turns = context.chat_data['turns']
    update.message.reply_text("😎 Ok, Let Me Share With You Some Essential Knowledge & Skills: \n"
                                "\n"
                                "🧠 Fundumental Knowledge about Startups: "
                                "\n"
                                "A startup is a company designed to grow fast."
                                "Being newly founded does not in itself make a company a startup. "
                                "Nor is it necessary for a startup to work on technology, or take "
                                "venture funding, or have some sort of 'exit.' "
                                "The only essential thing is growth. "
                                "Everything else we associate with startups follows from growth.\n"
                                "\n"
                                "🔥 Crucial Skills for Startups: \n"
                                "\n"
                                "1. Starting From Problems. \n"
                                "2. Coming Up With Unique Ideas. \n"
                                "3. Finding a Great Competitor Advantage. \n"
                                "4. Conducting Customer Development Interviews. \n"
                                "5. Calculating Metrics & Competitor Analysis. \n"
                                "6. Getting Insigths & Starting Validation. \n"
                                "7. Prototyping & Experimenting. \n"
                                "8. Quick and Easy Demand Testing. \n"
                                "9. Runing Continous Feedback Loop. \n"
                                "10. Pitching to Investors & Geting Funding. \n")

def tasks_command(update, context):

    logger.debug(f"{update.effective_message.chat_id} - User: /tasks")
    
    turns = context.chat_data['turns']
    update.message.reply_text("🔥 Tasks, Challenges & Resources: \n"
                              "Here's a list of tasks you should try: \n"
                              "Here's a list of challenges you should do: "
                              "Here's a list of resources you check out: \n")

def motivate_command(update, context):

    logger.debug(f"{update.effective_message.chat_id} - User: /motivate")
    
    turns = context.chat_data['turns']
    update.message.reply_text("💪 Let let me try to motivate you: \n")


def careers_command(update, context):

    logger.debug(f"{update.effective_message.chat_id} - User: /careers")
    
    turns = context.chat_data['turns']
    update.message.reply_text("🚀 Ok, let's develop contacts and explore careers: \n")


def reset_command(update, context):
    """Reset the dialogue when user sends the command "/reset"."""

    logger.debug(f"{update.effective_message.chat_id} - User: /reset")
    context.chat_data['turns'] = []
    update.message.reply_text("Beep beep!")


def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    """Retry n times if unsuccessful."""

    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def translate_message_to_gif(message, **chatbot_params):
    """Translate message text into a GIF.

    See https://engineering.giphy.com/contextually-aware-search-giphy-gets-work-specific/"""

    params = {
        'api_key': chatbot_params['giphy_token'],
        's': message,
        'weirdness': chatbot_params.get('giphy_weirdness', 5)
    }
    #urlencode makes this: 'http://api.giphy.com/v1/gifs/translate?api_key=giphy_token&s=Hello&weirdness=10'
    url = "http://api.giphy.com/v1/gifs/translate?" + urlencode(params)
    response = requests_retry_session().get(url)
    return response.json()['data']['images']['fixed_height']['url']

def self_decorator(self, func):
    """Passes bot object to func command."""

    # TODO: Any other ways to pass variables to handlers?
    def command_func(update, context, *args, **kwargs):
        return func(self, update, context, *args, **kwargs)

    return command_func


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(self, update, context, *args, **kwargs):
            #key thing here: action is ChatAction.TYPING
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(self, update, context, *args, **kwargs)

        return command_func

    return decorator


send_typing_action = send_action(ChatAction.TYPING)

@send_typing_action
def message(self, update, context):
    """Receive message, generate response, and send it back to the user."""

    max_turns_history = self.chatbot_params.get('max_turns_history', 2)
    giphy_prob = self.chatbot_params.get('giphy_prob', 0.1)
    giphy_max_words = self.chatbot_params.get('giphy_max_words', 10)

    if 'turns' not in context.chat_data:
        context.chat_data['turns'] = []
    turns = context.chat_data['turns']

    user_message = update.message.text
    return_gif = False
    if '@gif' in user_message:
        # Return gif
        return_gif = True
        user_message = user_message.replace('@gif', '').strip()
    if max_turns_history == 0:
        context.chat_data['turns'] = []
    # A single turn is a group of user messages and bot responses right after
    turn = {
        'user_messages': [],
        'bot_messages': []
    }
    turns.append(turn)
    turn['user_messages'].append(user_message)
    logger.debug(f"{update.effective_message.chat_id} - User: {user_message}")
    # Merge turns into a single prompt (don't forget EOS token)
    prompt = "I'm your startup mentor, I will help you build a successful startup<|endoftext|>Hi, that's so cool, I'm super excited! It's my dream to make a successful startup!<|endoftext|>"
    from_index = max(len(turns) - max_turns_history - 1, 0) if max_turns_history >= 0 else 0
    for turn in turns[from_index:]:
        # Each turn begins with user messages
        for user_message in turn['user_messages']:
            prompt += clean_text(user_message) + self.generation_pipeline.tokenizer.eos_token
        for bot_message in turn['bot_messages']:
            prompt += clean_text(bot_message) + self.generation_pipeline.tokenizer.eos_token

    # Generate bot messages
    bot_messages = generate_responses(
        prompt,
        self.generation_pipeline,
        seed=self.seed,
        debug=self.debug,
        **self.generator_kwargs
    )
    if len(bot_messages) == 1:
        bot_message = bot_messages[0]
    else:
        bot_message = pick_best_response(
            prompt,
            bot_messages,
            self.ranker_dict,
            debug=self.debug
        )
    turn['bot_messages'].append(bot_message)
    logger.debug(f"{update.effective_message.chat_id} - Bot: {bot_message}")
    # Return response as text
    update.message.reply_text(bot_message)
    if len(bot_message.split()) <= giphy_max_words and random.random() < giphy_prob:
        return_gif = True
    if return_gif:
        # Also return the response as a GIF
        gif_url = translate_message_to_gif(bot_message, **self.chatbot_params)
        context.bot.send_animation(update.effective_message.chat_id, gif_url)


def error(update, context):
    logger.warning(context.error)


class TelegramBot:
    """Telegram bot based on python-telegram-bot."""

    #__init__ is called when an object is created and it allow to initialize the attributes
    def __init__(self, **kwargs):
        # Extract parameters
        general_params = kwargs.get('general_params', {})
        device = general_params.get('device', -1)
        seed = general_params.get('seed', None)
        debug = general_params.get('debug', False)

        generation_pipeline_kwargs = kwargs.get('generation_pipeline_kwargs', {})
        generation_pipeline_kwargs = {**{
            'model': 'microsoft/DialoGPT-medium'
        }, **generation_pipeline_kwargs}

        generator_kwargs = kwargs.get('generator_kwargs', {})
        generator_kwargs = {**{
            'max_length': 1000,
            'do_sample': True,
            'clean_up_tokenization_spaces': True
        }, **generator_kwargs}

        prior_ranker_weights = kwargs.get('prior_ranker_weights', {})
        cond_ranker_weights = kwargs.get('cond_ranker_weights', {})

        chatbot_params = kwargs.get('chatbot_params', {})
        if 'telegram_token' not in chatbot_params:
            raise ValueError("Please provide `telegram_token`")
        if 'giphy_token' not in chatbot_params:
            raise ValueError("Please provide `giphy_token`")
        continue_after_restart = chatbot_params.get('continue_after_restart', True)
        data_filename = chatbot_params.get('data_filename', 'bot_data.pkl')

        #initializing attributes with "self" keyword, so we can acces them later
        #'self' binds attributes with given arguments
        self.generation_pipeline_kwargs = generation_pipeline_kwargs
        self.generator_kwargs = generator_kwargs
        self.prior_ranker_weights = prior_ranker_weights
        self.cond_ranker_weights = cond_ranker_weights
        self.chatbot_params = chatbot_params
        self.device = device
        self.seed = seed
        self.debug = debug

        # Prepare the pipelines
        self.generation_pipeline = load_pipeline('text-generation', device=device, **generation_pipeline_kwargs)
        self.ranker_dict = build_ranker_dict(device=device, **prior_ranker_weights, **cond_ranker_weights)

        # Initialize the chatbot
        logger.info("Initializing the telegram bot...")
        if continue_after_restart:
            persistence = PicklePersistence(data_filename)
            self.updater = Updater(chatbot_params['telegram_token'], use_context=True, persistence=persistence)
            if os.path.isfile(data_filename):
                with open(data_filename, 'rb') as handle:
                    chat_data = pickle.load(handle)['chat_data']
                for chat_id, chat_id_data in chat_data.items():
                    if len(chat_id_data['turns']) > 0:
                        self.updater.bot.send_message(chat_id=chat_id, text="I'm back! Let's resume...")
                    else:
                        self.updater.bot.send_message(chat_id=chat_id, text="I'm live!")
        else:
            self.updater = Updater(chatbot_params['telegram_token'], use_context=True)

        # Add command, message and error handlers for our dispatcher
        dp = self.updater.dispatcher
        #https://github.com/python-telegram-bot/python-telegram-bot/blob/master/telegram/ext/commandhandler.py 
        dp.add_handler(CommandHandler('start', start_command))
        dp.add_handler(CommandHandler('goals', goals_command))
        dp.add_handler(CommandHandler('progress', progress_command))
        dp.add_handler(CommandHandler('expertise', expertise_command))
        dp.add_handler(CommandHandler('tasks', tasks_command))
        dp.add_handler(CommandHandler('motivate', motivate_command))
        dp.add_handler(CommandHandler('careers', careers_command))
        dp.add_handler(CommandHandler('reset', reset_command))
        #calling the decorated message function to return itself and pass variables to a message handler
        dp.add_handler(MessageHandler(Filters.text, self_decorator(self, message)))
        dp.add_error_handler(error)

    def run(self):
        """Run the chatbot."""
        logger.info("Running the telegram bot...")

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until you press Ctrl-C to stop the process of polling
        self.updater.idle()


def run(**kwargs):
    """Run `TelegramBot`."""
    TelegramBot(**kwargs).run()










