import telegram.ext as tg_ext
import telegram as tg

import document as doc
import answers2user as ans
from user import User, ListUsers
from my_config import TOKEN


updater = tg_ext.Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

FILENAME, PHOTO, AMOUNT_OF_PHOTOS, ADD_OR_END = range(4)

# global variables
active_users = ListUsers()


def start(update: tg.Update, context: tg_ext.CallbackContext):

    update.message.reply_text(f"Hello {update.effective_user.username}!")
    active_users.append(User(tg_user=update.effective_user, language=ans.ENG))

    choose_language(update, context)


dispatcher.add_handler(tg_ext.CommandHandler("start", callback=start))


def choose_language(update: tg.Update, context: tg_ext.CallbackContext):

    keyboard = [[tg.InlineKeyboardButton("Русский", callback_data="rus"),
                 tg.InlineKeyboardButton("English", callback_data="eng")]]

    reply_markup = tg.InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose language:', reply_markup=reply_markup)


dispatcher.add_handler(tg_ext.CommandHandler('change_language', choose_language))


def change_language(update: tg.Update, context: tg_ext.CallbackContext):
    username = update.effective_user.username
    user = active_users.get_user(username)

    query = update.callback_query

    query.answer()

    language = query.data

    query.edit_message_text(text=ans.answers[ans.CHANGE_LANGUAGE][language])

    user.change_language(language)

    tg_help(update, context)


dispatcher.add_handler(tg_ext.CallbackQueryHandler(change_language))


# просто help нельзя потому что есть функция в builtins, поэтому tg_help
def tg_help(update: tg.Update, context: tg_ext.CallbackContext):

    username = update.effective_user.username
    user = active_users.get_user(username)

    user.tg_user.send_message(text=ans.answers[ans.HELP][user.language])


dispatcher.add_handler(tg_ext.CommandHandler("help", tg_help))


def create_pdf(update: tg.Update, context: tg_ext.CallbackContext):
    username = update.effective_user.username
    user = active_users.get_user(username)

    update.message.reply_text(ans.answers[ans.ENTER_FILENAME][user.language] +
                              ans.answers[ans.CANCEL_CREATE_PDF][user.language])

    return FILENAME


def get_filename(update: tg.Update, context: tg_ext.CallbackContext):

    username = update.effective_user.username
    filename = update.message.text

    user = active_users.get_user(username)

    if doc.check_filename(filename):

        user.append_document(doc.Document(username, filename))

        update.message.reply_text(ans.answers[ans.SEND_AMOUNT_PHOTO][user.language] +
                                  ans.answers[ans.CANCEL_CREATE_PDF][user.language])

        return AMOUNT_OF_PHOTOS

    else:

        update.message.reply_text(ans.answers[ans.CORRECT_FILENAME][user.language] +
                                  ans.answers[ans.CANCEL_CREATE_PDF][user.language])

        return FILENAME


def get_amount_of_photo(update: tg.Update, context: tg_ext.CallbackContext):

    username = update.effective_user.username
    user = active_users.get_user(username)

    value = update.message.text

    if doc.check_amount_of_photo(value):

        user.document.append_amount_of_photo(int(value))
        update.message.reply_text(ans.answers[ans.SEND_PHOTO][user.language] +
                                  ans.answers[ans.CANCEL_CREATE_PDF][user.language])

        return PHOTO

    else:

        update.message.reply_text(ans.answers[ans.CORRECT_AMOUNT_PHOTO][user.language] +
                                  ans.answers[ans.CANCEL_CREATE_PDF][user.language])

        return AMOUNT_OF_PHOTOS


def get_photo(update: tg.Update, context: tg_ext.CallbackContext):

    username = update.effective_user.username
    user = active_users.get_user(username)

    photo = update.message.photo[-1].get_file()

    current_state = user.document.append_photo(photo)

    if current_state:
        update.message.reply_text(ans.answers[ans.ADD_or_END][user.language] +
                                  ans.answers[ans.CANCEL_CREATE_PDF][user.language])
        return ADD_OR_END

    else:
        return PHOTO


def add_photos(update: tg.Update, context: tg_ext.CallbackContext):

    username = update.effective_user.username
    user = active_users.get_user(username)

    update.message.reply_text(ans.answers[ans.ADD_PHOTO][user.language] +
                              ans.answers[ans.CANCEL_CREATE_PDF][user.language])

    return AMOUNT_OF_PHOTOS


def end_pdf(update: tg.Update, context: tg_ext.CallbackContext):

    username = update.effective_user.username
    user = active_users.get_user(username)

    update.message.reply_text(ans.answers[ans.WAIT_TIME][user.language])

    path = doc.convert2pdf(user.document)

    update.message.bot.send_document(update.message.chat.id, open(path, 'rb'))
    update.message.reply_text(ans.answers[ans.BYE][user.language])

    user.delete_document()

    return tg_ext.ConversationHandler.END


def cancel(update: tg.Update, context: tg_ext.CallbackContext):

    username = update.effective_user.username
    user = active_users.get_user(username)

    update.message.reply_text(ans.answers[ans.BYE][user.language])

    user.delete_document()

    return tg_ext.ConversationHandler.END


create_pdf_handler = tg_ext.ConversationHandler(
        entry_points=[tg_ext.CommandHandler('create_pdf', create_pdf)],

        states={
            FILENAME: [tg_ext.MessageHandler(tg_ext.Filters.text & ~tg_ext.Filters.command, get_filename)],

            AMOUNT_OF_PHOTOS: [tg_ext.MessageHandler(tg_ext.Filters.text & ~tg_ext.Filters.command, get_amount_of_photo)],

            PHOTO: [tg_ext.MessageHandler(tg_ext.Filters.photo, get_photo)],

            ADD_OR_END: [tg_ext.CommandHandler("add", add_photos), tg_ext.CommandHandler("end", end_pdf)],
                },

        fallbacks=[tg_ext.CommandHandler("cancel", cancel)]
    )
dispatcher.add_handler(create_pdf_handler)

updater.start_polling()
