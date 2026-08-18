import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from slanguage.bootstrap import (
    DEFAULT_MODE,
    MODES,
    PRESET_ENTITIES,
    build,
    get_categories,
    get_constructs,
    handle_prompt,
)
from slanguage.terrain import render_map, run_command
from slanguage.vault.vault_enforcer import OmniLockTriggered, VaultCategoryError


class SlanguageGUI:
    def __init__(self):
        self.rt = build()
        self.rt.set_mode(DEFAULT_MODE)
        self.constructs = get_constructs(self.rt)
        self.categories = get_categories()

        self.root = tk.Tk()
        self.root.title("SlanguageOS")
        self.root.geometry("980x720")
        self.root.minsize(860, 620)
        self.root.configure(bg="#12151f")

        self._setup_style()
        self._build()
        self._refresh_vault_panel()

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        bg = "#12151f"
        card = "#1a1f2e"
        accent = "#7aa2f7"
        text = "#e0e4ef"

        style.configure(".", background=bg, foreground=text)
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=text, font=("Helvetica", 11))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), foreground=accent)
        style.configure("TButton", padding=6)
        style.configure("TNotebook", background=bg, borderwidth=0)
        style.configure("TNotebook.Tab", padding=[14, 6])

    def _build(self):
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=14, pady=(12, 8))
        ttk.Label(header, text="SlanguageOS", style="Header.TLabel").pack(side="left")
        ttk.Label(
            header,
            text="Mode-based runtime with vault access control",
        ).pack(side="left", padx=(12, 0))

        body = ttk.Frame(self.root)
        body.pack(fill="both", expand=True, padx=14, pady=8)

        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True)

        right = ttk.Frame(body, width=320)
        right.pack(side="right", fill="y", padx=(12, 0))
        right.pack_propagate(False)

        self._build_chat(left)
        self._build_terrain(left)
        self._build_controls(right)

        self.status = ttk.Label(self.root, text="Ready", anchor="w")
        self.status.pack(fill="x", padx=14, pady=(0, 10))

    def _build_chat(self, parent):
        chat_frame = ttk.LabelFrame(parent, text="Conversation")
        chat_frame.pack(fill="both", expand=True, pady=(0, 8))

        self.output = scrolledtext.ScrolledText(
            chat_frame,
            wrap="word",
            height=18,
            bg="#1a1f2e",
            fg="#e0e4ef",
            insertbackground="#e0e4ef",
            font=("Menlo", 11),
        )
        self.output.pack(fill="both", expand=True, padx=8, pady=8)
        self.output.configure(state="disabled")

        input_row = ttk.Frame(chat_frame)
        input_row.pack(fill="x", padx=8, pady=(0, 8))

        self.prompt = ttk.Entry(input_row)
        self.prompt.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.prompt.bind("<Return>", lambda _e: self._send_prompt())
        ttk.Button(input_row, text="Send", command=self._send_prompt).pack(side="right")

    def _build_terrain(self, parent):
        terrain_frame = ttk.LabelFrame(parent, text="Terrain Mapper")
        terrain_frame.pack(fill="both", expand=True)

        self.terrain_map = scrolledtext.ScrolledText(
            terrain_frame,
            wrap="none",
            height=16,
            bg="#1a1f2e",
            fg="#9ece6a",
            insertbackground="#e0e4ef",
            font=("Menlo", 10),
        )
        self.terrain_map.pack(fill="both", expand=True, padx=8, pady=8)

        coord_row = ttk.Frame(terrain_frame)
        coord_row.pack(fill="x", padx=8, pady=(0, 4))
        ttk.Label(coord_row, text="Lat").pack(side="left")
        self.lat_var = tk.StringVar(value="37.7749")
        ttk.Entry(coord_row, textvariable=self.lat_var, width=10).pack(side="left", padx=(4, 8))
        ttk.Label(coord_row, text="Lon").pack(side="left")
        self.lon_var = tk.StringVar(value="-122.4194")
        ttk.Entry(coord_row, textvariable=self.lon_var, width=10).pack(side="left", padx=(4, 8))

        action_row = ttk.Frame(terrain_frame)
        action_row.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(action_row, text="Goto", command=self._terrain_goto).pack(side="left", padx=(0, 4))
        ttk.Button(action_row, text="Step", command=self._terrain_step).pack(side="left", padx=(0, 4))
        ttk.Button(action_row, text="Refresh", command=self._terrain_refresh).pack(side="left")

        self._terrain_refresh()

    def _terrain_agent(self):
        return getattr(self.rt, "terrain", None)

    def _terrain_refresh(self):
        agent = self._terrain_agent()
        if agent is None:
            self.terrain_map.delete("1.0", "end")
            self.terrain_map.insert("1.0", "Terrain mapper not loaded.")
            return
        self.terrain_map.delete("1.0", "end")
        self.terrain_map.insert("1.0", render_map(agent))

    def _terrain_goto(self):
        agent = self._terrain_agent()
        if agent is None:
            messagebox.showerror("Terrain Mapper", "Terrain mapper not loaded.")
            return
        try:
            lat = float(self.lat_var.get())
            lon = float(self.lon_var.get())
        except ValueError:
            messagebox.showerror("Terrain Mapper", "Enter valid numeric lat/lon values.")
            return
        result = run_command(agent, ["goto", str(lat), str(lon)])
        self._terrain_refresh()
        self._set_status(result.get("message", "Terrain updated."))

    def _terrain_step(self):
        agent = self._terrain_agent()
        if agent is None:
            messagebox.showerror("Terrain Mapper", "Terrain mapper not loaded.")
            return
        result = run_command(agent, ["step"])
        self._terrain_refresh()
        self._set_status(result.get("message", "Terrain step complete."))

    def _build_controls(self, parent):
        mode_frame = ttk.LabelFrame(parent, text="Mode")
        mode_frame.pack(fill="x", pady=(0, 8))

        self.mode_var = tk.StringVar(value=DEFAULT_MODE)
        for mode in MODES:
            ttk.Radiobutton(
                mode_frame,
                text=mode,
                value=mode,
                variable=self.mode_var,
                command=self._change_mode,
            ).pack(anchor="w", padx=8, pady=2)

        entity_frame = ttk.LabelFrame(parent, text="Entity / Construct")
        entity_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(entity_frame, text="Entity").pack(anchor="w", padx=8, pady=(6, 0))
        self.entity_var = tk.StringVar(value="guest")
        entity_row = ttk.Frame(entity_frame)
        entity_row.pack(fill="x", padx=8, pady=4)
        self.entity_entry = ttk.Entry(entity_row, textvariable=self.entity_var)
        self.entity_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(entity_row, text="Use", width=6, command=self._refresh_vault_panel).pack(
            side="right", padx=(6, 0)
        )

        preset_row = ttk.Frame(entity_frame)
        preset_row.pack(fill="x", padx=8, pady=(0, 6))
        for name in PRESET_ENTITIES:
            ttk.Button(
                preset_row,
                text=name,
                command=lambda n=name: self._select_entity(n),
            ).pack(side="left", padx=(0, 4))

        ttk.Label(entity_frame, text="Construct").pack(anchor="w", padx=8)
        self.construct_var = tk.StringVar(value=self.constructs[0] if self.constructs else "PetAI_Core")
        ttk.Combobox(
            entity_frame,
            textvariable=self.construct_var,
            values=self.constructs,
            state="readonly",
        ).pack(fill="x", padx=8, pady=(2, 8))

        vault_frame = ttk.LabelFrame(parent, text="Vault Access")
        vault_frame.pack(fill="both", expand=True, pady=(0, 8))

        self.vault_info = tk.Text(
            vault_frame,
            height=8,
            wrap="word",
            bg="#1a1f2e",
            fg="#c0c8d8",
            font=("Menlo", 10),
        )
        self.vault_info.pack(fill="both", expand=True, padx=8, pady=8)

        grant_row = ttk.Frame(vault_frame)
        grant_row.pack(fill="x", padx=8, pady=(0, 4))
        self.category_var = tk.StringVar(value=self.categories[0])
        ttk.Combobox(
            grant_row,
            textvariable=self.category_var,
            values=self.categories,
            state="readonly",
            width=16,
        ).pack(side="left", fill="x", expand=True)
        ttk.Button(grant_row, text="Grant", command=self._grant_category).pack(
            side="right", padx=(6, 0)
        )

        action_row = ttk.Frame(vault_frame)
        action_row.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(action_row, text="Check Access", command=self._check_access).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(action_row, text="Revoke All", command=self._revoke_all).pack(
            side="right", padx=(6, 0)
        )

    def _select_entity(self, name):
        self.entity_var.set(name)
        self._refresh_vault_panel()

    def _change_mode(self):
        mode = self.mode_var.get()
        self.rt.set_mode(mode)
        self._set_status(f"Mode set to {mode}")

    def _append_output(self, text):
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def _entity(self):
        return self.entity_var.get().strip() or "guest"

    def _construct(self):
        return self.construct_var.get()

    def _refresh_vault_panel(self):
        entity = self._entity()
        granted = sorted(self.rt.vault.get_granted(entity))
        construct = self._construct()
        required = sorted(self.rt.vault.get_required(construct))

        lines = [
            f"Entity: {entity}",
            f"Granted: {', '.join(granted) if granted else '(none)'}",
            f"Construct: {construct}",
            f"Required: {', '.join(required) if required else '(none)'}",
        ]

        if entity == self.rt.operator:
            lines.append("Operator bypass: active")
        elif required and granted:
            allowed = bool(set(required).intersection(granted))
            lines.append(f"Access: {'allowed' if allowed else 'blocked'}")
        else:
            lines.append("Access: blocked")

        self.vault_info.delete("1.0", "end")
        self.vault_info.insert("1.0", "\n".join(lines))

    def _grant_category(self):
        entity = self._entity()
        category = self.category_var.get()
        self.rt.vault.grant_category(entity, category)
        self._refresh_vault_panel()
        self._set_status(f"Granted '{category}' to '{entity}'")

    def _revoke_all(self):
        entity = self._entity()
        self.rt.vault.entity_categories.pop(entity, None)
        self._refresh_vault_panel()
        self._set_status(f"Revoked all categories from '{entity}'")

    def _check_access(self):
        entity = self._entity()
        construct = self._construct()
        try:
            self.rt.vault.check_access(entity, construct)
            messagebox.showinfo("Vault Access", f"Access granted for '{entity}' → {construct}")
            self._set_status(f"Access OK: {entity} → {construct}")
        except (OmniLockTriggered, VaultCategoryError) as exc:
            messagebox.showerror("Vault Access", str(exc))
            self._set_status(str(exc))
        finally:
            self._refresh_vault_panel()

    def _send_prompt(self):
        text = self.prompt.get().strip()
        if not text:
            return

        entity = self._entity()
        construct = self._construct()
        self._append_output(f"> [{entity}] {text}")
        self.prompt.delete(0, "end")

        try:
            out = handle_prompt(
                self.rt,
                text,
                entity=entity,
                construct=construct,
            )
            self._append_output(out)
            if out.startswith("[OMNI-LOCK]") or out.startswith("[ERROR]"):
                self._set_status(out)
            else:
                self._set_status(f"Handled prompt as {entity}")
        finally:
            self.mode_var.set(self.rt.modes.active.name)
            self._refresh_vault_panel()

    def _set_status(self, text):
        self.status.configure(text=text)

    def run(self):
        self._append_output(
            "SlanguageOS GUI ready.\n"
            "Try entity 'guest' without grants to see OMNI-LOCK, "
            "then grant a category and send again."
        )
        self.root.mainloop()


def launch_gui():
    SlanguageGUI().run()


if __name__ == "__main__":
    launch_gui()
