from unittest.mock import patch
from pc_client.typing_engine import TypingEngine

@patch("pc_client.typing_engine.pyautogui")
def test_ascii_typing(mock_gui):
    engine = TypingEngine("fast")
    with patch.object(engine, "_wait", return_value=True):
        assert engine.type_text("A\nB").completed
    mock_gui.write.assert_called_with("B")

@patch("pc_client.typing_engine.pyautogui")
@patch("pc_client.typing_engine.pyperclip")
def test_unicode_pastes(mock_clip, mock_gui):
    engine = TypingEngine("fast")
    with patch.object(engine, "_wait", return_value=True): assert engine.type_text("é").completed
    mock_clip.copy.assert_called()
    mock_gui.hotkey.assert_called_with("ctrl", "v")
