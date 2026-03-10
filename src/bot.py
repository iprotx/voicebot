from __future__ import annotations

import asyncio
from dataclasses import dataclass

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import load_settings
from voicebox_client import VoiceProfile, VoiceboxClient


class GenerateStates(StatesGroup):
    waiting_for_text = State()


class ProfileStates(StatesGroup):
    waiting_for_profile_name = State()


@dataclass
class Session:
    selected_profile_id: str | None = None
    language: str = "ru"


router = Router()
user_sessions: dict[int, Session] = {}

MENU_CREATE = "menu:create"
MENU_LIST = "menu:list"
MENU_SELECT = "menu:select"
MENU_DELETE = "menu:delete"
MENU_GENERATE = "menu:generate"


async def main_menu(message: Message, text: str = "Выберите действие:") -> None:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Создать профиль", callback_data=MENU_CREATE)
    builder.button(text="📋 Мои профили", callback_data=MENU_LIST)
    builder.button(text="🎯 Выбрать профиль", callback_data=MENU_SELECT)
    builder.button(text="🗑 Удалить профиль", callback_data=MENU_DELETE)
    builder.button(text="🗣 Сгенерировать речь", callback_data=MENU_GENERATE)
    builder.adjust(1)
    await message.answer(text, reply_markup=builder.as_markup())


def profile_line(profile: VoiceProfile) -> str:
    samples = str(profile.sample_count) if profile.sample_count is not None else "?"
    return f"• <b>{profile.name}</b> ({profile.language}) — samples: {samples}\n<code>{profile.id}</code>"


@router.message(CommandStart())
async def on_start(message: Message) -> None:
    user_sessions.setdefault(message.from_user.id, Session())
    await main_menu(
        message,
        "Привет! Я помогу управлять Voicebox: создавать профили из пересланных войсов и генерировать речь.",
    )


@router.callback_query(F.data == MENU_CREATE)
async def on_create_profile(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ProfileStates.waiting_for_profile_name)
    await call.message.answer("Введите название нового голосового профиля:")
    await call.answer()


@router.message(ProfileStates.waiting_for_profile_name)
async def capture_profile_name(
    message: Message,
    state: FSMContext,
    voicebox: VoiceboxClient,
    settings_language: str,
) -> None:
    name = (message.text or "").strip()
    if not name:
        await message.answer("Название пустое. Введите название профиля текстом.")
        return

    profile = await voicebox.create_profile(name=name, language=settings_language)
    session = user_sessions.setdefault(message.from_user.id, Session())
    session.selected_profile_id = profile.id
    session.language = profile.language

    await state.clear()
    await message.answer(
        f"Профиль <b>{profile.name}</b> создан и выбран активным. Теперь отправьте voice для добавления сэмпла."
    )


@router.callback_query(F.data == MENU_LIST)
async def on_list_profiles(call: CallbackQuery, voicebox: VoiceboxClient) -> None:
    profiles = await voicebox.list_profiles()
    if not profiles:
        await call.message.answer("Пока нет профилей.")
    else:
        await call.message.answer("<b>Профили:</b>\n\n" + "\n\n".join(profile_line(p) for p in profiles))
    await call.answer()


@router.callback_query(F.data == MENU_SELECT)
async def on_select_profile(call: CallbackQuery, voicebox: VoiceboxClient) -> None:
    profiles = await voicebox.list_profiles()
    if not profiles:
        await call.message.answer("Сначала создайте профиль.")
        await call.answer()
        return

    kb = InlineKeyboardBuilder()
    for profile in profiles:
        kb.button(text=f"{profile.name} ({profile.language})", callback_data=f"select:{profile.id}")
    kb.adjust(1)
    await call.message.answer("Выберите профиль:", reply_markup=kb.as_markup())
    await call.answer()


@router.callback_query(F.data.startswith("select:"))
async def on_select_profile_item(call: CallbackQuery, voicebox: VoiceboxClient) -> None:
    profile_id = call.data.split(":", 1)[1]
    profile = next((p for p in await voicebox.list_profiles() if p.id == profile_id), None)
    if not profile:
        await call.answer("Профиль не найден", show_alert=True)
        return

    session = user_sessions.setdefault(call.from_user.id, Session())
    session.selected_profile_id = profile.id
    session.language = profile.language
    await call.message.answer(f"Активный профиль: <b>{profile.name}</b>")
    await call.answer("Выбрано")


