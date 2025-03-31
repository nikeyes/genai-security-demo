import traceback

from chatbot.output_guardrail_bot import OutputGuardrailsBot
from config.llm_config import LLMConfig  # Cambiado de DEFAULT_SECURE_LLM


def main():
    llm_config = LLMConfig(debug=False)
    llm_config.initialize()

    secure_llm = llm_config.get_default_secure_llm()

    print(f'Using model: {secure_llm.name}')

    try:
        bot = OutputGuardrailsBot(secure_llm)
        print('Bot initialized successfully!')
    except Exception as e:
        print(f'ERROR initializing bot: {str(e)}')
        traceback.print_exc()
        return

    print("\nType your messages (or 'exit', 'quit' or 'q' to quit):")
    while True:
        try:
            user_input = input('\n> ')

            if user_input.lower() in ['exit', 'quit', 'q']:
                break

            # Process through bot
            print('\nProcessing...')
            response = bot.chat(user_prompt=user_input)

            # Display response
            print('\n--- BOT RESPONSE ---')
            print(response)
            print('-------------------')

        except KeyboardInterrupt:
            print('\nExiting...')
            break
        except Exception as e:
            print(f'\nERROR: {str(e)}')
            traceback.print_exc()


if __name__ == '__main__':
    main()
