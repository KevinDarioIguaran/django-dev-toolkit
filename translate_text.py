from googletrans import Translator

async def translate_text(text, dest_lang):
    translator = Translator()
    result = await translator.translate(text, dest=dest_lang)
    return result.text