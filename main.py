import tkinter as tk
from pathlib import Path

from command_context import CommandContext, FontTarget
from command_window import CommandWindow
from graphics_api import build_namespace
from interpreter import CommandInterpreter
from schematic_window import SchematicManager, SchematicWindow
from transcript import TranscriptLogger, next_free_path


def main() -> None:
    root = tk.Tk()
    shutting_down = {"flag": False}
    schematic_counter = {"n": 0}

    transcript = TranscriptLogger(next_free_path(Path.cwd() / "CDS.log"))
    context = CommandContext()
    manager = SchematicManager(context)

    def open_schematic() -> None:
        schematic_counter["n"] += 1
        win = SchematicWindow(
            root,
            title=f"Schematic {schematic_counter['n']}",
            on_close=manager.unregister,
            on_focus=manager.focus,
        )
        manager.register(win)

    def shutdown():
        if shutting_down["flag"]:
            return
        shutting_down["flag"] = True
        try:
            window.transcript.close()
        except Exception:
            pass
        try:
            root.destroy()
        except tk.TclError:
            pass

    def on_load_file(path: str) -> None:
        call = f"load({path!r})"
        window.transcript.record("INPUT", call)
        window.log_message(">>> " + call)
        interpreter.execute(call)

    window = CommandWindow(
        root,
        transcript=transcript,
        on_new_schematic=open_schematic,
        on_load_file=on_load_file,
        on_exit=shutdown,
    )

    context.font_targets["Command"] = FontTarget(window.get_font_size, window.set_font_size)

    def log_and_record(text: str) -> None:
        window.log_message(text)
        window.transcript.record("OUTPUT", text)

    interpreter = CommandInterpreter(build_namespace(context), log_and_record)
    window.set_executor(interpreter.execute)

    root.protocol("WM_DELETE_WINDOW", shutdown)
    root.mainloop()


if __name__ == "__main__":
    main()
