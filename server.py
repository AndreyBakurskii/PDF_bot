import telegram.ext as tg_ext
import telegram as tg

import document as doc
from my_config import TOKEN


updater = tg_ext.Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

FILENAME, PHOTO, AMOUNT_OF_PHOTOS, ADD_OR_END = range(4)

# global variables

documents = doc.Documents()


def start(update: tg.Update, context: tg_ext.CallbackContext):

    update.message.reply_text(f"Hello {update.effective_user.username}! Check commands!",)


start_handler = tg_ext.CommandHandler("start", callback=start)
dispatcher.add_handler(start_handler)


def create_pdf(update: tg.Update, context: tg_ext.CallbackContext):

    update.message.reply_text("Input filename without extension, please.\n"
                              "If you don't create pdf_file, send me /cancel")

    return FILENAME


def get_filename(update: tg.Update, context: tg_ext.CallbackContext):

    username = update.effective_user.username
    filename = update.message.text

    if doc.check_filename(filename):

        documents.append(doc.Document(username, filename))

        update.message.reply_text("Send me amount of photo.\n"
                                  "If you don't create pdf_file, send me /cancel")

        return AMOUNT_OF_PHOTOS

    else:

        update.message.reply_text("Send me correct filename, please.\n"
                                  "If you don't create pdf_file, send me /cancel")

        return FILENAME


def get_amount_of_photo(update: tg.Update, context: tg_ext.CallbackContext):

    username = update.effective_user.username
    document = documents.get_document(username)

    value = update.message.text

    if doc.check_amount_of_photo(value):

        document.get_amount_of_photo(int(value))
        update.message.reply_text("Send me photo.\n"
                                  "If you don't create pdf_file, send me /cancel")

        return PHOTO

    else:

        update.message.reply_text("Send me correct value for the amount of photo, please.\n"
                                  "If you don't create pdf_file, send me /cancel")

        return AMOUNT_OF_PHOTOS


def get_photo(update: tg.Update, context: tg_ext.CallbackContext):

    username = update.effective_user.username
    document = documents.get_document(username)

    photo = update.message.photo[-1].get_file()

    if document.get_photo(photo):
        update.message.reply_text("All photos added to your pdf file!\n"
                                  "If you want to add another photos, send me /add, otherwise, /end\n"
                                  "If you don't create pdf_file, send me /cancel")
        return ADD_OR_END

    else:
        return PHOTO


def add_photos(update: tg.Update, context: tg_ext.CallbackContext):

    update.message.reply_text("Ok, send me amount of photo, which need to add.\n"
                              "If you don't create pdf_file, send me /cancel")

    return AMOUNT_OF_PHOTOS


def end_pdf(update: tg.Update, context: tg_ext.CallbackContext):

    username = update.effective_user.username
    document = documents.get_document(username)

    update.message.reply_text("Please, wait some time!")

    path = doc.convert2pdf(document)

    update.message.bot.send_document(update.message.chat.id, open(path, 'rb'))
    update.message.reply_text("Thank you for using me! See you again!")

    documents.delete_document(username)

    return tg_ext.ConversationHandler.END


def cancel(update: tg.Update, context: tg_ext.CallbackContext):

    username = update.effective_user.username

    update.message.reply_text("Thank you for using me! See you again!")

    documents.delete_document(username)

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
