import os
import sys
import questionary
import typer
from mkdocs_setup.constants import DEFAULT_PARADIGM
from mkdocs_setup.utils import is_project_initialized, get_python_modules
from mkdocs_setup.ai import get_api_key, save_api_key
from mkdocs_setup.core import init_project, generate_api_doc_files, update_mkdocs_nav
from mkdocs_setup.ai_logic import generate_ai_docs

def run_wizard():
    """
    Launches an interactive wizard to guide the user through setting up or updating documentation.
    """
    # 1. Ask for directory path if not initialized in current folder
    if not is_project_initialized():
        typer.secho("\n✨ Welcome to your Documentation Assistant! ✨\n", fg=typer.colors.CYAN, bold=True)
        project_path = questionary.path(
            "Where is your project located? (Leave empty for current folder)",
            default="."
        ).ask()
        
        if project_path and project_path != ".":
            try:
                os.chdir(project_path)
                typer.echo(f"📂 Switched to: {os.getcwd()}")
            except Exception as e:
                typer.secho(f"❌ Could not change directory to '{project_path}': {e}", fg=typer.colors.RED)

    while True:
        initialized = is_project_initialized()
        
        if not initialized:
            choices = [
                "Setup my project (Start here!)",
                "Exit"
            ]
        else:
            choices = [
                "New Project (Start fresh)",
                "Sync Code (Update reference guide)",
                "Write automatic documentation with AI",
                "Exit"
            ]
        
        choice = questionary.select(
            "What would you like to do?",
            choices=choices
        ).ask()

        if choice is None or choice == "Exit":
            typer.echo("See you later!")
            break

        if choice in ["Setup my project (Start here!)", "New Project (Start fresh)"]:
            if initialized:
                # Ask if they want to override
                confirm = questionary.select(
                    "It looks like you already have a documentation setup here. Do you want to overwrite it?",
                    choices=["Yes", "No"],
                    default="No"
                ).ask()
                if confirm != "Yes":
                    continue

            step = "name"
            project_name = ""
            paradigms = []
            extra_list = None
            
            p_choice_val = None
            last_step = None
            
            while step not in ["finish", "cancel"]:
                last_step = step
                
                if step == "name":
                    project_name = questionary.text("What is the name of your project? (Type 'back' to return)").ask()
                    if not project_name or project_name.lower() == 'back':
                        step = "cancel"
                    else:
                        step = "paradigms"
                
                elif step == "paradigms":
                    # Use a select-to-toggle approach to make "<- Back" an immediate action
                    choices = [questionary.Choice("<- Back", value="BACK")]
                    choices.append(questionary.Choice("---", disabled="---"))
                    
                    default_choice = choices[0]
                    for p in DEFAULT_PARADIGM.keys():
                        status = "[x]" if p in paradigms else "[ ]"
                        label = f"{status} {p}"
                        choice_obj = questionary.Choice(label, value=p)
                        choices.append(choice_obj)
                        if p_choice_val == p:
                            default_choice = choice_obj
                        
                    choices.append(questionary.Choice("---", disabled="---"))
                    done_choice = questionary.Choice("✅ Done (Next step)", value="DONE")
                    choices.append(done_choice)
                    if p_choice_val == "DONE":
                        default_choice = done_choice
                    
                    p_choice_val = questionary.select(
                        "Which sections would you like to include?",
                        choices=choices,
                        default=default_choice,
                        instruction="(Use arrows to move, Enter to toggle or confirm)"
                    ).ask()
                    
                    if p_choice_val == "BACK" or p_choice_val is None:
                        step = "name"
                    elif p_choice_val == "DONE":
                        step = "extra"
                    else:
                        # Toggle the selection
                        if p_choice_val in paradigms:
                            paradigms.remove(p_choice_val)
                        else:
                            paradigms.append(p_choice_val)
                        # stays in step="paradigms" to allow more selections
                
                elif step == "extra":
                    extra = questionary.text("Any other sections you'd like to add? (comma separated, leave empty if none, type 'back' to go back)").ask()
                    if extra is not None and extra.lower() == 'back':
                        step = "paradigms"
                    else:
                        extra_list = [e.strip() for e in extra.split(",")] if extra else None
                        step = "finish"
            
            if step == "finish":
                try:
                    typer.echo(f"✨ **Welcome!** Building your documentation project for '{project_name}'...")
                    init_project(project_name=project_name, include_paradigms=paradigms, extra_paradigms=extra_list, overwrite_config=True if initialized else False)
                    typer.secho(f"\n✅ All set! Your project '{project_name}' is ready.", fg=typer.colors.GREEN, bold=True)
                except Exception as e:
                    typer.secho(f"\n❌ Oops, setup failed. Please check if you have permission to write to this folder.\nDetails: {e}", fg=typer.colors.RED, bold=True)

        elif choice == "Sync Code (Update reference guide)":
            try:
                modules = get_python_modules()
                if not modules:
                    typer.echo("\n⚠️ **WARNING**: No Python modules found (excluding __init__.py). Nothing to document.")
                else:
                    api_nav_entries = generate_api_doc_files(modules)
                    update_mkdocs_nav(api_nav_entries)
                    typer.secho("\n✅ Reference guide synced successfully!", fg=typer.colors.GREEN, bold=True)
            except Exception as e:
                if isinstance(e, FileNotFoundError):
                    typer.secho("\n❌ Oops, I couldn't find your project files. Please run the setup first.", fg=typer.colors.RED, bold=True)
                else:
                    typer.secho(f"\n❌ Sync failed. Please make sure your 'docs' folder exists.\nDetails: {e}", fg=typer.colors.RED, bold=True)

        elif choice == "Write automatic documentation with AI":
            # Check provider status
            providers = ["openai", "google", "deepseek", "mistral"]
                
            step = "provider"
            provider = ""
            actions = []
            action_choices = {
                "Write code descriptions": "docstrings",
                "Write a professional README.md": "readme",
                "Generate structured docs for all sections": "modules"
            }
            
            action_choice_val = None
            last_step = None
            
            while step not in ["finish", "cancel"]:
                last_step = step
                
                if step == "provider":
                    provider = questionary.select(
                        "Which AI assistant would you like to use?",
                        choices=["<- Back"] + providers
                    ).ask()
                    if provider == "<- Back" or provider is None:
                        step = "cancel"
                    else:
                        # Check if key exists for chosen provider
                        key = get_api_key(provider)
                        if not key:
                            prompt_key = questionary.password(f"Please enter your {provider.title()} API key:").ask()
                            if not prompt_key:
                                typer.secho(f"❌ Key required for {provider.title()}.", fg=typer.colors.RED)
                                # Stay in 'provider' step
                                continue
                            else:
                                save_api_key(provider, prompt_key)
                                typer.secho(f"✅ Key saved for {provider.title()}.", fg=typer.colors.GREEN)
                        step = "actions"
                
                elif step == "actions":
                    # Use a select-to-toggle approach to make "<- Back" an immediate action
                    choices = [questionary.Choice("<- Back", value="BACK")]
                    choices.append(questionary.Choice("---", disabled="---"))
                    
                    default_choice = choices[0]
                    for txt, val in action_choices.items():
                        is_selected = val in actions
                        status = "[x]" if is_selected else "[ ]"
                        label = f"{status} {txt}"
                        choice_obj = questionary.Choice(label, value=txt)
                        choices.append(choice_obj)
                        if action_choice_val == txt:
                            default_choice = choice_obj
                    
                    choices.append(questionary.Choice("---", disabled="---"))
                    confirm_choice = questionary.Choice("✅ Confirm and Run Assistant", value="CONFIRM")
                    choices.append(confirm_choice)
                    if action_choice_val == "CONFIRM":
                        default_choice = confirm_choice

                    action_choice_val = questionary.select(
                        "What should the AI Assistant do?",
                        choices=choices,
                        default=default_choice,
                        instruction="(Use arrows to move, Enter to toggle or confirm)"
                    ).ask()
                    
                    if action_choice_val == "BACK" or action_choice_val is None:
                        step = "provider"
                    elif action_choice_val == "CONFIRM":
                        if not actions:
                            typer.secho("⚠️ Please select at least one task.", fg=typer.colors.YELLOW)
                        else:
                            step = "finish"
                    else:
                        # Toggle the selected action
                        val = action_choices[action_choice_val]
                        if val in actions:
                            actions.remove(val)
                        else:
                            actions.append(val)
                        # stays in step="actions" loop
            
            if step == "finish":
                typer.echo(f"▶️ Starting AI Assistant tasks...")
                try:
                    generate_ai_docs(
                        provider=provider,
                        docstrings="docstrings" in actions,
                        readme="readme" in actions,
                        modules="modules" in actions
                    )
                except Exception as e:
                    typer.secho(f"\n❌ AI work failed. Please check your internet connection or AI keys.\nDetails: {e}", fg=typer.colors.RED, bold=True)