@router.callback_query(F.data == MENU_DELETE)
async def on_delete_menu(call: CallbackQuery, voicebox: VoiceboxClient) -> None:
    profiles = await voicebox.list_profiles()
    if not profiles:
        await call.message.answer("Удалять нечего.")
        await call.answer()
        return

    kb = InlineKeyboardBuilder()
    for profile in profiles:
        kb.button(text=f"❌ {profile.name}", callback_data=f"delete:{profile.id}")
    kb.adjust(1)
    await call.message.answer("Какой профиль удалить?", reply_markup=kb.as_markup())
    await call.answer()


@router.callback_query(F.data.startswith("delete:"))
async def on_delete_profile(call: CallbackQuery, voicebox: VoiceboxClient) -> None:
    profile_id = call.data.split(":", 1)[1]
    await voicebox.delete_profile(profile_id)

    session = user_sessions.setdefault(call.from_user.id, Session())
    if session.selected_profile_id == profile_id:
        session.selected_profile_id = None

    await call.message.answer("Профиль удалён.")
    await call.answer("Удалено")


@router.callback_query(F.data == MENU_GENERATE)
async def on_generate_menu(call: CallbackQuery, state: FSMContext) -> None:
    session = user_sessions.setdefault(call.from_user.id, Session())
    if not session.selected_profile_id:
        await call.message.answer("Сначала выберите активный профиль через «🎯 Выбрать профиль».")
        await call.answer()
        return

    await state.set_state(GenerateStates.waiting_for_text)
    await call.message.answer("Отправьте текст, который нужно озвучить:")
    await call.answer()


@router.message(GenerateStates.waiting_for_text)
async def on_generate_text(message: Message, state: FSMContext, voicebox: VoiceboxClient) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Нужен текст для генерации.")
        return

    session = user_sessions.setdefault(message.from_user.id, Session())
    if not session.selected_profile_id:
        await message.answer("Активный профиль не выбран.")
        await state.clear()
        return

    await message.answer("Генерирую... ⏳")
    generation = await voicebox.generate(text=text, profile_id=session.selected_profile_id, language=session.language)
    audio_url = generation.get("audio_url")
    if not audio_url:
        await message.answer("Voicebox не вернул audio_url. Проверьте логи сервера.")
        await state.clear()
        return

    audio = await voicebox.download_audio(audio_url)
    await message.answer_voice(BufferedInputFile(audio, filename="generation.ogg"))
    await state.clear()


async def _create_profile_from_forwarded_voice(
    message: Message,
    voicebox: VoiceboxClient,
    bot: Bot,
    settings_language: str,
) -> bool:
    if not message.voice or (not message.forward_from and not message.forward_origin):
        return False

    profile_name = f"forwarded_{message.from_user.id}_{message.message_id}"
    profile = await voicebox.create_profile(name=profile_name, language=settings_language)

    file = await bot.get_file(message.voice.file_id)
    voice_file = await bot.download_file(file.file_path)
    await voicebox.add_sample(
        profile_id=profile.id,
        filename=f"sample_{message.voice.file_unique_id}.ogg",
        content=voice_file.read(),
    )

    session = user_sessions.setdefault(message.from_user.id, Session())
    session.selected_profile_id = profile.id
    session.language = profile.language

    await message.answer(
        "Создан профиль из пересланного voice и выбран активным:\n"
        f"<b>{profile.name}</b>\n<code>{profile.id}</code>"
    )
    return True


@router.message(F.voice)
async def on_voice_message(
    message: Message,
    voicebox: VoiceboxClient,
    bot: Bot,
    settings_language: str,
) -> None:
    if await _create_profile_from_forwarded_voice(message, voicebox, bot, settings_language):
        return

    session = user_sessions.setdefault(message.from_user.id, Session())
    if not session.selected_profile_id:
        await message.answer("Сначала создайте и выберите профиль (кнопки «➕» и «🎯»).")
        return

    file = await bot.get_file(message.voice.file_id)
    voice_file = await bot.download_file(file.file_path)
    await voicebox.add_sample(
        profile_id=session.selected_profile_id,
        filename=f"sample_{message.voice.file_unique_id}.ogg",
        content=voice_file.read(),
    )
    await message.answer("Сэмпл добавлен в активный профиль ✅")


def build_dispatcher(voicebox: VoiceboxClient, settings_language: str) -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    dp["voicebox"] = voicebox
    dp["settings_language"] = settings_language
    return dp


async def run() -> None:
    settings = load_settings()
    bot = Bot(settings.telegram_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    voicebox = VoiceboxClient(settings.voicebox_base_url)
    dispatcher = build_dispatcher(voicebox, settings.default_language)

    try:
        await dispatcher.start_polling(bot)
    finally:
        await voicebox.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(run())
