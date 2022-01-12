from telegram.ext import Updater, MessageHandler, CommandHandler, CallbackQueryHandler, Filters, CallbackContext
from status import Status
import command, user, config, check, threading

with open('token.txt', 'r') as file: TOKEN = file.read()
status = Status()

def main():

    updater = Updater(TOKEN)
    
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler( CommandHandler('start', command.start), group=0 )
    dispatcher.add_handler( CommandHandler('help', command._help), group=0 )
    dispatcher.add_handler( CommandHandler('my_info', command.my_info), group=0 )
    dispatcher.add_handler( CommandHandler('my_lastmatches', command.matches), group=0 )
    dispatcher.add_handler( CommandHandler('summoner', command.summoner), group=0 )
    dispatcher.add_handler( CallbackQueryHandler(command.champion_mastery, pattern=check.summoner_champion_mastery) )
    dispatcher.add_handler( CallbackQueryHandler(command.back_to_summoner, pattern=check.back_to_summoner) )
    dispatcher.add_handler( CommandHandler('freechampions', command.free_champion), group=0 )
    dispatcher.add_handler( CommandHandler('item', command._item), group=0 )
    dispatcher.add_handler( CommandHandler('champion', command.champion), group=0 )
    dispatcher.add_handler( CallbackQueryHandler(command.back_to_champion, pattern=check.back_to_champion), group=0 )
    dispatcher.add_handler( CallbackQueryHandler(command.champion_stats, pattern=check.champion_stats), group=0 )
    dispatcher.add_handler( CallbackQueryHandler(command.champion_tips, pattern=check.champion_tips), group=0 )
    dispatcher.add_handler( CallbackQueryHandler(command.champion_spells, pattern=check.champion_spells), group=0 )
    dispatcher.add_handler( CallbackQueryHandler(command.champion_skins, pattern=check.champion_skins), group=0 )
  
    dispatcher.add_handler( CommandHandler('config', config.config), group=0 )
    dispatcher.add_handler( CommandHandler('config_region', config.region), group=0 )
    dispatcher.add_handler( CommandHandler('config_summoner', config.summoner), group=0 )
    dispatcher.add_handler( CommandHandler('config_spectator_on', config.spectator_on), group=0 )
    dispatcher.add_handler( CommandHandler('config_spectator_off', config.spectator_off), group=0 )
    dispatcher.add_handler( CommandHandler('config_time_zone', config.time_zone), group=0 )

    dispatcher.add_handler( MessageHandler(Filters.text, user.check) , group=1 )

    updater.start_polling()
    # Start
    status.write('')
    status.write('Inicia el bot.')

    thread = threading.Thread(target=user.spectator, args=(updater,))
    thread.start()
    status.write('Empieza a correr spectator.')

    updater.idle()
    # End

if __name__ == '__main__':
    main()